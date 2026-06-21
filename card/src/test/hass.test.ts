import { describe, it, expect } from "vitest";
import { detectEntity, sourceState } from "../shared/hass";

describe("detectEntity", () => {
  it("uses config.entity when set", () => {
    const hass: any = { states: {}, entities: {} };
    expect(detectEntity(hass, { type: "x", entity: "media_player.ytmusic_a" })).toBe("media_player.ytmusic_a");
  });
  it("finds the single ytmusic media_player via the entity registry", () => {
    const hass: any = {
      states: { "media_player.ytmusic_a": {}, "media_player.sonos": {} },
      entities: {
        "media_player.ytmusic_a": { entity_id: "media_player.ytmusic_a", platform: "ytmusic" },
        "media_player.sonos": { entity_id: "media_player.sonos", platform: "sonos" },
      },
    };
    expect(detectEntity(hass, { type: "x" })).toBe("media_player.ytmusic_a");
  });
  it("falls back to entity_id prefix when registry lacks platform", () => {
    const hass: any = { states: { "media_player.ytmusic_01abc": {} }, entities: {} };
    expect(detectEntity(hass, { type: "x" })).toBe("media_player.ytmusic_01abc");
  });
  it("null when none", () => {
    const hass: any = { states: { "media_player.sonos": {} }, entities: {} };
    expect(detectEntity(hass, { type: "x" })).toBeNull();
  });
});

describe("sourceState", () => {
  it("returns the downstream speaker state", () => {
    const speaker = { entity_id: "media_player.sonos", state: "playing", attributes: {} };
    const hass: any = { states: { "media_player.sonos": speaker } };
    const yt = { entity_id: "media_player.ytmusic_a", state: "playing", attributes: { source: "media_player.sonos" } };
    expect(sourceState(hass, yt)).toBe(speaker);
  });
  it("null when no source", () => {
    const hass: any = { states: {} };
    expect(sourceState(hass, { entity_id: "e", state: "idle", attributes: {} })).toBeNull();
  });
});
