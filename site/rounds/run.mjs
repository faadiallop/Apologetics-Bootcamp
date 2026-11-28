// A site round: one short training on a private copy of the site, used as a trainee uses it.
//
// The Worker runs here (wrangler dev, with its own empty database), and a real browser opens
// its page, signs in with a fresh invite code, picks a group, and trains. Only the microphone
// and the voice are stood in for: what the trainee "says" comes from a Claude Code agent
// playing him, and what the coach "says" is captured instead of played. A second agent then
// grades the transcript against the round's statements.
//
// Who pays for what:
//   - The site's own replies (coach, router, member) use SITE_TEST_ANTHROPIC_API_KEY, the
//     author's personal key, never the site's. The copy's spending limits are all set to
//     --cap, so the site itself refuses to spend past it.
//   - The trainee and the grader run through Claude Code, on the author's subscription
//     (CLAUDE_CODE_OAUTH_TOKEN in CI, or a signed-in `claude` on his own machine).
//
// Usage, from site/: node rounds/run.mjs [--round rounds/short-round.md] [--cap 1]
//                    [--turns N] [--out round.json] [--headed]

import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { randomBytes } from "node:crypto";
import { chromium } from "playwright";

const SITE = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = parseArgs(process.argv.slice(2));
const ROUND = resolve(SITE, args.round ?? "rounds/short-round.md");
const CAP = Number(args.cap ?? "1");
const OUT = args.out ? resolve(args.out) : null;
const TRAINEE_MODEL = args["trainee-model"] ?? "haiku";
const GRADER_MODEL = args["grader-model"] ?? "opus";
const PORT = Number(args.port ?? 8799);
const BASE = `http://127.0.0.1:${PORT}`;
const TURN_TIMEOUT_MS = 180_000;
// Wrangler is run by Node directly, not through npx or a shell, so that stopping it stops the
// server under it too, on Windows as well, and paths with spaces need no quoting.
const WRANGLER = join(SITE, "node_modules", "wrangler", "bin", "wrangler.js");
const log = (m) => console.error(`[round] ${m}`);

const key = process.env.SITE_TEST_ANTHROPIC_API_KEY;
if (!key) fail("SITE_TEST_ANTHROPIC_API_KEY is not set: the site's replies need the author's personal key.");
if (!(CAP > 0 && CAP <= 5)) fail("--cap must be more than 0 and at most 5 (US dollars).");

const round = readRound(ROUND);
const MAX_TURNS = Number(args.turns ?? round.turns);

const report = { round: ROUND.slice(SITE.length + 1), group: round.group, cap_usd: CAP, checks: [], graded: [], transcript: [] };
const check = (name, pass, detail = "") => { report.checks.push({ name, pass: Boolean(pass), detail }); };

const work = mkdtempSync(join(tmpdir(), "site-round-"));
let server = null, browser = null;
try {
  await run();
} catch (error) {
  check("The round ran to its end", false, String(error?.message ?? error));
} finally {
  await browser?.close().catch(() => {});
  if (server) await stopServer(server);
  try { rmSync(work, { recursive: true, force: true, maxRetries: 10, retryDelay: 500 }); } catch { /* a file still held open; the temp folder is left */ }
}
finish();

