// The shape of a session's conversation, and the router's answer.

export type Speaker = "trainee" | "coach" | "member";

export interface Line {
  speaker: Speaker;
  text: string;
}

export interface SessionState {
  lines: Line[];
  /** Index in `lines` of the coach's setup for the round in progress, or null between rounds. */
  roundStart: number | null;
}

export type RouteName = "member" | "member-leaving" | "member-closing" | "close" | "hint";

export interface Route {
  route: RouteName;
  kind?: string;
  asked?: boolean;
  note?: string;
}

const ROUTES: RouteName[] = ["member", "member-leaving", "member-closing", "close", "hint"];

/**
 * Read the router's one line of JSON. If it can't be read, stay with the member:
 * a hint missed costs the trainee little, and the coach marks it in the debrief.
 */
export function parseRoute(text: string): Route {
  const match = text.match(/\{[\s\S]*\}/);
  if (match) {
    try {
      const parsed = JSON.parse(match[0]) as Record<string, unknown>;
      if (typeof parsed.route === "string" && (ROUTES as string[]).includes(parsed.route)) {
        return {
          route: parsed.route as RouteName,
          kind: typeof parsed.kind === "string" ? parsed.kind : undefined,
          asked: parsed.asked === true,
          note: typeof parsed.note === "string" ? parsed.note : undefined,
        };
      }
    } catch {
      // fall through
    }
  }
  return { route: "member", note: "router answer could not be read" };
}

const LABEL: Record<Speaker, string> = { trainee: "Trainee", coach: "Coach", member: "Member" };

/** The round so far, as the router and the member read it. */
export function roundTranscript(state: SessionState): string {
  const from = state.roundStart ?? 0;
  return state.lines
    .slice(from)
    .map((l) => `**${LABEL[l.speaker]}:** ${l.text}`)
    .join("\n\n");
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

/**
 * The whole session as the coach's model sees it: the trainee is the user, and
 * everything the coach or the member said is the assistant, since from the coach's
 * side the member's lines are its own role-play. Neighbouring lines by one side
 * are joined, because the API wants the two sides to alternate.
 */
export function coachMessages(state: SessionState): ChatMessage[] {
  const out: ChatMessage[] = [];
  for (const line of state.lines) {
    const role = line.speaker === "trainee" ? "user" : "assistant";
    const last = out[out.length - 1];
    if (last && last.role === role) last.content += "\n\n" + line.text;
    else out.push({ role, content: line.text });
  }
  return out;
}
