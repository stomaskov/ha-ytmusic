import type { HassEntity } from "./types";

export function currentPosition(stateObj: HassEntity, nowMs: number): number | null {
  const a = stateObj?.attributes ?? {};
  if (a.media_position == null) return null;
  let pos = Number(a.media_position);
  if (stateObj.state === "playing" && a.media_position_updated_at) {
    const updated = Date.parse(a.media_position_updated_at);
    if (!isNaN(updated)) pos += Math.max(0, (nowMs - updated) / 1000);
  }
  if (a.media_duration != null) pos = Math.min(pos, Number(a.media_duration));
  return Math.max(0, pos);
}