async function run() {
  // ---- a private copy of the site, with its own empty database and low limits
  if (await fetch(BASE + "/").catch(() => null)) throw new Error(`Something is already serving ${BASE}; stop it, or pass --port.`);
  const owner = randomBytes(24).toString("hex");
  // Wrangler reads secrets from a .dev.vars beside its config, so the copy gets a config of its
  // own in the temp folder, pointing back at the site's code. The site's own .dev.vars is untouched.
  const config = JSON.parse(readFileSync(join(SITE, "wrangler.jsonc"), "utf8").replace(/^\s*\/\/.*$/gm, ""));
  delete config.$schema;
  delete config.triggers;
  config.main = join(SITE, config.main);
  config.assets = { ...config.assets, directory: join(SITE, config.assets.directory) };
  const configFile = join(work, "wrangler.json");
  writeFileSync(configFile, JSON.stringify(config, null, 2));
  writeFileSync(join(work, ".dev.vars"), `ANTHROPIC_API_KEY=${key}\nOWNER_TOKEN=${owner}\n`);
  const state = join(work, "state");
  log("Setting up the database");
  await sh([WRANGLER, "d1", "execute", "bootcamp-site", "--config", configFile, "--local", "--persist-to", state, "--file=schema.sql"]);
  const cap = CAP.toFixed(2);
  const vars = { USER_DAILY_USD: cap, USER_MONTHLY_USD: cap, SITE_DAILY_USD: cap, SITE_MONTHLY_USD: cap, SITE_TIGHTEN_AT_USD: cap };
  server = startServer([WRANGLER, "dev", "--local", "--ip", "127.0.0.1", "--port", String(PORT), "--persist-to", state,
    "--config", configFile, "--var", ...Object.entries(vars).map(([k, v]) => `${k}:${v}`)]);
  log("Starting the site");
  await waitFor(async () => (await fetch(BASE + "/").catch(() => null))?.ok, 120_000, "the local site to start");

  // ---- the owner invites a trainee, as on /admin
  const invited = await api("POST", "/api/admin/users", owner, { name: "Site round" });
  check("The owner can invite a trainee", invited.ok && invited.body.code, `status ${invited.status}`);
  if (!invited.body.code) return;
  const code = invited.body.code;

  // ---- the browser
  log("Opening the browser");
  browser = await chromium.launch({ headless: !args.headed });
  const context = await browser.newContext({ reducedMotion: "reduce" });
  const page = await context.newPage();
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(e.message));

  // The transcript, from what the page actually sent and got back.
  const turns = [];
  let asked = 0;
  page.on("request", (req) => { if (req.url().endsWith("/api/turn")) asked++; });
  let traineeTurns = 0, done = false, failedTurn = null, waiting = null;
  page.on("response", async (res) => {
    if (!res.url().endsWith("/api/turn")) return;
    const sent = res.request().postDataJSON()?.text ?? "";
    const body = await res.json().catch(() => ({}));
    log(`Turn ${turns.length + 1}: ${res.status()}`);
    turns.push({ status: res.status(), sent, reply: body.reply ?? "", error: body.error ?? "", reason: body.reason ?? "" });
    report.transcript.push({ speaker: "trainee", text: sent });
    if (res.ok()) report.transcript.push({ speaker: "site", text: body.reply ?? "" });
    else { failedTurn = `${res.status()}: ${body.error ?? ""}`; report.transcript.push({ speaker: "site (refused)", text: body.error ?? "" }); }
  });

  // What the coach's voice would have said, so that warnings spoken aloud are seen too.
  const spoken = [];
  await page.exposeFunction("__roundSpoke", (text) => { if (text.trim()) spoken.push(text); });
  // The trainee's next words, asked for each time the page starts listening.
  await page.exposeFunction("__roundNextLine", async () => {
    // The reply he is answering must be in the transcript first.
    await waitFor(async () => turns.length >= asked, 30_000, "the last reply to be read", 100);
    if (failedTurn) return null;
    if (done || traineeTurns >= MAX_TURNS) { done = true; return null; }
    log("The trainee is answering");
    const line = await traineeSays(round.trainee, report.transcript);
    if (!line || /^\[END\]$/.test(line)) { done = true; return null; }
    traineeTurns++;
    return line;
  });
  await page.addInitScript(fakeSpeech());

  await page.goto(BASE + "/");
  await page.locator("#token").fill(code);
  await page.locator("#signin button").click();
  const groups = page.locator("#choose:not(.gone) #groups");
  await groups.waitFor({ timeout: 15_000 }).catch(() => {});
  check("The invite code signs in and the groups are shown", await groups.isVisible());
  if (!(await groups.isVisible())) return;

  log(`Training on ${round.group}`);
  await page.locator(`button[data-group="${round.group}"]`).click();

  // Train until the trainee is done, the site stops the training, or a turn hangs.
  let last = -1, since = Date.now();
  await waitFor(async () => {
    if (done || failedTurn) return true;
    if (!(await page.locator("#choose").getAttribute("class"))?.includes("gone")) return true;   // the site stopped it
    if (turns.length !== last) { last = turns.length; since = Date.now(); }
    if (Date.now() - since > TURN_TIMEOUT_MS) throw new Error(`No turn finished within ${TURN_TIMEOUT_MS / 1000} seconds.`);
    return false;
  }, 60 * 60_000, "the training to end", 500);

  const stoppedBySite = !(await page.locator("#choose").getAttribute("class"))?.includes("gone") && !done;
  const why = stoppedBySite ? (await page.locator("#why-title").textContent().catch(() => "")) : "";
  if (done && !failedTurn) {
    await page.locator("#end").click().catch(() => {});
  }
  await page.locator("#choose:not(.gone)").waitFor({ timeout: 15_000 }).catch(() => {});
  const endedTitle = (await page.locator("#why-title").textContent().catch(() => "")) ?? "";

  // ---- what can be checked without a model
  check("Every turn was answered", !failedTurn && turns.length > 0 && turns.every((t) => t.status === 200 && t.reply.trim()),
    failedTurn ?? (stoppedBySite ? `The site stopped the training: ${why}` : `${turns.length} turns`));
  check("The trainee could finish the round", done && !stoppedBySite,
    stoppedBySite ? `Stopped by the site: ${why}` : `${traineeTurns} trainee turns of at most ${MAX_TURNS}`);
  check("Ending the training shows the right reason", !done || endedTitle.includes("You ended the training"), endedTitle);
  const plain = (t) => t.replace(/[*_#`>\[\]]/g, "").replace(/\s+/g, " ").trim();
  const heard = plain(spoken.join(" "));
  check("Every reply was spoken", turns.filter((t) => t.reply.trim()).every((t) => heard.includes(plain(t.reply).slice(0, 40))),
    `${spoken.length} pieces spoken`);
  check("The page threw no errors", pageErrors.length === 0, pageErrors.join(" | "));

  const status = await api("GET", "/api/status", code);
  const cost = status.body?.spent_usd?.you_today ?? 0;
  report.cost_usd = cost;
  check("The site recorded what the round cost", status.ok && cost > 0, `$${cost.toFixed(2)}`);
  check("The round stayed within its cap", cost <= CAP, `$${cost.toFixed(2)} of $${CAP.toFixed(2)}`);

  const users = await api("GET", "/api/admin/users", owner);
  const me = users.body?.users?.find?.((u) => u.name === "Site round");
  const sessions = me ? await api("GET", `/api/admin/sessions?user=${encodeURIComponent(me.id)}`, owner) : null;
  const saved = sessions?.body?.sessions?.[0];
  const answered = turns.filter((t) => t.status === 200).length;
  check("The owner's page shows the session with every turn", saved && saved.turns === answered,
    saved ? `${saved.turns} turns saved, ${answered} answered` : "no session found");

  // ---- what the grader judges
  log("Grading");
  if (report.transcript.some((l) => l.speaker === "site")) report.graded = await grade(round.statements, report.transcript);
}

// ------------------------------------------------------------------ the two agents

async function traineeSays(instructions, transcript) {
  const said = transcript.map((l) => `${l.speaker === "trainee" ? "You" : "Coach"}: ${l.text}`).join("\n\n");
  const prompt = `${said ? "The conversation so far:\n\n" + said + "\n\n" : ""}Reply with exactly the words you say aloud next, and nothing else.`;
  const out = await claude(prompt, { model: TRAINEE_MODEL, system: instructions });
  // The page's opening line is sent for him, so his first turn comes after the coach's first reply.
  return out.trim().replace(/^(You|Sam):\s*/i, "").replace(/^"|"$/g, "").trim();
}

async function grade(statements, transcript) {
  const said = transcript.map((l) => `${l.speaker === "trainee" ? "TRAINEE" : "SITE"}: ${l.text}`).join("\n\n");
  const prompt = `You grade one training session on a voice website that coaches Christians in apologetics. Judge only the transcript; the trainee's lines were played by a test agent.

For each statement, decide whether the transcript shows it is true. Be strict, and quote the words that decide it.

Statements:
${statements.map((s, i) => `${i + 1}. ${s}`).join("\n")}

Transcript:

${said}`;
  const schema = {
    type: "object",
    properties: { results: { type: "array", items: { type: "object", properties: {
      statement: { type: "integer" }, pass: { type: "boolean" }, why: { type: "string" } }, required: ["statement", "pass", "why"] } } },
    required: ["results"],
  };
  const out = await claude(prompt, { model: GRADER_MODEL, schema });
  let results;
  try {
    const parsed = JSON.parse(out);
    results = (parsed.structured_output ?? parsed).results;
    if (!Array.isArray(results)) throw new Error(parsed.result ?? "no results");
  } catch {
    return [{ statement: statements.join(" / "), pass: false, why: "The grader's answer could not be read: " + out.slice(0, 300) }];
  }
  return statements.map((s, i) => {
    const r = results.find((x) => x.statement === i + 1);
    return { statement: s, pass: Boolean(r?.pass), why: r?.why ?? "Not graded." };
  });
}

function claude(prompt, { model, system, schema }) {
  // An empty argument is lost through the Windows shell, so it is quoted there.
  const none = process.platform === "win32" ? '""' : "";
  const a = ["-p", "--model", model, "--tools", none, "--no-session-persistence", "--strict-mcp-config"];
  if (system) a.push("--system-prompt", system);
  if (schema) a.push("--output-format", "json", "--json-schema", JSON.stringify(schema));
  return new Promise((ok, no) => {
    const p = spawn("claude", a, { shell: process.platform === "win32", env: { ...process.env, SITE_TEST_ANTHROPIC_API_KEY: "" } });
    let out = "", err = "";
    p.stdout.on("data", (d) => (out += d));
    p.stderr.on("data", (d) => (err += d));
    p.on("error", no);
    p.on("close", (c) => (c === 0 ? ok(out) : no(new Error(`claude exited ${c}: ${err.slice(0, 400)}`))));
    p.stdin.end(prompt);
  });
}

// ------------------------------------------------------------------ the stand-ins

// The page listens through SpeechRecognition and speaks through speechSynthesis. These stand-ins
// hand it the trainee's words and record what it says, and otherwise behave as a browser does.
function fakeSpeech() { return `
(() => {
  class FakeRecognition {
    start() {
      this.live = true;
      window.__roundNextLine().then((line) => {
        if (!this.live) return;
        if (line === null) return;                       // he has finished: the test presses End
        this.live = false;
        this.onresult && this.onresult({ results: [[{ transcript: line }]] });
        this.onend && this.onend();
      });
    }
    // As in a browser, the end of an aborted listen is reported a moment later.
    abort() { if (!this.live) return; this.live = false; setTimeout(() => { this.onerror && this.onerror({ error: "aborted" }); this.onend && this.onend(); }, 0); }
    stop() { this.abort(); }
  }
  window.SpeechRecognition = FakeRecognition;
  window.webkitSpeechRecognition = FakeRecognition;
  if (!window.SpeechSynthesisUtterance) window.SpeechSynthesisUtterance = class { constructor(t) { this.text = t; } };
  const synth = {
    speak(u) { setTimeout(() => { u.onstart && u.onstart(); window.__roundSpoke(u.text || ""); u.onend && u.onend(); }, 0); },
    cancel() {}, pause() {}, resume() {},
    getVoices() { return []; },
    speaking: false, pending: false,
  };
  Object.defineProperty(window, "speechSynthesis", { value: synth, configurable: true });
})();
`; }

// ------------------------------------------------------------------ helpers

function readRound(file) {
  const text = readFileSync(file, "utf8");
  const group = text.match(/\*\*Group:\*\*\s*`([^`]+)`/)?.[1];
  const turns = Number(text.match(/\*\*Most trainee turns:\*\*\s*(\d+)/)?.[1] ?? 8);
  const section = (title) => text.split(/^## /m).find((s) => s.startsWith(title)) ?? "";
  const trainee = section("The simulated trainee").split("\n").filter((l) => l.startsWith(">")).map((l) => l.replace(/^>\s?/, "")).join("\n").trim();
  const statements = section("What the grader checks").split("\n").filter((l) => /^\d+\.\s/.test(l)).map((l) => l.replace(/^\d+\.\s+/, ""));
  if (!group || !trainee || !statements.length) fail(`${file} needs a Group, a simulated trainee and the grader's statements.`);
  return { group, turns, trainee, statements };
}

