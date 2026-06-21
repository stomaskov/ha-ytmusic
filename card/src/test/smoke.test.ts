import { describe, it, expect } from "vitest";
import { YTMUSIC_CARD_VERSION } from "../ytmusic-card";

describe("toolchain", () => {
  it("loads the entry module", () => {
    expect(YTMUSIC_CARD_VERSION).toBe("0.1.0");
  });
});
