import { describe, expect, it } from "vitest";
import { check, daysLeftInMonth, limitsFromEnv, nearing, siteDailyAllowance, usd } from "../src/quota";
import type { Spend } from "../src/quota";

const limits = limitsFromEnv({});
const none: Spend = { userDay: 0, userMonth: 0, siteDay: 0, siteMonth: 0, sessionSpend: 0, sessionTurns: 0, turnsLastMinute: 0 };
const reason = (spend: Partial<Spend>, daysLeft = 10) => {
  const v = check(limits, { ...none, ...spend }, daysLeft);
  return v.ok ? "ok" : v.reason;
};

describe("limits", () => {
  it("defaults to the $20 plan", () => {
    expect(limits.userDaily).toBe(usd(0.5));
    expect(limits.userMonthly).toBe(usd(3.5));
    expect(limits.siteDaily).toBe(usd(1.5));
    expect(limits.siteMonthly).toBe(usd(20));
    expect(limits.sessionTurns).toBe(40);
  });
  it("reads its numbers from the environment", () => {
    expect(limitsFromEnv({ USER_DAILY_USD: "0.25" }).userDaily).toBe(usd(0.25));
    expect(limitsFromEnv({ USER_DAILY_USD: "nonsense" }).userDaily).toBe(usd(0.5));
  });
});

describe("check", () => {
  it("lets a fresh trainee through", () => expect(reason({})).toBe("ok"));
  it("stops a trainee at his daily allowance", () => expect(reason({ userDay: usd(0.5) })).toBe("user-day"));
  it("stops a trainee at his monthly allowance", () => expect(reason({ userMonth: usd(3.5) })).toBe("user-month"));
  it("stops everyone at the site's daily budget", () => expect(reason({ siteDay: usd(1.5) })).toBe("site-day"));
  it("stops everyone at the site's monthly budget", () => expect(reason({ siteMonth: usd(20) })).toBe("site-month"));
  it("stops a session at its turn limit", () => expect(reason({ sessionTurns: 40 })).toBe("session"));
  it("stops a session at its spending limit", () => expect(reason({ sessionSpend: usd(0.6) })).toBe("session"));
  it("stops a trainee who sends too fast", () => expect(reason({ turnsLastMinute: 6 })).toBe("rate"));
  it("lets him through just under each limit", () =>
    expect(reason({ userDay: usd(0.49), userMonth: usd(3.49), siteDay: usd(1.49), sessionTurns: 39 })).toBe("ok"));
});

describe("the last four dollars", () => {
  it("keeps the usual daily budget below the tightening point", () =>
    expect(siteDailyAllowance(limits, usd(15.99), 10)).toBe(usd(1.5)));
  it("spreads what is left over the days left", () => expect(siteDailyAllowance(limits, usd(16), 10)).toBe(usd(0.4)));
  it("never raises the daily budget", () => expect(siteDailyAllowance(limits, usd(16), 1)).toBe(usd(1.5)));
  it("stops the site when the tightened budget for today is used", () =>
    expect(reason({ siteMonth: usd(16), siteDay: usd(0.4) }, 10)).toBe("site-day"));
});

describe("daysLeftInMonth", () => {
  it("counts today", () => {
    expect(daysLeftInMonth(new Date("2026-11-27T12:00:00Z"))).toBe(4);
    expect(daysLeftInMonth(new Date("2026-11-30T23:59:00Z"))).toBe(1);
    expect(daysLeftInMonth(new Date("2028-02-01T00:00:00Z"))).toBe(29);
  });
});

describe("the heads-up before an allowance runs out", () => {
  const at = (spend: Partial<Spend>): Spend => ({ ...none, ...spend });
  it("says nothing while there is plenty left", () =>
    expect(nearing(limits, at({ userDay: usd(0.1) }), at({ userDay: usd(0.2) }))).toBeNull());
  it("speaks on the turn that passes four fifths of the day", () =>
    expect(nearing(limits, at({ userDay: usd(0.39) }), at({ userDay: usd(0.41) }))).toContain("today"));
  it("does not repeat itself on later turns", () =>
    expect(nearing(limits, at({ userDay: usd(0.41) }), at({ userDay: usd(0.45) }))).toBeNull());
  it("speaks of the month when the month is nearly used", () =>
    expect(nearing(limits, at({ userMonth: usd(2.79) }), at({ userMonth: usd(2.81) }))).toContain("month"));
  it("speaks of the session when its turns or its spending run low", () => {
    expect(nearing(limits, at({ sessionTurns: 31 }), at({ sessionTurns: 32 }))).toContain("session");
    expect(nearing(limits, at({ sessionSpend: usd(0.47) }), at({ sessionSpend: usd(0.49) }))).toContain("session");
  });
});
