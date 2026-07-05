import { describe, it, expect, vi, beforeEach } from "vitest";
import "../cards/search";

function el(typed = true, extra: Record<string, any> = {}, results?: any[]) {
  const node: any = document.createElement("ytmusic-search");
  const stateObj = { entity_id: "media_player.ytmusic_a", state: "idle", attributes: { typed_search: typed } };
  node.hass = {
    states: { "media_player.ytmusic_a": stateObj }, entities: {},
    callService: vi.fn().mockResolvedValue(undefined),
    callWS: vi.fn().mockResolvedValue({ results: results ?? [{ kind: "song", id: "v1", title: "Get Lucky", subtitle: "Daft Punk", thumbnail: null }] }),
  };
  node.setConfig({ type: "custom:ytmusic-search", entity: "media_player.ytmusic_a", ...extra });
  document.body.appendChild(node);
  return node;
}
beforeEach(() => { document.body.innerHTML = ""; });
const manyResults = Array.from({ length: 15 }, (_, i) => ({ kind: "song", id: `v${i}`, title: `Song ${i}`, subtitle: "Artist", thumbnail: null }));

describe("ytmusic-search", () => {
  it("queries the WS and renders rows", async () => {
    const node = el();
    await node.updateComplete;
    await node.runSearch("daft");          // test seam: bypass the debounce timer
    await node.updateComplete;
    expect(node.hass.callWS).toHaveBeenCalledWith(expect.objectContaining({ type: "ytmusic/search", entity_id: "media_player.ytmusic_a", query: "daft" }));
    expect(node.shadowRoot.textContent).toContain("Get Lucky");
  });

  it("play maps a song to play_media music with metadata", async () => {
    const node = el();
    await node.runSearch("daft"); await node.updateComplete;
    node.shadowRoot.querySelector('[data-test="play"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "play_media", expect.objectContaining({
      entity_id: "media_player.ytmusic_a", media_content_type: "music", media_content_id: "v1",
      extra: { metadata: expect.objectContaining({ title: "Get Lucky" }) },
    }));
  });

  it("enqueue calls ytmusic.enqueue for a song", async () => {
    const node = el();
    await node.runSearch("daft"); await node.updateComplete;
    node.shadowRoot.querySelector('[data-test="enqueue"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("ytmusic", "enqueue", expect.objectContaining({ entity_id: "media_player.ytmusic_a", video_id: "v1" }));
  });

  it("shows type tabs only when typed_search", async () => {
    const typed = el(true); await typed.updateComplete;
    expect(typed.shadowRoot.querySelector('[data-test="tabs"]')).not.toBeNull();
    document.body.innerHTML = "";
    const mixed = el(false); await mixed.updateComplete;
    expect(mixed.shadowRoot.querySelector('[data-test="tabs"]')).toBeNull();
  });

  it("max_visible caps the results scroll height", async () => {
    const node = el(true, { max_visible: 4 }, manyResults);
    await node.runSearch("x"); await node.updateComplete;
    const scroll = node.shadowRoot.querySelector('[data-test="sscroll"]');
    expect(scroll).not.toBeNull();
    expect(scroll.style.maxHeight).toBe("264px");            // 4 × 66
  });

  it("defaults to a 6-row cap when max_visible is omitted", async () => {
    const node = el(true, {}, manyResults);
    await node.runSearch("x"); await node.updateComplete;
    expect(node.shadowRoot.querySelector('[data-test="sscroll"]').style.maxHeight).toBe("396px"); // 6 × 66
  });
});
