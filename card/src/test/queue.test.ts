import { describe, it, expect, vi, beforeEach } from "vitest";
import "../cards/queue";

function el(queue: any[], pos = 0, extra: Record<string, any> = {}) {
  const node: any = document.createElement("ytmusic-queue");
  const stateObj = { entity_id: "media_player.ytmusic_a", state: "playing", attributes: { queue, queue_position: pos, shuffle: false } };
  node.hass = { states: { "media_player.ytmusic_a": stateObj }, entities: {}, callService: vi.fn().mockResolvedValue(undefined) };
  node.setConfig({ type: "custom:ytmusic-queue", entity: "media_player.ytmusic_a", ...extra });
  document.body.appendChild(node);
  return node;
}
beforeEach(() => { document.body.innerHTML = ""; });
const Q = [{ video_id: "a", title: "A", artists: "x" }, { video_id: "b", title: "B", artists: "y" }, { video_id: "c", title: "C", artists: "z" }];
const longQ = Array.from({ length: 20 }, (_, i) => ({ video_id: `v${i}`, title: `T${i}`, artists: "x" }));

describe("ytmusic-queue", () => {
  it("renders a row per queue item", async () => {
    const node = el(Q); await node.updateComplete;
    expect(node.shadowRoot.querySelectorAll('[data-test="qrow"]').length).toBe(3);
  });
  it("tap a row jumps to its index", async () => {
    const node = el(Q, 0); await node.updateComplete;
    node.shadowRoot.querySelectorAll('[data-test="qrow"]')[2].click();
    expect(node.hass.callService).toHaveBeenCalledWith("ytmusic", "jump", { entity_id: "media_player.ytmusic_a", index: 2 });
  });
  it("remove calls ytmusic.remove with the index (current row not removable)", async () => {
    const node = el(Q, 0); await node.updateComplete;
    const removeBtns = node.shadowRoot.querySelectorAll('[data-test="remove"]');
    expect(removeBtns.length).toBe(2);          // current row (index 0) has no remove
    removeBtns[0].click();                       // first removable row = index 1
    expect(node.hass.callService).toHaveBeenCalledWith("ytmusic", "remove", { entity_id: "media_player.ytmusic_a", index: 1 });
  });
  it("clear + shuffle wired", async () => {
    const node = el(Q, 0); await node.updateComplete;
    node.shadowRoot.querySelector('[data-test="clear"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("ytmusic", "clear_queue", { entity_id: "media_player.ytmusic_a" });
    node.shadowRoot.querySelector('[data-test="shuffle"]').click();
    expect(node.hass.callService).toHaveBeenCalledWith("media_player", "shuffle_set", { entity_id: "media_player.ytmusic_a", shuffle: true });
  });
  it("empty queue message", async () => {
    const node = el([]); await node.updateComplete;
    expect(node.shadowRoot.textContent.toLowerCase()).toContain("empty");
  });

  it("max_visible caps the scroll height but renders every row", async () => {
    const node = el(longQ, 0, { max_visible: 5 }); await node.updateComplete;
    const scroll = node.shadowRoot.querySelector('[data-test="qscroll"]');
    expect(scroll).not.toBeNull();
    expect(scroll.style.maxHeight).toBe("290px");            // 5 × 58
    expect(node.shadowRoot.querySelectorAll('[data-test="qrow"]').length).toBe(20);
  });

  it("max_visible 0 means unlimited (no max-height cap)", async () => {
    const node = el(longQ, 0, { max_visible: 0 }); await node.updateComplete;
    const scroll = node.shadowRoot.querySelector('[data-test="qscroll"]');
    expect(scroll).not.toBeNull();
    expect(scroll.style.maxHeight).toBe("");
  });

  it("defaults to a 7-row cap when max_visible is omitted", async () => {
    const node = el(longQ); await node.updateComplete;
    expect(node.shadowRoot.querySelector('[data-test="qscroll"]').style.maxHeight).toBe("406px"); // 7 × 58
  });
});
