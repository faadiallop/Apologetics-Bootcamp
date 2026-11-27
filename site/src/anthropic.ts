// The calls to Claude. The key never leaves the Worker.

import Anthropic from "@anthropic-ai/sdk";
import type { CoachReply, Models } from "./engine";
import { coachSystem, memberSystem, routerSystem } from "./materials";
import { COACH_MODEL, SMALL_MODEL } from "./pricing";
import type { Usage } from "./pricing";
import type { ChatMessage, Route } from "./round";

export type Record = (role: "coach" | "router" | "member", model: string, usage: Usage) => void;

const TOOLS: Anthropic.Tool[] = [
  {
    name: "start_round",
    description:
      "Begin a practice conversation. Another voice plays the member from here; you are called back for a hint or when the round is over.",
    strict: true,
    input_schema: {
      type: "object",
      properties: {
        setup: {
          type: "string",
          description:
            "The two sentences the trainee hears before the round: who he is talking to, the goal, about how many turns, and in a drill the tactic and what counts as a hit.",
        },
      },
      required: ["setup"],
      additionalProperties: false,
    },
  },
  {
    name: "save_card",
    description: "Save the trainee's card for this session to his training log, replacing this session's earlier card.",
    strict: true,
    input_schema: {
      type: "object",
      properties: { card: { type: "string", description: "The whole card, as the skill describes it." } },
      required: ["card"],
      additionalProperties: false,
    },
  },
];

const cached = (text: string) => ({ type: "text" as const, text, cache_control: { type: "ephemeral" as const } });

export function makeModels(apiKey: string, groupId: string, record: Record): Models {
  const client = new Anthropic({ apiKey });

  async function small(role: "router" | "member", system: string, user: string, maxTokens: number): Promise<string> {
    const res = await client.messages.create({
      model: SMALL_MODEL,
      max_tokens: maxTokens,
      output_config: { effort: "low" },
      system: [cached(system)],
      messages: [{ role: "user", content: user }],
    });
    record(role, res.model, res.usage);
    return res.content.map((b) => (b.type === "text" ? b.text : "")).join("").trim();
  }

  return {
    async coach(history: ChatMessage[]): Promise<CoachReply> {
      const [shared, own] = coachSystem(groupId);
      const messages: Anthropic.MessageParam[] = history.map((m) => ({ role: m.role, content: m.content }));
      const reply: CoachReply = { text: "" };
      const said: string[] = [];

      // The coach may call a tool and then go on, so ask until it has finished speaking.
      for (let step = 0; step < 4; step++) {
        // No fallback model is named: a request the coach's model declines is not
        // retried on another, dearer one, so every call costs what pricing.ts expects.
        const res = await client.messages.create({
          model: COACH_MODEL,
          max_tokens: 4000,
          output_config: { effort: "low" },
          system: [cached(shared), cached(own)],
          tools: TOOLS,
          messages,
        });
        record("coach", res.model, res.usage);
        if (res.stop_reason === "refusal") return { text: "", refused: true };

        const results: Anthropic.ToolResultBlockParam[] = [];
        for (const block of res.content) {
          if (block.type === "text") said.push(block.text);
          if (block.type !== "tool_use") continue;
          const input = block.input as { setup?: string; card?: string };
          let content = "Unknown tool.";
          if (block.name === "start_round" && typeof input.setup === "string") {
            reply.startRound = input.setup;
            content = "The round has begun, and the member speaks next. Say nothing more in this turn.";
          } else if (block.name === "save_card" && typeof input.card === "string") {
            reply.card = input.card;
            content = "Saved.";
          }
          results.push({ type: "tool_result", tool_use_id: block.id, content });
        }
        if (res.stop_reason !== "tool_use" || results.length === 0 || reply.startRound) break;
        messages.push({ role: "assistant", content: res.content });
        messages.push({ role: "user", content: results });
      }

      reply.text = said.join("\n\n").trim();
      return reply;
    },

    router(roundSoFar: string, card: string | null): Promise<string> {
      const user = `# The round so far\n\n${roundSoFar}\n\n# The trainee's newest card\n\n${card ?? "He has no card yet."}`;
      return small("router", routerSystem(), user, 1000);
    },

    member(roundSoFar: string, route: Route): Promise<string> {
      const user = `# The round so far\n\n${roundSoFar}\n\n# The route for this turn\n\n${JSON.stringify(route)}`;
      return small("member", memberSystem(groupId), user, 1000);
    },
  };
}
