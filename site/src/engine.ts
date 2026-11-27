// One turn of a session: who speaks, and what the session looks like afterwards.
// The models and the materials are passed in, so this file can be tested without either.

import { coachMessages, parseRoute, roundTranscript } from "./round";
import type { ChatMessage, Route, SessionState } from "./round";

export interface CoachReply {
  text: string;
  /** Set when the coach handed a round to the member: the setup the trainee hears. */
  startRound?: string;
  /** Set when the coach saved the trainee's card. */
  card?: string;
  refused?: boolean;
}

export interface Models {
  coach(messages: ChatMessage[]): Promise<CoachReply>;
  router(roundSoFar: string, card: string | null): Promise<string>;
  member(roundSoFar: string, route: Route): Promise<string>;
}

export interface TurnResult {
  reply: string;
  card?: string;
  route?: Route;
}

export const REFUSED = "I couldn't answer that. Please say it another way.";

const note = (text: string) => `\n\n[Site note, not said by the trainee: ${text}]`;

export function newSession(card: string | null, today: string): SessionState & { header: string } {
  const cardText = card ? `His newest card for this group:\n\n${card}` : "He has no card for this group yet.";
  return {
    lines: [],
    roundStart: null,
    header: `[Site note, not said by the trainee: today is ${today}. He is typing, not speaking. ${cardText}]\n\n`,
  };
}

export type Session = ReturnType<typeof newSession>;

function messagesFor(session: Session): ChatMessage[] {
  const messages = coachMessages(session);
  if (messages[0]?.role === "user") messages[0].content = session.header + messages[0].content;
  return messages;
}

async function coachSpeaks(session: Session, models: Models, card: string | null): Promise<TurnResult> {
  const coach = await models.coach(messagesFor(session));
  if (coach.refused) return { reply: REFUSED };

  const said: string[] = [];
  if (coach.text.trim()) {
    session.lines.push({ speaker: "coach", text: coach.text.trim() });
    said.push(coach.text.trim());
  }
  if (coach.startRound) {
    const setup = coach.startRound.trim();
    session.lines.push({ speaker: "coach", text: setup });
    session.roundStart = session.lines.length - 1;
    const opening = await models.member(roundTranscript(session), {
      route: "member",
      note: "The round has just been set up. Open the conversation as the person the setup names.",
    });
    session.lines.push({ speaker: "member", text: opening.trim() });
    said.push(setup, opening.trim());
  }
  return { reply: said.join("\n\n") || REFUSED, card: coach.card ?? card ?? undefined };
}

export async function takeTurn(
  session: Session,
  text: string,
  models: Models,
  card: string | null,
): Promise<TurnResult> {
  session.lines.push({ speaker: "trainee", text });
  const trainee = session.lines[session.lines.length - 1];

  if (session.roundStart === null) return coachSpeaks(session, models, card);

  const route = parseRoute(await models.router(roundTranscript(session), card));

  if (route.route === "hint") {
    trainee.text += note(
      `a hint is due now${route.asked ? ", because he asked for one" : ""}. ${route.note ?? ""} ` +
        "Give only the hint, as the skill's rules for hints direct, and send him back in. The round goes on.",
    );
    return { ...(await coachSpeaks(session, models, card)), route };
  }

  const line = (await models.member(roundTranscript(session), route)).trim();

  if (route.route === "close") {
    trainee.text += note(
      `the round is over (${route.kind ?? "closed"}). ${route.note ?? ""} The member has already answered him: ` +
        `"${line}". Step out as coach now, coach the round as after any round, and save his card.`,
    );
    session.roundStart = null;
    const coach = await models.coach(messagesFor(session));
    session.lines.push({ speaker: "member", text: line });
    if (coach.refused) return { reply: line, route };
    session.lines.push({ speaker: "coach", text: coach.text.trim() });
    return { reply: `${line}\n\n${coach.text.trim()}`, card: coach.card ?? card ?? undefined, route };
  }

  session.lines.push({ speaker: "member", text: line });
  return { reply: line, route };
}
