import { describe, it, expect } from "vitest";
import { BaseCard } from "../shared/base";

class Probe extends BaseCard { render() { return null as any; } }
customElements.define("ytm-probe", Probe);

describe("BaseCard", () => {
  it("setConfig stores config and resolves entity + accent", () => {
    const el = new Probe();
    el.hass = { states: { "media_player.ytmusic_a": { entity_id: "media_player.ytmusic_a", state: "idle", attributes: {} } }, entities: {} } as any;
    el.setConfig({ type: "x" });
    expect(el.entityId).toBe("media_player.ytmusic_a");
    expect(el.accent).toBe("#ff2d55");
  });
  it("applies the configured accent to the host --ytm-accent", async () => {
    const el = new Probe();
    el.hass = { states: { "media_player.ytmusic_a": { entity_id: "media_player.ytmusic_a", state: "idle", attributes: {} } }, entities: {} } as any;
    el.setConfig({ type: "x", entity: "media_player.ytmusic_a", accent: "#0af" });
    document.body.appendChild(el);
    await el.updateComplete;
    expect(el.style.getPropertyValue("--ytm-accent")).toBe("#0af");
    document.body.removeChild(el);
  });
  it("stateObj returns the entity state", () => {
    const el = new Probe();
    const obj = { entity_id: "media_player.ytmusic_a", state: "playing", attributes: {} };
    el.hass = { states: { "media_player.ytmusic_a": obj }, entities: {} } as any;
    el.setConfig({ type: "x", entity: "media_player.ytmusic_a" });
    expect(el.stateObj).toBe(obj);
  });
});
