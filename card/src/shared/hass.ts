import type { Hass, HassEntity, CardConfig } from "./types";

export function detectEntity(hass: Hass, config: CardConfig): string | null {
  if (config.entity) return config.entity;
  const reg = hass.entities ?? {};
  const byPlatform = Object.values(reg).filter((e) => e.platform === "ytmusic" && e.entity_id.startsWith("media_player."));
  if (byPlatform.length === 1) return byPlatform[0].entity_id;
  if (byPlatform.length > 1) return byPlatform[0].entity_id;
  const byPrefix = Object.keys(hass.states).filter((id) => id.startsWith("media_player.ytmusic_"));
  return byPrefix.length ? byPrefix[0] : null;
}

export function sourceState(hass: Hass, stateObj: HassEntity): HassEntity | null {
  const src = stateObj?.attributes?.source;
  return src ? hass.states[src] ?? null : null;
}
