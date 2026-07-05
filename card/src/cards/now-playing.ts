import { html, css, nothing, unsafeCSS, type CSSResult } from "lit";
import { BaseCard } from "../shared/base";
import { frostedStyles } from "../shared/styles";
import { currentPosition } from "../shared/position";
import { formatTime, joinArtists } from "../shared/format";
import { lyrics as fetchLyrics } from "../shared/ws";
import type { CardConfig, LyricsLine } from "../shared/types";

const REPEAT_NEXT: Record<string, string> = { off: "all", all: "one", one: "off" };

// Landscape "hero" layout: large cover left, left-aligned body right, bigger controls.
// Shared between the responsive container-query path and the forced `layout: wide` path
// by prefixing every rule with the host selector — no CSS nesting required.
const wideRules = (s: CSSResult) => css`
  ${s} .card { min-height: auto; }
  ${s} .stage { flex-direction: row; align-items: center; gap: 28px; }
  ${s} .cover { width: 200px; height: 200px; margin: 0; }
  ${s} .body { min-width: 0; }
  ${s} .meta { text-align: left; }
  ${s} .ttl { font-size: 26px; }
  ${s} .sub { font-size: 15px; }
  ${s} .ctl { margin-top: 18px; }
  ${s} .trans { justify-content: flex-start; gap: 22px; }
  ${s} .secrow { justify-content: flex-start; }
  ${s} .ic { width: 52px; height: 52px; font-size: 20px; }
  ${s} .ic.big { width: 72px; height: 72px; font-size: 30px; }
  ${s} .ic.sm { width: 40px; height: 40px; font-size: 15px; }
  ${s} input[type=range] { width: 120px; }
`;
const WIDE_AUTO = unsafeCSS(':host([data-layout="auto"])');
const WIDE_FORCED = unsafeCSS(':host([data-layout="wide"])');

class YtmusicNowPlaying extends BaseCard {
  static properties = { ...BaseCard.properties, _tick: { state: true }, _showLyrics: { state: true }, _lyrics: { state: true }, _sleepMenu: { state: true } };
  declare _tick: number;
  declare _showLyrics: boolean;
  declare _lyrics: { lines: LyricsLine[] | null; synced: boolean } | null;
  declare _sleepMenu: boolean;
  private _timer?: number;

