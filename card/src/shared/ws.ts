import type { Hass, SearchResult, BrowseItem, LyricsLine } from "./types";

export async function search(hass: Hass, entityId: string, query: string, filter?: string): Promise<SearchResult[]> {
  const msg: Record<string, any> = { type: "ytmusic/search", entity_id: entityId, query };
  if (filter) msg.filter = filter;
  const res = await hass.callWS<{ results: SearchResult[] }>(msg);
  return res.results ?? [];
}

export async function browse(hass: Hass, entityId: string, itemType?: string, itemId?: string): Promise<BrowseItem[]> {
  const msg: Record<string, any> = { type: "ytmusic/browse", entity_id: entityId };
  if (itemType) msg.item_type = itemType;
  if (itemId) msg.item_id = itemId;
  const res = await hass.callWS<{ items: BrowseItem[] }>(msg);
  return res.items ?? [];
}

export async function lyrics(hass: Hass, entityId: string, videoId: string): Promise<{ lines: LyricsLine[] | null; synced: boolean }> {
  return hass.callWS({ type: "ytmusic/lyrics", entity_id: entityId, video_id: videoId });
}
