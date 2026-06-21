import { describe, it, expect } from "vitest";
import { formatTime, joinArtists } from "../shared/format";

describe("formatTime", () => {
  it("m:ss", () => expect(formatTime(83)).toBe("1:23"));
  it("pads seconds", () => expect(formatTime(5)).toBe("0:05"));
  it("h:mm:ss past an hour", () => expect(formatTime(3725)).toBe("1:02:05"));
  it("null/undefined/negative -> 0:00", () => {
    expect(formatTime(null)).toBe("0:00");
    expect(formatTime(undefined)).toBe("0:00");
    expect(formatTime(-4)).toBe("0:00");
  });
});

describe("joinArtists", () => {
  it("passes a string through", () => expect(joinArtists("Daft Punk")).toBe("Daft Punk"));
  it("joins an array", () => expect(joinArtists(["A", "B"])).toBe("A, B"));
  it("empty -> ''", () => expect(joinArtists(undefined)).toBe(""));
});