  static styles = [frostedStyles, css`
    /* Immersive (direction A): blurred entity_picture backdrop + dark veil; centered cover/title; bottom controls */
    .card { position: relative; border-radius: 20px; overflow: hidden; min-height: 400px; padding: 0; display: flex; flex-direction: column;
      background: radial-gradient(120% 80% at 50% -10%, rgba(255,255,255,.07), transparent 55%), linear-gradient(180deg, #1c2028, #111317);
      border: 1px solid var(--ytm-hairline);
      box-shadow: 0 18px 44px -16px rgba(0,0,0,.78), inset 0 1px 0 rgba(255,255,255,.07); }
    .bg { position: absolute; inset: 0; background-size: cover; background-position: center; filter: blur(26px) saturate(1.45) brightness(1.05); transform: scale(1.4); opacity: 1; }
    .veil { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,8,12,.35), rgba(8,8,12,.5) 42%, rgba(8,8,12,.88)); }
    .inner { position: relative; height: 100%; padding: 18px; display: flex; flex-direction: column; flex: 1; }
    .stage { display: flex; flex-direction: column; flex: 1; }
    .body { display: flex; flex-direction: column; flex: 1; }
    .cover { width: 138px; height: 138px; border-radius: 16px; margin: 14px auto 16px; background-size: cover; background-position: center; box-shadow: 0 20px 50px -10px rgba(0,0,0,.7); cursor: pointer; flex-shrink: 0; display: grid; place-items: center; background-color: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.10); }
    .cover .ph { font-size: 46px; line-height: 1; color: var(--ytm-accent); opacity: .6; }
    .meta { text-align: center; }
    .ttl { font-size: 18px; }
    .sub { font-size: 13px; margin-top: 2px; }
    .ctl { margin-top: auto; }
    .bar { margin: 14px 0 6px; }
    .bar > i::after { content: ''; position: absolute; right: -5px; top: 50%; transform: translateY(-50%); width: 11px; height: 11px; border-radius: 50%; background: #fff; }
    .times { display: flex; justify-content: space-between; color: #aeb4c0; font-size: 11px; font-variant-numeric: tabular-nums; }
    .trans { display: flex; align-items: center; justify-content: center; gap: 18px; margin-top: 12px; }
    .ic { width: 46px; height: 46px; font-size: 18px; }
    .ic.big { width: 64px; height: 64px; font-size: 26px; }
    .ic.sm { width: 36px; height: 36px; font-size: 14px; }
    .secrow { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 14px; flex-wrap: wrap; }
    .chip { display: inline-flex; gap: 6px; align-items: center; padding: 5px 10px; border-radius: 99px; background: rgba(255,255,255,.10); font-size: 12px; color: #dfe3ea; }
    .chip.active { background: var(--ytm-accent); color: #fff; }
    .lyr { position: absolute; inset: 0; padding: 18px; overflow: auto; display: flex; flex-direction: column; background: rgba(8,8,12,.92); }
    .lyr-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .lyr-body { flex: 1; overflow: hidden auto; }
    .lyr-body p { margin: 7px 0; color: rgba(255,255,255,.45); font-size: 14px; }
    .lyr-body p.on { color: #fff; font-weight: 600; font-size: 16px; }
    .menu { position: absolute; right: 16px; bottom: 64px; background: rgba(20,22,28,.96); border: 1px solid rgba(255,255,255,.16); border-radius: 12px; padding: 7px; width: 150px; z-index: 10; }
    .menu .menu-title { color: #8a909c; font-size: 10px; text-transform: uppercase; letter-spacing: .05em; padding: 4px 10px; }
    .menu .mi { color: #dfe3ea; font-size: 12.5px; padding: 7px 10px; border-radius: 7px; cursor: pointer; }
    .menu .mi:hover { background: rgba(255,255,255,.08); }
    select { background: rgba(255,255,255,.10); color: #fff; border: none; border-radius: 8px; padding: 5px 9px; font-size: 12px; cursor: pointer; max-width: 100%; box-sizing: border-box; }
    input[type=range] { -webkit-appearance: none; appearance: none; width: 96px; height: 4px; border-radius: 99px; background: rgba(255,255,255,.18); cursor: pointer; vertical-align: middle; }
    input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 12px; height: 12px; border-radius: 50%; background: #fff; }
    input[type=range]::-moz-range-thumb { width: 12px; height: 12px; border: none; border-radius: 50%; background: #fff; }
    input[type=range]::-moz-range-progress { height: 4px; border-radius: 99px; background: var(--ytm-accent); }
    .speaker-prompt { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 24px 18px; }

    /* Responsive: go wide when the card has room (auto), unless forced compact. */
    :host { container-type: inline-size; }
    @container (min-width: 560px) { ${wideRules(WIDE_AUTO)} }
    ${wideRules(WIDE_FORCED)}
  `];

  connectedCallback(): void { super.connectedCallback(); this._timer = window.setInterval(() => { this._tick = Date.now(); }, 1000); }
  disconnectedCallback(): void { super.disconnectedCallback(); if (this._timer) clearInterval(this._timer); }

  setConfig(config: CardConfig): void { super.setConfig(config); }
  getCardSize(): number { return 6; }

  updated(changed: Map<string, unknown>): void {
    super.updated(changed);
    this.setAttribute("data-layout", this._config?.layout ?? "auto");
  }

  private get a() { return this.stateObj?.attributes ?? {}; }

  private _toggleLyrics() {
    this._showLyrics = !this._showLyrics;
    if (this._showLyrics && this.entityId) {
      const vid = (this.a.queue ?? [])[this.a.queue_position]?.video_id;
      if (vid) {
        fetchLyrics(this.hass, this.entityId, vid)
          .then((r) => (this._lyrics = r))
          .catch(() => (this._lyrics = { lines: null, synced: false }));
      }
    }
  }

  private _seek(ev: MouseEvent) {
    const bar = ev.currentTarget as HTMLElement;
    const rect = bar.getBoundingClientRect();
    const frac = Math.min(1, Math.max(0, (ev.clientX - rect.left) / rect.width));
    const dur = Number(this.a.media_duration) || 0;
    if (dur) this.callService("media_player", "media_seek", { seek_position: frac * dur });
  }

