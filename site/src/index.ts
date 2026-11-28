// The website's server. Every request for a model passes through here, where the
// key is held, the caller is checked, and the budget is checked before anything is spent.

import Anthropic from "@anthropic-ai/sdk";
import { makeModels } from "./anthropic";
import { generateCode, hashCode, same } from "./auth";
import { newSession, takeTurn } from "./engine";
import type { Session } from "./engine";
import { GROUPS } from "./materials";
import { costMicros } from "./pricing";
import type { Usage } from "./pricing";
import { check, daysLeftInMonth, limitsFromEnv, nearing, siteDailyAllowance } from "./quota";
import type { Spend } from "./quota";

export interface Env {
  DB: D1Database;
  ANTHROPIC_API_KEY: string;
  /** The owner's own sign-in. Everyone else signs in with an invite code (see auth.ts). */
  OWNER_TOKEN: string;
  [limit: string]: unknown;
}

const MAX_MESSAGE = 1500;
const OWNER = "owner";

interface User {
  id: string;
  name: string;
  owner: boolean;
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8" } });

/** Who is asking: the owner, an invited trainee whose invite still stands, or no one. */
async function whoIs(request: Request, env: Env): Promise<User | null> {
  const given = (request.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "").trim();
  if (!given || given.length > 200) return null;
  if (same(given, env.OWNER_TOKEN ?? "")) return { id: OWNER, name: "Owner", owner: true };
  const row = await env.DB.prepare("SELECT id, name FROM users WHERE code_hash = ? AND active = 1")
    .bind(await hashCode(given))
    .first<{ id: string; name: string }>();
  return row ? { id: row.id, name: row.name, owner: false } : null;
}

/** Where a request came from, as a short tag that can't be turned back into an address. */
async function placeOf(request: Request, env: Env): Promise<{ country: string; tag: string }> {
  const ip = request.headers.get("cf-connecting-ip") ?? "unknown";
  const tag = (await hashCode(ip + "|" + (env.OWNER_TOKEN ?? ""))).slice(0, 10);
  const country = (request as Request & { cf?: { country?: string } }).cf?.country ?? "";
  return { country, tag };
}

const TRIES = 20;
const TRIES_WINDOW = 10 * 60_000;

/** Write down a refused code. Returns true when this place has guessed too often to be let try again yet. */
async function refused(request: Request, env: Env): Promise<boolean> {
  const { country, tag } = await placeOf(request, env);
  const now = Date.now();
  await env.DB.prepare("INSERT INTO signins (at, user_id, outcome, country, ip_tag) VALUES (?, NULL, 'refused', ?, ?)")
    .bind(now, country, tag)
    .run();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM signins WHERE outcome = 'refused' AND ip_tag = ? AND at > ?")
    .bind(tag, now - TRIES_WINDOW)
    .first<{ n: number }>();
  console.warn(JSON.stringify({ event: "sign-in refused", place: tag, country, recent: recent?.n ?? 0 }));
  return (recent?.n ?? 0) > TRIES;
}

async function signIn(request: Request, env: Env, user: User): Promise<Response> {
  const { country, tag } = await placeOf(request, env);
  await env.DB.prepare("INSERT INTO signins (at, user_id, outcome, country, ip_tag) VALUES (?, ?, ?, ?, ?)")
    .bind(Date.now(), user.id, user.owner ? "owner" : "trainee", country, tag)
    .run();
  console.log(JSON.stringify({ event: "signed in", user: user.id, place: tag, country }));
  return json({ name: user.name, owner: user.owner });
}

async function listSignins(env: Env): Promise<Response> {
  const rows = await env.DB.prepare(
    `SELECT s.at, s.outcome, s.country, s.ip_tag, u.name
     FROM signins s LEFT JOIN users u ON u.id = s.user_id ORDER BY s.at DESC LIMIT 100`,
  ).all<{ at: number; outcome: string; country: string | null; ip_tag: string | null; name: string | null }>();
  return json({
    signins: rows.results.map((r) => ({
      at: r.at,
      who: r.outcome === "refused" ? "Refused" : r.outcome === "owner" ? "Owner (you)" : (r.name ?? "A removed invite"),
      refused: r.outcome === "refused",
      country: r.country ?? "",
      place: r.ip_tag ?? "",
    })),
  });
}

const day = (d: Date) => d.toISOString().slice(0, 10);

async function killed(env: Env): Promise<boolean> {
  const row = await env.DB.prepare("SELECT value FROM settings WHERE key = 'kill'").first<{ value: string }>();
  return row?.value === "1";
}

async function spendSoFar(env: Env, user: string, now: Date, sessionTurns: number): Promise<Spend> {
  const today = day(now);
  const totals = await env.DB.prepare(
    `SELECT
       COALESCE(SUM(CASE WHEN user_id = ?1 AND day = ?2 THEN cost_micros END), 0) AS userDay,
       COALESCE(SUM(CASE WHEN user_id = ?1 THEN cost_micros END), 0) AS userMonth,
       COALESCE(SUM(CASE WHEN day = ?2 THEN cost_micros END), 0) AS siteDay,
       COALESCE(SUM(cost_micros), 0) AS siteMonth,
       COALESCE(SUM(CASE WHEN user_id = ?1 AND role != 'router' AND at > ?4 THEN 1 END), 0) AS turnsLastMinute
     FROM usage WHERE day >= ?3`,
  )
    .bind(user, today, today.slice(0, 8) + "01", now.getTime() - 60_000)
    .first<Omit<Spend, "sessionTurns">>();
  return {
    userDay: totals?.userDay ?? 0,
    userMonth: totals?.userMonth ?? 0,
    siteDay: totals?.siteDay ?? 0,
    siteMonth: totals?.siteMonth ?? 0,
    turnsLastMinute: totals?.turnsLastMinute ?? 0,
    sessionTurns,
  };
}

async function newestCard(env: Env, user: string, group: string): Promise<string | null> {
  const row = await env.DB.prepare("SELECT body FROM cards WHERE user_id = ? AND grp = ? ORDER BY saved_at DESC LIMIT 1")
    .bind(user, group)
    .first<{ body: string }>();
  return row?.body ?? null;
}

async function turn(request: Request, env: Env, user: User): Promise<Response> {
  const body = (await request.json().catch(() => null)) as { session_id?: string; group?: string; text?: string } | null;
  const text = (body?.text ?? "").trim();
  if (!text) return json({ error: "Say something first." }, 400);
  if (text.length > MAX_MESSAGE) return json({ error: `Keep a message under ${MAX_MESSAGE} characters.` }, 400);
  if (await killed(env)) return json({ error: "Training is paused for now.", reason: "paused" }, 503);

  const now = new Date();
  let id = body?.session_id;
  let group = body?.group ?? "";
  let session: Session;
  let turns = 0;

  if (id) {
    const row = await env.DB.prepare("SELECT grp, state, turns FROM sessions WHERE id = ? AND user_id = ?")
      .bind(id, user.id)
      .first<{ grp: string; state: string; turns: number }>();
    if (!row) return json({ error: "That session was not found." }, 404);
    if (!row.state) return json({ error: "That session has ended. Start a new one; your card carries your progress over.", reason: "expired" }, 410);
    group = row.grp;
    session = JSON.parse(row.state) as Session;
    turns = row.turns;
  } else {
    if (!GROUPS[group]) return json({ error: "Choose a group first.", groups: Object.keys(GROUPS) }, 400);
    id = crypto.randomUUID();
    session = newSession(await newestCard(env, user.id, group), day(now));
  }

  const limits = limitsFromEnv(env as Record<string, string | undefined>);
  const before = await spendSoFar(env, user.id, now, turns);
  const verdict = check(limits, before, daysLeftInMonth(now));
  if (!verdict.ok) {
    console.warn(JSON.stringify({ event: "limit reached", user: user.id, reason: verdict.reason }));
    return json({ error: verdict.message, reason: verdict.reason, session_id: body?.session_id }, 429);
  }

  const used: { role: string; model: string; usage: Usage; cost: number }[] = [];
  const models = makeModels(env.ANTHROPIC_API_KEY, group, (role, model, usage) =>
    used.push({ role, model, usage, cost: costMicros(model, usage) }),
  );

  let result: Awaited<ReturnType<typeof takeTurn>> | null = null;
  let failure: unknown = null;
  try {
    result = await takeTurn(session, text, models, await newestCard(env, user.id, group));
  } catch (error) {
    failure = error;
  }

  // Whatever was spent is written down, even when the turn failed part-way.
  const spent = used.reduce((sum, u) => sum + u.cost, 0);
  const writes = used.map((u) =>
    env.DB.prepare(
      `INSERT INTO usage (user_id, session_id, day, at, role, model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, cost_micros)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    ).bind(
      user.id, id, day(now), now.getTime(), u.role, u.model,
      u.usage.input_tokens ?? 0, u.usage.output_tokens ?? 0,
      u.usage.cache_read_input_tokens ?? 0, u.usage.cache_creation_input_tokens ?? 0, u.cost,
    ),
  );
  if (result) {
    writes.push(
      env.DB.prepare(
        `INSERT INTO sessions (id, user_id, grp, state, turns, cost_micros, created_at, updated_at) VALUES (?1, ?2, ?3, ?4, 1, ?5, ?6, ?6)
         ON CONFLICT(id) DO UPDATE SET state = ?4, turns = turns + 1, cost_micros = cost_micros + ?5, updated_at = ?6`,
      ).bind(id, user.id, group, JSON.stringify(session), spent, now.getTime()),
    );
    if (result.card) {
      writes.push(
        env.DB.prepare(
          `INSERT INTO cards (session_id, user_id, grp, body, saved_at) VALUES (?1, ?2, ?3, ?4, ?5)
           ON CONFLICT(session_id) DO UPDATE SET body = ?4, saved_at = ?5`,
        ).bind(id, user.id, group, result.card, now.getTime()),
      );
    }
  }
  if (writes.length) await env.DB.batch(writes);

  // The server's log of a turn: who, which session, what it cost and what failed. Never what was said.
  console.log(JSON.stringify({
    event: result ? "turn" : "turn failed",
    user: user.id,
    session: id,
    group,
    route: result?.route?.route ?? (result ? "coach" : undefined),
    calls: used.map((u) => u.role + ":" + u.model),
    cost_usd: spent / 1_000_000,
    error: failure instanceof Error ? failure.name + ": " + failure.message.slice(0, 300) : undefined,
  }));

  if (!result) {
    if (failure instanceof Anthropic.RateLimitError) return json({ error: "The coach is busy. Try again in a moment.", reason: "busy" }, 503);
    if (failure instanceof Anthropic.AuthenticationError) return json({ error: "The site's key was refused." }, 500);
    if (failure instanceof Anthropic.APIError) return json({ error: `The coach could not answer (${failure.status}).` }, 502);
    throw failure;
  }
  return json({
    session_id: id,
    reply: result.reply,
    in_round: session.roundStart !== null,
    route: result.route?.route,
    cost_usd: spent / 1_000_000,
    // Said aloud after the reply, once, when this turn used up most of an allowance.
    warning: nearing(limits, before, {
      ...before,
      userDay: before.userDay + spent,
      userMonth: before.userMonth + spent,
      sessionTurns: before.sessionTurns + 1,
    }),
  });
}

async function status(env: Env, user: User): Promise<Response> {
  const now = new Date();
  const limits = limitsFromEnv(env as Record<string, string | undefined>);
  const spend = await spendSoFar(env, user.id, now, 0);
  const dollars = (micros: number) => Math.round(micros / 10_000) / 100;
  return json({
    name: user.name,
    owner: user.owner,
    paused: await killed(env),
    spent_usd: { you_today: dollars(spend.userDay), you_month: dollars(spend.userMonth), site_today: dollars(spend.siteDay), site_month: dollars(spend.siteMonth) },
    limits_usd: {
      you_today: dollars(limits.userDaily),
      you_month: dollars(limits.userMonthly),
      site_today: dollars(siteDailyAllowance(limits, spend.siteMonth, daysLeftInMonth(now))),
      site_month: dollars(limits.siteMonthly),
    },
    session_turns: limits.sessionTurns,
    keep_conversations_days: keepDays(env),
    groups: Object.fromEntries(Object.entries(GROUPS).map(([id, g]) => [id, g.name])),
  });
}

async function listUsers(env: Env): Promise<Response> {
  const now = new Date();
  const today = day(now);
  const spend = await env.DB.prepare(
    `SELECT user_id,
            COALESCE(SUM(CASE WHEN day = ?1 THEN cost_micros END), 0) AS today,
            COALESCE(SUM(cost_micros), 0) AS month,
            COUNT(DISTINCT session_id) AS sessions,
            MAX(at) AS last_at
     FROM usage WHERE day >= ?2 GROUP BY user_id`,
  )
    .bind(today, today.slice(0, 8) + "01")
    .all<{ user_id: string; today: number; month: number; sessions: number; last_at: number }>();
  const by = new Map(spend.results.map((r) => [r.user_id, r]));
  const users = await env.DB.prepare("SELECT id, name, active, created_at FROM users ORDER BY created_at")
    .all<{ id: string; name: string; active: number; created_at: number }>();
  const dollars = (micros: number) => Math.round(micros / 10_000) / 100;
  const row = (id: string, name: string, active: boolean) => ({
    id,
    name,
    active,
    today_usd: dollars(by.get(id)?.today ?? 0),
    month_usd: dollars(by.get(id)?.month ?? 0),
    sessions_this_month: by.get(id)?.sessions ?? 0,
    last_active: by.get(id)?.last_at ?? null,
  });
  return json({ users: [row(OWNER, "Owner (you)", true), ...users.results.map((u) => row(u.id, u.name, u.active === 1))] });
}

async function invite(request: Request, env: Env): Promise<Response> {
  const body = (await request.json().catch(() => null)) as { name?: string } | null;
  const name = (body?.name ?? "").trim().slice(0, 80);
  if (!name) return json({ error: "Give the person a name, so you can tell the invites apart." }, 400);
  const code = generateCode();
  const id = crypto.randomUUID();
  await env.DB.prepare("INSERT INTO users (id, name, code_hash, active, created_at) VALUES (?, ?, ?, 1, ?)")
    .bind(id, name, await hashCode(code), Date.now())
    .run();
  // The code is returned this once and is not kept; only its hash is.
  return json({ id, name, code });
}

async function setActive(request: Request, env: Env): Promise<Response> {
  const body = (await request.json().catch(() => null)) as { id?: string; active?: boolean } | null;
  if (!body?.id) return json({ error: "Which invite?" }, 400);
  const done = await env.DB.prepare("UPDATE users SET active = ? WHERE id = ?").bind(body.active ? 1 : 0, body.id).run();
  if (!done.meta.changes) return json({ error: "That invite was not found." }, 404);
  return json({ id: body.id, active: Boolean(body.active) });
}

/** One person's sessions, newest first, with the card each one saved. Owner only. */
async function listSessions(env: Env, url: URL): Promise<Response> {
  const user = url.searchParams.get("user") ?? "";
  const rows = await env.DB.prepare(
    `SELECT s.id, s.grp, s.turns, s.cost_micros, s.created_at, s.updated_at, c.body AS card
     FROM sessions s LEFT JOIN cards c ON c.session_id = s.id
     WHERE s.user_id = ? ORDER BY s.updated_at DESC LIMIT 100`,
  )
    .bind(user)
    .all<{ id: string; grp: string; turns: number; cost_micros: number; created_at: number; updated_at: number; card: string | null }>();
  return json({
    sessions: rows.results.map((r) => ({
      id: r.id,
      group: GROUPS[r.grp]?.name ?? r.grp,
      turns: r.turns,
      cost_usd: Math.round(r.cost_micros / 10_000) / 100,
      started: r.created_at,
      last: r.updated_at,
      card: r.card,
    })),
  });
}

/** One session's conversation, line by line. Owner only. */
async function readSession(env: Env, url: URL): Promise<Response> {
  const row = await env.DB.prepare("SELECT state FROM sessions WHERE id = ?")
    .bind(url.searchParams.get("id") ?? "")
    .first<{ state: string }>();
  if (!row) return json({ error: "That session was not found." }, 404);
  if (!row.state) return json({ lines: [], removed: true });
  const state = JSON.parse(row.state) as Session;
  // The site's own notes to the coach are left out: the trainee never said or heard them.
  const lines = state.lines.map((l) => ({ speaker: l.speaker, text: l.text.replace(/\s*\[Site note, not said by the trainee:[\s\S]*\]$/, "") }));
  return json({ lines });
}

const keepDays = (env: Env): number => {
  const days = Number(env.KEEP_CONVERSATIONS_DAYS);
  return Number.isFinite(days) && days > 0 ? days : 14;
};

/**
 * Remove what was said in sessions that have been idle longer than the keeping time.
 * The session's row stays, with its group, turns and cost, and so does its card.
 */
async function removeOldConversations(env: Env, now: number): Promise<number> {
  const done = await env.DB.prepare("UPDATE sessions SET state = '' WHERE state != '' AND updated_at < ?")
    .bind(now - keepDays(env) * 86_400_000)
    .run();
  return done.meta.changes ?? 0;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(request.url);
    if (!pathname.startsWith("/api/")) return new Response("Not found", { status: 404 });
    const user = await whoIs(request, env);
    if (!user) {
      // A request with no code at all is not a guess, so only a refused code is written down.
      if (request.headers.get("authorization") && (await refused(request, env)))
        return json({ error: "Too many wrong codes from here. Wait ten minutes and try again." }, 429);
      return json({ error: "Sign in first." }, 401);
    }

    if (pathname === "/api/signin" && request.method === "POST") return signIn(request, env, user);

    if (pathname === "/api/turn" && request.method === "POST") return turn(request, env, user);
    if (pathname === "/api/status" && request.method === "GET") return status(env, user);

    if (pathname.startsWith("/api/admin/")) {
      if (!user.owner) return json({ error: "Only the owner can do that." }, 403);
      if (pathname === "/api/admin/users" && request.method === "GET") return listUsers(env);
      if (pathname === "/api/admin/users" && request.method === "POST") return invite(request, env);
      if (pathname === "/api/admin/users/active" && request.method === "POST") return setActive(request, env);
      if (pathname === "/api/admin/signins" && request.method === "GET") return listSignins(env);
      if (pathname === "/api/admin/sessions" && request.method === "GET") return listSessions(env, new URL(request.url));
      if (pathname === "/api/admin/session" && request.method === "GET") return readSession(env, new URL(request.url));
      if (pathname === "/api/admin/pause" && request.method === "POST") {
        const body = (await request.json().catch(() => null)) as { paused?: boolean } | null;
        await env.DB.prepare("INSERT INTO settings (key, value) VALUES ('kill', ?1) ON CONFLICT(key) DO UPDATE SET value = ?1")
          .bind(body?.paused ? "1" : "0")
          .run();
        return json({ paused: Boolean(body?.paused) });
      }
    }
    return json({ error: "Not found." }, 404);
  },

  async scheduled(_controller: ScheduledController, env: Env): Promise<void> {
    const removed = await removeOldConversations(env, Date.now());
    console.log(JSON.stringify({ event: "old conversations removed", sessions: removed, kept_days: keepDays(env) }));
  },
} satisfies ExportedHandler<Env>;
