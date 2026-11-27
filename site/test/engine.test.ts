import { describe, expect, it } from "vitest";
import { newSession, takeTurn } from "../src/engine";
import type { CoachReply, Models } from "../src/engine";
import { costMicros } from "../src/pricing";
import { coachMessages, parseRoute } from "../src/round";
import type { ChatMessage, Route } from "../src/round";

function fake(script: { coach?: CoachReply[]; router?: string[]; member?: string[] }) {
  const calls: { who: string; messages?: ChatMessage[]; route?: Route; round?: string }[] = [];
  const next = <T>(list: T[] | undefined, who: string): T => {
    const value = list?.shift();
    if (value === undefined) throw new Error(`unexpected call to the ${who}`);
    return value;
  };
  const models: Models = {
    async coach(messages) {
      calls.push({ who: "coach", messages: JSON.parse(JSON.stringify(messages)) });
      return next(script.coach, "coach");
    },
    async router(round) {
      calls.push({ who: "router", round });
      return next(script.router, "router");
    },
    async member(round, route) {
      calls.push({ who: "member", round, route });
      return next(script.member, "member");
    },
  };
  return { models, calls };
}

describe("parseRoute", () => {
  it("reads the router's line", () =>
    expect(parseRoute('{"route": "close", "kind": "crossed-early", "note": "x"}')).toMatchObject({
      route: "close",
      kind: "crossed-early",
    }));
  it("reads it out of surrounding text", () =>
    expect(parseRoute('Here:\n{"route":"hint","asked":true}').asked).toBe(true));
  it("stays with the member when the answer can't be read", () => {
    expect(parseRoute("no idea").route).toBe("member");
    expect(parseRoute('{"route":"dance"}').route).toBe("member");
  });
});

describe("a session", () => {
  it("opens with the coach, who is given the card", async () => {
    const session = newSession("Next: step 2.", "2026-11-27");
    const { models, calls } = fake({ coach: [{ text: "Welcome back." }] });
    const result = await takeTurn(session, "Train me to talk with Muslims.", models, null);
    expect(result.reply).toBe("Welcome back.");
    expect(calls.map((c) => c.who)).toEqual(["coach"]);
    expect(calls[0].messages![0].content).toContain("Next: step 2.");
    expect(calls[0].messages![0].content).toContain("Train me to talk with Muslims.");
    expect(session.roundStart).toBeNull();
  });

  it("hands a round to the member when the coach starts one", async () => {
    const session = newSession(null, "2026-11-27");
    const { models, calls } = fake({
      coach: [{ text: "", startRound: "You're at Hamza's stall. About five turns." }],
      member: ["The Bible was changed."],
    });
    const result = await takeTurn(session, "Ready.", models, null);
    expect(result.reply).toBe("You're at Hamza's stall. About five turns.\n\nThe Bible was changed.");
    expect(calls.map((c) => c.who)).toEqual(["coach", "member"]);
    expect(session.roundStart).toBe(1);
  });

  async function inRound() {
    const session = newSession(null, "2026-11-27");
    const { models } = fake({ coach: [{ text: "", startRound: "Setup." }], member: ["The Bible was changed."] });
    await takeTurn(session, "Ready.", models, null);
    return session;
  }

  it("lets the member answer an ordinary turn, with no call to the coach", async () => {
    const session = await inRound();
    const { models, calls } = fake({ router: ['{"route":"member"}'], member: ["Everyone knows that."] });
    const result = await takeTurn(session, "How do you know it was changed?", models, null);
    expect(result.reply).toBe("Everyone knows that.");
    expect(calls.map((c) => c.who)).toEqual(["router", "member"]);
    expect(calls[0].round).toContain("**Trainee:** How do you know it was changed?");
    expect(calls[0].round).not.toContain("Ready.");
    expect(session.roundStart).toBe(1);
  });

  it("brings the coach back for a hint and keeps the round going", async () => {
    const session = await inRound();
    const { models, calls } = fake({
      router: ['{"route":"hint","note":"He argued the claim."}'],
      coach: [{ text: "Time out. Ask for his reasons. Back to Hamza." }],
    });
    const result = await takeTurn(session, "No it wasn't.", models, null);
    expect(result.reply).toBe("Time out. Ask for his reasons. Back to Hamza.");
    expect(calls.map((c) => c.who)).toEqual(["router", "coach"]);
    expect(calls[1].messages!.at(-1)!.content).toContain("a hint is due now");
    expect(session.roundStart).toBe(1);
  });

  it("closes a round with the member's last line, then the coach, and keeps the card", async () => {
    const session = await inRound();
    const { models, calls } = fake({
      router: ['{"route":"close","kind":"closing-turns-done"}'],
      member: ["Goodbye, then."],
      coach: [{ text: "Coach here. Two of three. Not a pass yet.", card: "Boot camp log" }],
    });
    const result = await takeTurn(session, "Thanks for your time.", models, null);
    expect(result.reply).toBe("Goodbye, then.\n\nCoach here. Two of three. Not a pass yet.");
    expect(result.card).toBe("Boot camp log");
    expect(calls.map((c) => c.who)).toEqual(["router", "member", "coach"]);
    expect(calls[2].messages!.at(-1)!.role).toBe("user");
    expect(calls[2].messages!.at(-1)!.content).toContain('"Goodbye, then."');
    expect(session.roundStart).toBeNull();
    // What is kept alternates between the two sides, as the API requires.
    expect(coachMessages(session).map((m) => m.role)).toEqual(["user", "assistant", "user", "assistant"]);
  });
});

describe("costMicros", () => {
  it("prices a cached coach turn", () =>
    expect(
      costMicros("claude-sonnet-5-5", { input_tokens: 500, output_tokens: 300, cache_read_input_tokens: 45000 }),
    ).toBe(500 * 2 + 300 * 10 + 4500));
  it("prices a member turn on the small model", () =>
    expect(costMicros("claude-haiku-5-5", { input_tokens: 20000, output_tokens: 100 })).toBe(2000 + 50));
  it("charges an unknown model at the dearest rate", () =>
    expect(costMicros("something-else", { input_tokens: 1000, output_tokens: 0 })).toBe(4000));
});
