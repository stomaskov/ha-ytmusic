import { describe, it, expect, vi } from "vitest";
import { search, browse, lyrics } from "../shared/ws";

function mockHass(result: any) {
  return { callWS: vi.fn().mockResolvedValue(result) } as any;
}

describe("ws client", () => {
  it("search sends the right message and returns results", async () => {
    const hass = mockHass({ results: [{ kind: "song", id: "v1", title: "S", subtitle: "A", thumbnail: null }] });
    const out = await search(hass, "media_player.ytmusic_x", "daft", "songs");
    expect(hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/search", entity_id: "media_player.ytmusic_x", query: "daft", filter: "songs" });
    expect(out[0].id).toBe("v1");
  });
  it("search omits filter when not given", async () => {
    const hass = mockHass({ results: [] });
    await search(hass, "e", "q");
    expect(hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/search", entity_id: "e", query: "q" });
  });
  it("browse root", async () => {
    const hass = mockHass({ items: [{ id: "PL", title: "Mix", thumbnail: null, kind: "playlist", can_expand: true }] });
    const out = await browse(hass, "e");
    expect(hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/browse", entity_id: "e" });
    expect(out[0].kind).toBe("playlist");
  });
  it("browse drill-in", async () => {
    const hass = mockHass({ items: [] });
    await browse(hass, "e", "playlist", "PL1");
    expect(hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/browse", entity_id: "e", item_type: "playlist", item_id: "PL1" });
  });
  it("lyrics returns the payload", async () => {
    const hass = mockHass({ lines: [{ text: "hi", start_ms: 0 }], synced: true });
    const out = await lyrics(hass, "e", "v1");
    expect(hass.callWS).toHaveBeenCalledWith({ type: "ytmusic/lyrics", entity_id: "e", video_id: "v1" });
    expect(out.synced).toBe(true);
  });
});
