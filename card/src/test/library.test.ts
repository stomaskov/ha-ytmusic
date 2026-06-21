import { describe, it, expect, vi, beforeEach } from "vitest";
import "../cards/library";

function el(rootItems: any[]) {
  const node: any = document.createElement("ytmusic-library");
  const stateObj = { entity_id: "media_player.ytmusic_a", state: "idle", attributes: {} };
  node.hass = {
    states: { "media_player.ytmusic_a": stateObj }, entities: {},
    callService: vi.fn().mockResolvedValue(undefined),
    callWS: vi.fn().mockResolvedValue({ items: rootItems }),
  };
  node.setConfig({ type: "custom:ytmusic-library", entity: "media_player.ytmusic_a" });
  document.body.appendChild(node);
  return node;
}
beforeEach(() => { document.body.innerHTML = ""; });
const ROOT = [{ id: "PL1", title: "Workout", thumbnail: null, kind: "playlist", can_expand: true }];

describe("ytmusic-library", () => {
  it("loads + renders library tiles", async () => {
    const node = el(ROOT);
    await node.loadRoot();              // test seam
    await node.updateComplete;
    expect(node.hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/browse", entity_id: "media_player.ytmusic_a" });
    expect(node.shadowRoot.textContent).toContain("Workout");
  });
  it("opening a playlist drills in and Play all plays the playlist", async () => {
    const node = el(ROOT);
    await node.loadRoot(); await node.updateComplete;
    node.hass.callWS.mockResolvedValueOnce({ items: [{ video_id: "v1", title: "Song", artists: "A", kind: "song", thumbnail: null }] });
    await node.openItem({ id: "PL1", title: "Workout", kind: "playlist" });
    await node.updateComplete;
    expect(node.hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/browse", entity_id: "media_player.ytmusic_a", item_type: "playlist", item_id: "PL1" });
    node.shadowRoot.querySelector('[data-test="playall"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "play_media", expect.objectContaining({ media_content_type: "playlist", media_content_id: "PL1" }));
  });
});
