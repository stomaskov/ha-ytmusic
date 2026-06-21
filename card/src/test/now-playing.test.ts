import { describe, it, expect, vi, beforeEach } from "vitest";
import "../cards/now-playing";

function el(attrs: Record<string, any>, source = "media_player.sonos") {
  const node: any = document.createElement("ytmusic-now-playing");
  const stateObj = { entity_id: "media_player.ytmusic_a", state: attrs.state ?? "playing", attributes: { source, source_list: ["media_player.sonos"], ...attrs } };
  const speaker = { entity_id: "media_player.sonos", state: "playing", attributes: {} };
  node.hass = { states: { "media_player.ytmusic_a": stateObj, "media_player.sonos": speaker }, entities: {}, callService: vi.fn().mockResolvedValue(undefined), callWS: vi.fn().mockResolvedValue({ lines: null, synced: false }) };
  node.setConfig({ type: "custom:ytmusic-now-playing", entity: "media_player.ytmusic_a" });
  document.body.appendChild(node);
  return node;
}

beforeEach(() => { document.body.innerHTML = ""; });

describe("ytmusic-now-playing", () => {
  it("renders the title from state", async () => {
    const node = el({ media_title: "Midnight City", media_artist: "M83" });
    await node.updateComplete;
    expect(node.shadowRoot.textContent).toContain("Midnight City");
  });

  it("play/pause toggles based on state", async () => {
    const node = el({ media_title: "X", state: "playing" });
    await node.updateComplete;
    node.shadowRoot.querySelector('[data-test="playpause"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "media_pause", { entity_id: "media_player.ytmusic_a" });
  });

  it("next calls media_next_track", async () => {
    const node = el({ media_title: "X" });
    await node.updateComplete;
    node.shadowRoot.querySelector('[data-test="next"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "media_next_track", { entity_id: "media_player.ytmusic_a" });
  });

  it("hides the lyrics toggle when lyrics_supported is false", async () => {
    const node = el({ media_title: "X", lyrics_supported: false });
    await node.updateComplete;
    expect(node.shadowRoot.querySelector('[data-test="lyrics"]')).toBeNull();
  });

  it("shows a speaker prompt when no source", async () => {
    const node = el({ media_title: "X" }, null as any);
    await node.updateComplete;
    expect(node.shadowRoot.textContent.toLowerCase()).toContain("speaker");
  });

  it("volume slider sets volume_level", async () => {
    const node = el({ media_title: "X", volume_level: 0.4 });
    await node.updateComplete;
    const slider = node.shadowRoot.querySelector('[data-test="volume"]');
    slider.value = "0.7";
    slider.dispatchEvent(new Event("change"));
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "volume_set", { entity_id: "media_player.ytmusic_a", volume_level: 0.7 });
  });
});
