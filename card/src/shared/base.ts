import { LitElement } from "lit";
import type { Hass, HassEntity, CardConfig } from "./types";
import { detectEntity } from "./hass";
import { resolveAccent } from "./accent";

export class BaseCard extends LitElement {
  static properties = { hass: { attribute: false }, _config: { state: true } };
  declare hass: Hass;
  declare _config: CardConfig;

  setConfig(config: CardConfig): void {
    if (!config) throw new Error("Invalid configuration");
    this._config = config;
  }

  getCardSize(): number { return 3; }

  get entityId(): string | null {
    return this.hass && this._config ? detectEntity(this.hass, this._config) : null;
  }

  get stateObj(): HassEntity | undefined {
    const id = this.entityId;
    return id ? this.hass?.states?.[id] : undefined;
  }

  get accent(): string { return resolveAccent(this._config ?? ({ type: "" } as CardConfig)); }

  updated(changed: Map<string, unknown>): void {
    super.updated(changed);
    this.style.setProperty("--ytm-accent", this.accent);
  }

  protected callService(domain: string, service: string, data: Record<string, any> = {}): void {
    const id = this.entityId;
    if (id) this.hass.callService(domain, service, { entity_id: id, ...data });
  }
}