async function api(method, path, token, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: { authorization: "Bearer " + token, ...(body ? { "content-type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  }).catch(() => null);
  return { ok: Boolean(res?.ok), status: res?.status ?? 0, body: res ? await res.json().catch(() => ({})) : {} };
}

function startServer(a) {
  const p = spawn(process.execPath, a, { cwd: SITE, stdio: ["ignore", "pipe", "pipe"], detached: process.platform !== "win32" });
  let log = "";
  const keep = (d) => { log = (log + d).slice(-4000); };
  p.stdout.on("data", keep);
  p.stderr.on("data", keep);
  p.log = () => log;
  return p;
}

function stopServer(p) {
  return new Promise((done) => {
    if (p.exitCode !== null) return done();
    p.on("close", () => done());
    setTimeout(done, 10_000);
    try {
      if (process.platform === "win32") spawn("taskkill", ["/pid", String(p.pid), "/T", "/F"], { stdio: "ignore" });
      else process.kill(-p.pid, "SIGTERM");
    } catch { done(); }
  });
}

function sh(a) {
  return new Promise((ok, no) => {
    const p = spawn(process.execPath, a, { cwd: SITE });
    let err = "";
    p.stdout.on("data", () => {});
    p.stderr.on("data", (d) => (err += d));
    p.on("close", (c) => (c === 0 ? ok() : no(new Error(`wrangler ${a.slice(1, 3).join(" ")} failed: ${err.slice(-400)}`))));
  });
}

async function waitFor(test, ms, what, every = 1000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    if (await test()) return;
    await new Promise((r) => setTimeout(r, every));
  }
  throw new Error(`Gave up waiting for ${what}.` + (server?.log ? "\n" + server.log().slice(-1500) : ""));
}

function parseArgs(list) {
  const out = {};
  for (let i = 0; i < list.length; i++) {
    if (!list[i].startsWith("--")) continue;
    const name = list[i].slice(2);
    if (list[i + 1] === undefined || list[i + 1].startsWith("--")) out[name] = true;
    else out[name] = list[++i];
  }
  return out;
}

function fail(message) {
  console.error(message);
  process.exit(2);
}

function finish() {
  const all = [...report.checks, ...report.graded];
  report.pass = all.length > 0 && all.every((c) => c.pass);
  if (OUT) writeFileSync(OUT, JSON.stringify(report, null, 2));
  const mark = (p) => (p ? "✅" : "❌");
  const lines = [
    `## Site round: ${report.round}`,
    "",
    `${report.pass ? "Passed" : "Failed"}. Group \`${report.group}\`, cost $${(report.cost_usd ?? 0).toFixed(2)} of a $${CAP.toFixed(2)} cap.`,
    "",
    "**The site**",
    "",
    ...report.checks.map((c) => `- ${mark(c.pass)} ${c.name}${c.detail ? ` (${c.detail.replace(/\n/g, " ").slice(0, 300)})` : ""}`),
    "",
  ];
  if (report.graded.length) lines.push("**The grader**", "", ...report.graded.map((g) => `- ${mark(g.pass)} ${g.statement}<br>${g.why.replace(/\n/g, " ")}`), "");
  console.log(lines.join("\n"));
  process.exit(report.pass ? 0 : 1);
}
