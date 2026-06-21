import { html, css, nothing } from "lit";
import { BaseCard } from "../shared/base";
import { frostedStyles } from "../shared/styles";
import { joinArtists } from "../shared/format";
import type { CardConfig } from "../shared/types";

class YtmusicQueue extends BaseCard {
  static properties = { ...BaseCard.properties, _drag: { state: true } };
  declare _drag: number | null;

  constructor() {
    super();
    this._drag = null;
  }

  static styles = [frostedStyles, css`
    .hdr { display: flex; align-items: center; gap: 8px 10px; margin-bottom: 12px; flex-wrap: wrap; }
    .count { font-size: 11px; font-weight: 700; color: var(--ytm-dim); background: rgba(255,255,255,.08); border-radius: 99px; padding: 2px 8px; }
    .tools { margin-left: auto; display: flex; gap: 8px; }
    .tool { font-size: 12px; padding: 5px 11px; border-radius: 99px; background: rgba(255,255,255,.08); color: var(--ytm-text); border: none; cursor: pointer; white-space: nowrap; transition: background .12s ease; }
    .tool:hover { background: rgba(255,255,255,.16); }
    .qrow { position: relative; display: flex; align-items: center; gap: 11px; padding: 8px; border-radius: 12px; cursor: pointer; transition: background .12s ease; }
    .qrow:hover { background: rgba(255,255,255,.06); }
    .qrow.now { background: linear-gradient(90deg, rgba(255,51,88,.20), rgba(255,51,88,.05)); }
    .qrow.now::before { content: ''; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px; border-radius: 99px; background: var(--ytm-accent); }
    .handle { color: #7e8593; cursor: grab; font-size: 16px; width: 16px; text-align: center; flex-shrink: 0; }
    .cov { width: 42px; height: 42px; border-radius: 9px; background-size: cover; background-color: rgba(255,255,255,.06); flex-shrink: 0; box-shadow: 0 4px 12px -4px rgba(0,0,0,.6); }
    .meta { flex: 1; min-width: 0; } .n { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .x { color: #9aa0ab; background: rgba(255,255,255,.06); width: 26px; height: 26px; border-radius: 50%; border: none; cursor: pointer; flex-shrink: 0; transition: background .12s ease, color .12s ease; }
    .x:hover { background: rgba(255,51,88,.28); color: #fff; }
    .eq { color: var(--ytm-accent); width: 16px; text-align: center; font-size: 13px; flex-shrink: 0; }
  `];

  setConfig(c: CardConfig): void { super.setConfig(c); }
  getCardSize(): number { return 5; }

  private _move(from: number, to: number) {
    if (from !== to) this.callService("ytmusic", "move", { from_index: from, to_index: to });
    this._drag = null;
  }

  render() {
    const a = this.stateObj?.attributes;
    if (!a) return html`<ha-card><div class="empty">No YouTube Music entity</div></ha-card>`;
    const queue: any[] = a.queue ?? [];
    const cur = a.queue_position ?? 0;
    return html`<ha-card><div class="glass" style="padding:16px">
      <div class="hdr">
        <span class="label">Up Next</span>
        <span class="count">${queue.length}</span>
        <div class="tools">
          <button class="tool" data-test="shuffle" @click=${() => this.callService("media_player", "shuffle_set", { shuffle: !a.shuffle })}>🔀 Shuffle</button>
          <button class="tool" data-test="clear" @click=${() => this.callService("ytmusic", "clear_queue")}>Clear</button>
        </div>
      </div>
      ${!queue.length ? html`<div class="empty">Queue is empty</div>` : queue.map((t, i) => html`
        <div class="qrow ${i === cur ? "now" : ""}" data-test="qrow" draggable="true"
             @click=${() => this.callService("ytmusic", "jump", { index: i })}
             @dragstart=${() => (this._drag = i)}
             @dragover=${(e: Event) => e.preventDefault()}
             @drop=${(e: Event) => { e.preventDefault(); if (this._drag != null) this._move(this._drag, i); }}>
          ${i === cur ? html`<span class="eq">▮▮</span>` : html`<span class="handle" @click=${(e: Event) => e.stopPropagation()}>≡</span>`}
          <div class="cov" style=${t.thumbnail ? `background-image:url(${t.thumbnail})` : ""}></div>
          <div class="meta"><div class="n ttl" style="font-size:13px">${t.title}</div><div class="n sub" style="font-size:11.5px">${joinArtists(t.artists)}</div></div>
          ${i === cur ? nothing : html`<button class="x" data-test="remove" @click=${(e: Event) => { e.stopPropagation(); this.callService("ytmusic", "remove", { index: i }); }}>✕</button>`}
        </div>`)}
    </div></ha-card>`;
  }

  static getConfigElement() { return document.createElement("ytmusic-queue-editor"); }
  static getStubConfig() { return { entity: "" }; }
}
customElements.define("ytmusic-queue", YtmusicQueue);

class YtmusicQueueEditor extends BaseCard {
  setConfig(c: CardConfig): void { this._config = c; }
  private _schema = [
    { name: "entity", selector: { entity: { integration: "ytmusic", domain: "media_player" } } },
    { name: "accent", selector: { text: {} } },
    { name: "max_visible", selector: { number: { min: 0, mode: "box" } } },
  ];
  render() {
    if (!this.hass || !this._config) return html``;
    return html`<ha-form .hass=${this.hass} .data=${this._config} .schema=${this._schema} .computeLabel=${(s: any) => s.name}
      @value-changed=${(e: CustomEvent) => this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: e.detail.value }, bubbles: true, composed: true }))}></ha-form>`;
  }
}
customElements.define("ytmusic-queue-editor", YtmusicQueueEditor);

(window as any).customCards = (window as any).customCards ?? [];
(window as any).customCards.push({ type: "ytmusic-queue", name: "YouTube Music — Queue", description: "Queue with reorder/remove for the ytmusic player", preview: true });
