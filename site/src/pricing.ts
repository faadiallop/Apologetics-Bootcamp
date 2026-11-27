// What a call cost, in micro-dollars, from the token counts the API reports.
// Prices are USD per million tokens (list prices, Nov 2026). Check them against
// https://platform.claude.com/docs/en/about-claude/pricing when a model changes.

export interface Price {
  input: number;
  output: number;
  cacheRead: number;
  cacheWrite: number;
}

export const COACH_MODEL = "claude-sonnet-5-5";
export const SMALL_MODEL = "claude-haiku-5-5";

const PRICES: Record<string, Price> = {
  // Cache writes are 1.25x input for the 5-minute cache.
  "claude-sonnet-5-5": { input: 2, output: 10, cacheRead: 0.1, cacheWrite: 2.5 },
  // Haiku's cache prices are assumed at the usual ratios (0.1x read, 1.25x write).
  "claude-haiku-5-5": { input: 0.1, output: 0.5, cacheRead: 0.01, cacheWrite: 0.125 },
};

// A model this table doesn't know (a fallback model, say) is charged at the dearest
// rate here, so the quotas err on the side of stopping early.
const UNKNOWN: Price = { input: 4, output: 20, cacheRead: 0.2, cacheWrite: 5 };

export interface Usage {
  input_tokens?: number | null;
  output_tokens?: number | null;
  cache_read_input_tokens?: number | null;
  cache_creation_input_tokens?: number | null;
}

export function costMicros(model: string, usage: Usage): number {
  const p = PRICES[model] ?? UNKNOWN;
  // tokens x (USD per million tokens) = micro-dollars
  return Math.ceil(
    (usage.input_tokens ?? 0) * p.input +
      (usage.output_tokens ?? 0) * p.output +
      (usage.cache_read_input_tokens ?? 0) * p.cacheRead +
      (usage.cache_creation_input_tokens ?? 0) * p.cacheWrite,
  );
}
