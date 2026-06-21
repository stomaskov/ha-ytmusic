import { html, css, nothing } from "lit";
import { BaseCard } from "../shared/base";
import { frostedStyles } from "../shared/styles";
import { search as wsSearch } from "../shared/ws";
import type { CardConfig, SearchResult } from "../shared/types";

const KIND_TO_PLAY: Record<string, string> = { song: "music", video: "music", playlist: "playlist", album: "album", artist: "artist" };
const TABS: Array<{ key: string; label: string; filter?: string }> = [
  { key: "all", label: "All" }, { key: "songs", label: "Songs", filter: "songs" },
  { key: "albums", label: "Albums", filter: "albums" }, { key: "artists", label: "Artists", filter: "artists" },
  { key: "playlists", label: "Playlists", filter: "playlists" },
];

class YtmusicSearch extends BaseCard {
  static properties = { ...BaseCard.properties, _q: { state: true }, _tab: { state: true }, _results: { state: true }, _loading: { state: true } };
  declare _q: string; declare _tab: string; declare _results: SearchResult[] | null; declare _loading: boolean;
  private _seq = 0; private _debounce?: number;

  constructor() {
    super();
    this._q = "";
    this._tab = "all";
    this._results = null;
    this._loading = false;
  }

  static styles = [frostedStyles, css`
    /* Layout B — action list. Ported from docs/superpowers/mockups/search-layout.html */
    .box { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,.25); border: 1px solid rgba(255,255,255,.10); border-radius: 14px; padding: 11px 14px; transition: border-color .15s ease; }
    .box:focus-within { border-color: var(--ytm-accent); }
    .box input { flex: 1; background: transparent; border: none; color: #fff; outline: none; font-size: 14px; }
    .box input::placeholder { color: var(--ytm-dim); }
    .clear-btn { cursor: pointer; color: var(--ytm-dim); }
    .tabs { display: flex; gap: 7px; margin: 14px 0 6px; flex-wrap: wrap; }
    .tab { font-size: 12px; padding: 6px 12px; border-radius: 99px; background: rgba(255,255,255,.07); color: var(--ytm-dim); cursor: pointer; border: none; transition: background .12s ease, color .12s ease; }
    .tab:hover { background: rgba(255,255,255,.13); color: #fff; }
    .tab.on { background: #fff; color: #111; font-weight: 650; }
    .row { display: flex; align-items: center; gap: 12px; padding: 9px 8px; border-radius: 12px; transition: background .12s ease; }
    .row:hover { background: rgba(255,255,255,.06); }
    .cov { width: 48px; height: 48px; border-radius: 10px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; box-shadow: 0 4px 12px -4px rgba(0,0,0,.6); }
    .meta { flex: 1; min-width: 0; }
    .n { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .acts { display: flex; gap: 7px; flex-shrink: 0; }
    .acts .ic { width: 32px; height: 32px; font-size: 13px; }
    .badge { font-size: 9px; letter-spacing: .04em; text-transform: uppercase; background: rgba(255,255,255,.14); color: var(--ytm-dim); padding: 2px 6px; border-radius: 6px; margin-left: 8px; vertical-align: middle; }
    .empty { text-align: center; padding: 28px 0; color: var(--ytm-dim); font-size: 14px; }
  `];

  setConfig(c: CardConfig): void { super.setConfig(c); }
  getCardSize(): number { return 6; }
  private get typed() { return !!this.stateObj?.attributes?.typed_search; }

  private _onInput(ev: Event) {
    this._q = (ev.target as HTMLInputElement).value;
    if (this._debounce) clearTimeout(this._debounce);
    this._debounce = window.setTimeout(() => this.runSearch(this._q), 300);
  }

  async runSearch(query: string): Promise<void> {
    const q = query.trim();
    if (!q || !this.entityId) { this._results = null; return; }
    const seq = ++this._seq; this._loading = true;
    const filter = this.typed && this._tab !== "all" ? TABS.find((t) => t.key === this._tab)?.filter : undefined;
    try {
      const res = await wsSearch(this.hass, this.entityId, q, filter);
      if (seq === this._seq) { this._results = res; }
    } finally { if (seq === this._seq) this._loading = false; }
  }

  private _play(r: SearchResult) {
    this.callService("media_player", "play_media", {
      media_content_type: KIND_TO_PLAY[r.kind] ?? "music", media_content_id: r.id,
      extra: { metadata: { title: r.title, artist: r.subtitle, thumbnail: r.thumbnail } },
    });
  }

  private _enqueue(r: SearchResult) {
    if (r.kind === "song" || r.kind === "video") this.callService("ytmusic", "enqueue", { video_id: r.id, title: r.title, artist: r.subtitle });
    else this._play(r);
  }

  private _more(r: SearchResult) {
    if (r.kind === "song" || r.kind === "video") this.callService("ytmusic", "play_next", { video_id: r.id, title: r.title, artist: r.subtitle });
    else this.callService("ytmusic", "start_radio", { video_id: r.id });
  }

  render() {
    if (!this.stateObj) return html`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    return html`<ha-card><div class="glass" style="padding:14px">
      <div class="box">🔎 <input .value=${this._q} placeholder="Search YouTube Music" @input=${this._onInput} />
        ${this._q ? html`<span @click=${() => { this._q = ""; this._results = null; }} style="cursor:pointer">✕</span>` : nothing}</div>
      ${this.typed ? html`<div class="tabs" data-test="tabs">${TABS.map((t) => html`<button class="tab ${this._tab === t.key ? "on" : ""}" @click=${() => { this._tab = t.key; this.runSearch(this._q); }}>${t.label}</button>`)}</div>` : nothing}
      ${this._renderResults()}
    </div></ha-card>`;
  }

  private _renderResults() {
    if (this._loading) return html`<div class="empty">Searching…</div>`;
    if (this._results == null) return html`<div class="empty">Search for songs, albums, artists…</div>`;
    if (!this._results.length) return html`<div class="empty">No results</div>`;
    return this._results.map((r) => html`<div class="row">
      <div class="cov" style=${r.thumbnail ? `background-image:url(${r.thumbnail})` : ""}></div>
      <div class="meta"><div class="n ttl">${r.title}<span class="badge">${r.kind}</span></div><div class="n sub">${r.subtitle}</div></div>
      <div class="acts">
        <button class="ic solid" data-test="play" @click=${() => this._play(r)}>▶</button>
        <button class="ic" data-test="enqueue" @click=${() => this._enqueue(r)}>＋</button>
        <button class="ic" data-test="more" @click=${() => this._more(r)}>⋯</button>
      </div></div>`);
  }

  static getConfigElement() { return document.createElement("ytmusic-search-editor"); }
  static getStubConfig() { return { entity: "" }; }
}
customElements.define("ytmusic-search", YtmusicSearch);

class YtmusicSearchEditor extends BaseCard {
  setConfig(c: CardConfig): void { this._config = c; }
  private _schema = [
    { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
    { name: "accent", selector: { text: {} } },
  ];
  render() {
    if (!this.hass || !this._config) return html``;
    return html`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema} .computeLabel=${(s: any) => s.name}
      @value-changed=${(e: CustomEvent) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: e.detail.value }, bubbles: true, composed: true }))}></ha-form>`;
  }
}
customElements.define("ytmusic-search-editor", YtmusicSearchEditor);

(window as any).customCards = (window as any).customCards ?? [];
(window as any).customCards.push({ type: "ytmusic-search", name: "YouTube Music — Search", description: "Search + queue tracks for the ytmusic player", preview: true });
