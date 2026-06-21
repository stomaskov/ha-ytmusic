import { describe, it, expect } from "vitest";
import { currentPosition } from "../shared/position";

const base = { entity_id: "media_player.ytmusic_x", state: "playing", attributes: {} as any };

describe("currentPosition", () => {
  it("interpolates while playing", () => {
    const updated = new Date("2026-06-21T00:00:00Z").getTime();
    const obj = { ...base, attributes: { media_position: 10, media_duration: 200, media_position_updated_at: new Date(updated).toISOString() } };
    expect(currentPosition(obj, updated + 5000)).toBe(15);
  });
  it("clamps to duration", () => {
    const updated = new Date("2026-06-21T00:00:00Z").getTime();
    const obj = { ...base, attributes: { media_position: 195, media_duration: 200, media_position_updated_at: new Date(updated).toISOString() } };
    expect(currentPosition(obj, updated + 60000)).toBe(200);
  });
  it("does not advance when not playing", () => {
    const updated = new Date("2026-06-21T00:00:00Z").getTime();
    const obj = { ...base, state: "paused", attributes: { media_position: 30, media_position_updated_at: new Date(updated).toISOString() } };
    expect(currentPosition(obj, updated + 5000)).toBe(30);
  });
  it("null when no position", () => {
    expect(currentPosition({ ...base, attributes: {} }, Date.now())).toBeNull();
  });
});
