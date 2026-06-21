import { describe, it, expect } from "vitest";
import { resolveAccent } from "../shared/accent";

describe("resolveAccent", () => {
  it("default when unset", () => expect(resolveAccent({ type: "x" })).toBe("#ff2d55"));
  it("uses config.accent", () => expect(resolveAccent({ type: "x", accent: "#0af" })).toBe("#0af"));
});
