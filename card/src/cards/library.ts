import { html, css } from "lit";
import { BaseCard } from "../shared/base";
import { frostedStyles } from "../shared/styles";
import { joinArtists } from "../shared/format";
import { browse as wsBrowse } from "../shared/ws";
import type { CardConfig, BrowseItem } from "../shared/types";

class YtmusicLibrary extends BaseCard {
  static properties = { ...BaseCard.properties, _root: { state: true }, _open: { state: true }, _tracks: { state: true }, _loading: { state: true } };
  declare _root: BrowseItem[] | null;
  declare _open: BrowseItem | null;
  declare _tracks: BrowseItem[] | null;
  declare _loading: boolean;

  constructor() {
    super();
    this._root = null;
    this._open = null;
    this._tracks = null;
    this._loading = false;
  }

  static styles = [frostedStyles, css`
    /* Port from docs/superpowers/mockups/browse-layout.html (root grid A + drill-in). */
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(94px, 1fr)); gap: 14px; }
    .tile { cursor: pointer; transition: transform .12s ease; }
    .tile:hover { transform: translateY(-3px); }
    .tile .cov { aspect-ratio: 1; border-radius: 13px; background-size: cover; background-color: rgba(255,255,255,.06); box-shadow: 0 8px 22px -8px rgba(0,0,0,.7); }
    .tile:hover .cov { box-shadow: 0 12px 28px -8px rgba(0,0,0,.85); }
    .tile .n { font-size: 12.5px; margin-top: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .back { display: inline-flex; gap: 7px; align-items: center; color: var(--ytm-dim); cursor: pointer; margin-bottom: 14px; font-size: 13px; }
    .back:hover { color: #fff; }
    .head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; gap: 10px; }
    .playall { display: inline-flex; gap: 8px; align-items: center; background: var(--ytm-accent); color: #fff; font-weight: 650; font-size: 12.5px; padding: 8px 16px; border-radius: 99px; border: none; cursor: pointer; box-shadow: 0 6px 18px -6px var(--ytm-accent); transition: transform .12s ease; white-space: nowrap; }
    .playall:hover { transform: translateY(-1px); }
    .trow { display: flex; align-items: center; gap: 11px; padding: 8px 6px; border-radius: 10px; transition: background .12s ease; }
    .trow:hover { background: rgba(255,255,255,.06); }
    .num { color: #7e8593; width: 18px; text-align: center; font-size: 12px; flex-shrink: 0; }
    .cov2 { width: 36px; height: 36px; border-radius: 8px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; }
    .meta { flex: 1; min-width: 0; } .n2 { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .acts { display: flex; gap: 7px; flex-shrink: 0; } .acts .ic { width: 30px; height: 30px; font-size: 12px; }
  `];

  setConfig(c: CardConfig): void { super.setConfig(c); }
  getCardSize(): number { return 6; }

  updated(changed: Map<string, unknown>) {
    super.updated(changed);
    if (changed.has("hass") && this._root == null && this.entityId) this.loadRoot();
  }

  async loadRoot(): Promise<void> {
    if (!this.entityId) return;
    this._loading = true;
    try { this._root = await wsBrowse(this.hass, this.entityId); } finally { this._loading = false; }
  }

  async openItem(item: BrowseItem): Promise<void> {
    if (!this.entityId || !item.id) return;
    this._open = item; this._tracks = null; this._loading = true;
    try { this._tracks = await wsBrowse(this.hass, this.entityId, "playlist", item.id); } finally { this._loading = false; }
  }

  private _playAll() {
    if (this._open?.id) this.callService("media_player", "play_media", { media_content_type: "playlist", media_content_id: this._open.id });
  }

  private _playTrack(t: BrowseItem) {
    this.callService("media_player", "play_media", {
      media_content_type: "music", media_content_id: t.video_id,
      extra: { metadata: { title: t.title, artist: joinArtists(t.artists), album: t.album, thumbnail: t.thumbnail, duration: t.duration } },
    });
  }

  private _enqueue(t: BrowseItem) {
    this.callService("ytmusic", "enqueue", { video_id: t.video_id, title: t.title, artist: joinArtists(t.artists) });
  }

  render() {
    if (!this.stateObj) return html`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    return html`<ha-card><div class="glass" style="padding:14px">${this._open ? this._renderDrill() : this._renderRoot()}</div></ha-card>`;
  }

  private _renderRoot() {
    if (this._loading && !this._root) return html`<div class="empty">Loading library…</div>`;
    const items = this._root ?? [];
    if (!items.length) return html`<div class="empty">Library is empty</div>`;
    return html`<div class="grid">${items.map((p) => html`<div class="tile" @click=${() => this.openItem(p)}>
      <div class="cov" style=${p.thumbnail ? `background-image:url(${p.thumbnail})` : ""}></div>
      <div class="n ttl">${p.title}</div></div>`)}</div>`;
  }

  private _renderDrill() {
    return html`
      <div class="back" @click=${() => { this._open = null; this._tracks = null; }}>‹ Library</div>
      <div class="head"><div class="ttl">${this._open?.title}</div>
        <button class="playall" data-test="playall" @click=${this._playAll}>▶ Play all</button></div>
      ${this._loading && !this._tracks ? html`<div class="empty">Loading…</div>` : (this._tracks ?? []).map((t, i) => html`
        <div class="trow"><span class="num">${i + 1}</span>
          <div class="cov2" style=${t.thumbnail ? `background-image:url(${t.thumbnail})` : ""}></div>
          <div class="meta"><div class="n2 ttl" style="font-size:13px">${t.title}</div><div class="n2 sub" style="font-size:11.5px">${joinArtists(t.artists)}</div></div>
          <div class="acts"><button class="ic solid" @click=${() => this._playTrack(t)}>▶</button><button class="ic" @click=${() => this._enqueue(t)}>＋</button></div>
        </div>`)}`;
  }

  static getConfigElement() { return document.createElement("ytmusic-library-editor"); }
  static getStubConfig() { return { entity: "" }; }
}
customElements.define("ytmusic-library", YtmusicLibrary);

class YtmusicLibraryEditor extends BaseCard {
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
customElements.define("ytmusic-library-editor", YtmusicLibraryEditor);

(window as any).customCards = (window as any).customCards ?? [];
(window as any).customCards.push({ type: "ytmusic-library", name: "YouTube Music — Library", description: "Browse your library playlists + tracks", preview: true });
