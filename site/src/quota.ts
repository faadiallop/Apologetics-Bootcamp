// Spending limits. All money is in micro-dollars (1 USD = 1_000_000), so sums stay whole numbers.

export interface Limits {
  userDaily: number;
  userMonthly: number;
  siteDaily: number;
  siteMonthly: number;
  /** Once the site has spent this much in the month, the daily budget shrinks to make the rest last. */
  tightenAt: number;
  sessionSpend: number;
  sessionTurns: number;
  turnsPerMinute: number;
}

export interface Spend {
  userDay: number;
  userMonth: number;
  siteDay: number;
  siteMonth: number;
  sessionSpend: number;
  sessionTurns: number;
  turnsLastMinute: number;
}

export type Verdict = { ok: true } | { ok: false; reason: string; message: string };

export const usd = (dollars: number): number => Math.round(dollars * 1_000_000);

export function limitsFromEnv(env: Record<string, string | undefined>): Limits {
  const num = (key: string, fallback: number) => {
    const v = Number(env[key]);
    return Number.isFinite(v) && v >= 0 ? v : fallback;
  };
  return {
    userDaily: usd(num("USER_DAILY_USD", 0.5)),
    userMonthly: usd(num("USER_MONTHLY_USD", 3.5)),
    siteDaily: usd(num("SITE_DAILY_USD", 1.5)),
    siteMonthly: usd(num("SITE_MONTHLY_USD", 20)),
    tightenAt: usd(num("SITE_TIGHTEN_AT_USD", 16)),
    sessionSpend: usd(num("SESSION_USD", 0.6)),
    sessionTurns: num("SESSION_TURNS", 40),
    turnsPerMinute: num("TURNS_PER_MINUTE", 6),
  };
}

/** Days left in the month, today included (UTC). */
export function daysLeftInMonth(now: Date): number {
  const last = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0)).getUTCDate();
  return last - now.getUTCDate() + 1;
}

/** Today's site-wide budget: the usual one, or what is left spread over the days left. */
export function siteDailyAllowance(limits: Limits, siteMonth: number, daysLeft: number): number {
  if (siteMonth < limits.tightenAt) return limits.siteDaily;
  const left = Math.max(0, limits.siteMonthly - siteMonth);
  return Math.min(limits.siteDaily, Math.floor(left / Math.max(1, daysLeft)));
}

export function check(limits: Limits, spend: Spend, daysLeft: number): Verdict {
  const no = (reason: string, message: string): Verdict => ({ ok: false, reason, message });
  if (spend.turnsLastMinute >= limits.turnsPerMinute)
    return no("rate", "You're going faster than the site allows. Wait a minute and try again.");
  if (spend.siteMonth >= limits.siteMonthly)
    return no("site-month", "The site has used its budget for this month. Training opens again next month.");
  if (spend.siteDay >= siteDailyAllowance(limits, spend.siteMonth, daysLeft))
    return no("site-day", "The site has used today's budget. Training opens again tomorrow.");
  if (spend.userMonth >= limits.userMonthly)
    return no("user-month", "You've used your training allowance for this month.");
  if (spend.userDay >= limits.userDaily)
    return no("user-day", "You've used today's training allowance. Come back tomorrow; your card is saved.");
  if (spend.sessionTurns >= limits.sessionTurns || spend.sessionSpend >= limits.sessionSpend)
    return no("session", "This session has reached its limit. Start a new session; your card carries your progress over.");
  return { ok: true };
}