  private _sleep(opt: { minutes?: number; end_of_track?: boolean }) {
    this.callService("ytmusic", "set_sleep_timer", opt);
    this._sleepMenu = false;
  }

  render() {
    const obj = this.stateObj;
    if (!obj) return html`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    const a = this.a;
    if (!a.source) {
      return html`<ha-card><div class="card">
        <div class="inner">
          <div class="speaker-prompt">
            <div class="empty">Select a speaker to start playback</div>
            <select @change=${(e: Event) => this.callService("media_player", "select_source", { source: (e.target as HTMLSelectElement).value })}>
              <option value="">Choose speaker…</option>
              ${(a.source_list ?? []).map((s: string) => html`<option value=${s}>${s}</option>`)}
            </select>
          </div>
        </div>
      </div></ha-card>`;
    }
    const art = a.entity_picture ? `url(${a.entity_picture})` : "none";
    const playing = obj.state === "playing";
    const pos = currentPosition(obj, this._tick || Date.now()) ?? 0;
    const dur = Number(a.media_duration) || 0;
    const frac = dur ? Math.min(100, (pos / dur) * 100) : 0;
    return html`<ha-card>
      <div class="card">
        <div class="bg" style="background-image:${art}"></div>
        <div class="veil"></div>
        <div class="inner">
          ${this._showLyrics ? this._renderLyrics(pos) : nothing}
          <div class="stage" data-test="stage">
          <div class="cover ${a.entity_picture ? "has-art" : ""}"
               style=${a.entity_picture ? `background-image:url(${a.entity_picture})` : ""}
               @click=${() => a.lyrics_supported && this._toggleLyrics()}>
            ${a.entity_picture ? nothing : html`<span class="ph">♫</span>`}
          </div>
          <div class="body">
          <div class="meta">
            <div class="ttl">${a.media_title ?? "Nothing playing"}</div>
            <div class="sub">${joinArtists(a.media_artist)}</div>
          </div>
          <div class="ctl">
            <div class="bar" @click=${this._seek}><i style="width:${frac}%"></i></div>
            <div class="times"><span>${formatTime(pos)}</span><span>${formatTime(dur)}</span></div>
            <div class="trans">
              <button class="ic" data-test="prev"
                      @click=${() => this.callService("media_player", "media_previous_track")}>⏮</button>
              <button class="ic solid big" data-test="playpause"
                      @click=${() => this.callService("media_player", playing ? "media_pause" : "media_play")}>
                ${playing ? "⏸" : "▶"}
              </button>
              <button class="ic" data-test="next"
                      @click=${() => this.callService("media_player", "media_next_track")}>⏭</button>
            </div>
            <div class="secrow">
              <button class="ic sm" data-test="shuffle"
                      @click=${() => this.callService("media_player", "shuffle_set", { shuffle: !a.shuffle })}
                      style=${a.shuffle ? "color:var(--ytm-accent)" : ""}>🔀</button>
              <button class="ic sm" data-test="repeat"
                      @click=${() => this.callService("media_player", "repeat_set", { repeat: REPEAT_NEXT[a.repeat ?? "off"] })}>
                ${a.repeat === "one" ? "🔂" : "🔁"}
              </button>
              <button class="ic sm" data-test="mute"
                      @click=${() => this.callService("media_player", "volume_mute", { is_volume_muted: !a.is_volume_muted })}>
                ${a.is_volume_muted ? "🔇" : "🔊"}
              </button>
              <button class="ic sm" data-test="stop" title="Stop"
                      @click=${() => this.callService("media_player", "media_stop")}>⏹</button>
              <input data-test="volume" type="range" min="0" max="1" step="0.01"
                     .value=${String(a.volume_level ?? 0)}
                     @change=${(e: Event) => this.callService("media_player", "volume_set", { volume_level: Number((e.target as HTMLInputElement).value) })} />
              ${this._config.show_sleep_timer === false ? nothing : html`
                <button class="ic sm" data-test="sleep"
                        @click=${() => (this._sleepMenu = !this._sleepMenu)}>⏲</button>`}
              ${a.lyrics_supported && this._config.show_lyrics !== false ? html`
                <button class="ic sm" data-test="lyrics" @click=${this._toggleLyrics}>💬</button>` : nothing}
              ${a.source ? html`
                <button class="ic sm" data-test="disconnect" title="Stop & disconnect speaker"
                        @click=${() => this.callService("ytmusic", "disconnect")}>⏏</button>` : nothing}
              <select class="chip"
                      @change=${(e: Event) => this.callService("media_player", "select_source", { source: (e.target as HTMLSelectElement).value })}>
                ${(a.source_list ?? []).map((s: string) => html`<option value=${s} ?selected=${s === a.source}>${s}</option>`)}
              </select>
            </div>
            ${this._sleepCountdown()}
            ${this._sleepMenu ? this._renderSleepMenu() : nothing}
          </div>
          </div>
          </div>
        </div>
      </div>
    </ha-card>`;
  }

  private _sleepCountdown() {
    const a = this.a;
    if (a.sleep_timer_end_of_track) {
      return html`<div class="secrow"><span class="chip active">⏲ stops after this track</span></div>`;
    }
    if (!a.sleep_timer_ends_at) return nothing;
    const left = Math.max(0, Date.parse(a.sleep_timer_ends_at) - (this._tick || Date.now()));
    return html`<div class="secrow"><span class="chip active">⏲ ${formatTime(left / 1000)} left</span></div>`;
  }

  private _renderSleepMenu() {
    return html`<div class="menu glass">
      <div class="menu-title">Sleep timer</div>
      ${[15, 30, 45].map((m) => html`<div class="mi" @click=${() => this._sleep({ minutes: m })}>${m} min</div>`)}
      <div class="mi" @click=${() => this._sleep({ end_of_track: true })}>End of track</div>
      <div class="mi" @click=${() => this._sleep({ minutes: 0 })}>Off</div>
    </div>`;
  }

  private _renderLyrics(pos: number) {
    const lines = this._lyrics?.lines;
    return html`<div class="lyr" @click=${() => (this._showLyrics = false)}>
      <div class="lyr-header">
        <span class="sub" style="text-align:left">${this.a.media_title ?? ""}</span>
        <button class="ic sm" style="flex-shrink:0">✕</button>
      </div>
      <div class="lyr-body">
        ${!lines
          ? html`<div class="empty">No lyrics</div>`
          : lines.map((ln, i) => {
              const next = lines[i + 1];
              const on = this._lyrics?.synced && ln.start_ms != null
                && pos * 1000 >= ln.start_ms
                && (!next || next.start_ms == null || pos * 1000 < next.start_ms);
              return html`<p class=${on ? "on" : ""}>${ln.text}</p>`;
            })}
      </div>
    </div>`;
  }

  static getConfigElement() { return document.createElement("ytmusic-now-playing-editor"); }
  static getStubConfig() { return { entity: "" }; }
}
customElements.define("ytmusic-now-playing", YtmusicNowPlaying);

class YtmusicNowPlayingEditor extends BaseCard {
  setConfig(config: CardConfig): void { this._config = config; }
  private _schema = [
    { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
    { name: "accent", selector: { text: {} } },
    { name: "layout", selector: { select: { mode: "dropdown", options: [
      { value: "auto", label: "Auto (responsive)" },
      { value: "wide", label: "Wide (landscape)" },
      { value: "compact", label: "Compact (vertical)" },
    ] } } },
    { name: "show_lyrics", selector: { boolean: {} } },
    { name: "show_sleep_timer", selector: { boolean: {} } },
  ];
  render() {
    if (!this.hass || !this._config) return html``;
    return html`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema}
      .computeLabel=${(s: { name: string }) => s.name} @value-changed=${this._vc}></ha-form>`;
  }
  private _vc(ev: CustomEvent) {
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: (ev as CustomEvent<{ value: CardConfig }>).detail.value }, bubbles: true, composed: true }));
  }
}
customElements.define("ytmusic-now-playing-editor", YtmusicNowPlayingEditor);

(window as any).customCards = (window as any).customCards ?? [];
(window as any).customCards.push({ type: "ytmusic-now-playing", name: "YouTube Music — Now Playing", description: "Immersive now-playing + transport for the ytmusic player", preview: true });
