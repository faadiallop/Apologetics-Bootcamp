import { describe, expect, it } from "vitest";
import { generateCode, hashCode, normalizeCode, same } from "../src/auth";

describe("invite codes", () => {
  it("look like four groups of four, with no letters that are easily confused", () => {
    for (let i = 0; i < 200; i++) expect(generateCode()).toMatch(/^([A-HJKMNP-Z2-9]{4}-){3}[A-HJKMNP-Z2-9]{4}$/);
  });
  it("do not repeat", () => {
    const made = new Set(Array.from({ length: 500 }, generateCode));
    expect(made.size).toBe(500);
  });
  it("are read the same however they are typed", async () => {
    expect(normalizeCode(" k7mp 2qxr-9tdn-4hvc ")).toBe("K7MP2QXR9TDN4HVC");
    expect(await hashCode("k7mp 2qxr 9tdn 4hvc")).toBe(await hashCode("K7MP-2QXR-9TDN-4HVC"));
  });
  it("hash to 64 hex characters, differently for different codes", async () => {
    const a = await hashCode("K7MP-2QXR-9TDN-4HVC");
    expect(a).toMatch(/^[0-9a-f]{64}$/);
    expect(a).not.toBe(await hashCode("K7MP-2QXR-9TDN-4HVD"));
  });
});

describe("same", () => {
  it("is true only for equal, non-empty strings", () => {
    expect(same("abc", "abc")).toBe(true);
    expect(same("abc", "abd")).toBe(false);
    expect(same("abc", "abcd")).toBe(false);
    expect(same("", "")).toBe(false);
  });
});
