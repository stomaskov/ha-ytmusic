export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, any>;
}

export interface Hass {
  states: Record<string, HassEntity>;
  entities?: Record<string, { entity_id: string; platform?: string }>;
  language?: string;
  callService(domain: string, service: string, data?: Record<string, any>): Promise<unknown>;
  callWS<T = any>(msg: Record<string, any>): Promise<T>;
}

export interface CardConfig {
  type: string;
  entity?: string;
  accent?: string;
  title?: string;
  show_lyrics?: boolean;
  show_sleep_timer?: boolean;
  max_visible?: number;
}

export interface SearchResult {
  kind: "song" | "video" | "playlist" | "album" | "artist";
  id: string;
  title: string;
  subtitle: string;
  thumbnail: string | null;
}

export interface BrowseItem {
  kind: "playlist" | "song";
  id?: string;
  video_id?: string;
  title: string;
  subtitle?: string;
  artists?: string;
  album?: string | null;
  thumbnail: string | null;
  duration?: number | null;
  can_expand?: boolean;
}

export interface LyricsLine { text: string; start_ms: number | null; }
