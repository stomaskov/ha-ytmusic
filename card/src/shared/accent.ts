import type { CardConfig } from "./types";

export const DEFAULT_ACCENT = "#ff2d55";

export function resolveAccent(config: CardConfig): string {
  return config?.accent || DEFAULT_ACCENT;
}
