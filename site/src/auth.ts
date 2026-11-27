// Invite codes. A code is shown once, to the owner, when he invites someone.
// The site keeps only its hash, so the database never holds a code that works.

// No 0, O, 1, I or L, which are easily confused when a code is read out or copied by hand.
const ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";

/** A new code such as "K7MP-2QXR-9TDN-4HVC": 16 characters, about 79 bits. */
export function generateCode(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  // 248 is the largest multiple of 31 below 256, so no letter is likelier than another.
  const chars: string[] = [];
  let i = 0;
  while (chars.length < 16) {
    if (i === bytes.length) {
      crypto.getRandomValues(bytes);
      i = 0;
    }
    const b = bytes[i++];
    if (b < 248) chars.push(ALPHABET[b % ALPHABET.length]);
  }
  return chars.join("").replace(/(.{4})(?=.)/g, "$1-");
}

/** A code as typed: any case, with or without its hyphens or spaces. */
export const normalizeCode = (typed: string): string => typed.toUpperCase().replace(/[^A-Z0-9]/g, "");

export async function hashCode(typed: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(normalizeCode(typed)));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Compare two strings without stopping at the first difference. */
export function same(a: string, b: string): boolean {
  if (!a || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
