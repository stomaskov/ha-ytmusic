import { css } from "lit";

// Shared surface + control language for the ytmusic card family.
// Designed to look premium on a FLAT dark dashboard (not reliant on backdrop
// translucency): each card carries its own layered dark-gradient surface with a
// top-light hairline, depth shadow, and a faint accent glow. A subtle
// backdrop-filter is kept so themed/wallpaper backgrounds still frost nicely.
export const frostedStyles = css`
  :host {
    display: block;
    --ytm-accent: #ff3358;
    --ytm-accent-2: #ff7a93;
    --ytm-text: #f4f5f8;
    --ytm-dim: #99a0ad;
    --ytm-hairline: rgba(255, 255, 255, 0.08);
    --ytm-radius: 20px;
    color: var(--ytm-text);
    font-family: var(--ha-card-header-font-family, var(--paper-font-body1_-_font-family, inherit));
  }

  /* Let the card's own surface show — HA's opaque ha-card would flatten it. */
  ha-card {
    background: transparent;
    border: none;
    box-shadow: none;
    overflow: visible;
  }

  .glass {
    position: relative;
    border-radius: var(--ytm-radius);
    background:
      radial-gradient(135% 105% at 0% 0%, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0) 55%),
      linear-gradient(180deg, #1c2028 0%, #131519 100%);
    border: 1px solid var(--ytm-hairline);
    box-shadow: 0 16px 40px -16px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(10px);
    overflow: hidden;
  }
  /* Faint accent glow in the corner for atmosphere. */
  .glass::after {
    content: "";
    position: absolute;
    top: -45%;
    right: -25%;
    width: 70%;
    height: 90%;
    background: radial-gradient(closest-side, var(--ytm-accent), transparent);
    opacity: 0.12;
    pointer-events: none;
  }
  .glass > * { position: relative; z-index: 1; }

  .sub { color: var(--ytm-dim); }
  .ttl { color: var(--ytm-text); font-weight: 650; letter-spacing: -0.01em; }
  .label {
    color: var(--ytm-dim);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    white-space: nowrap;
  }

  .ic {
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    color: #fff;
    cursor: pointer;
    transition: transform 0.13s ease, background 0.13s ease, color 0.13s ease, box-shadow 0.13s ease;
  }
  .ic:hover { background: rgba(255, 255, 255, 0.17); transform: translateY(-1px); }
  .ic.solid { background: #fff; color: #111; box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.7); }
  .ic.solid:hover { box-shadow: 0 10px 26px -6px var(--ytm-accent); transform: translateY(-1px) scale(1.03); }
  .ic.active { background: var(--ytm-accent); color: #fff; box-shadow: 0 0 16px -2px var(--ytm-accent); }
  button.ic { border: none; padding: 0; }

  .bar { height: 5px; border-radius: 99px; background: rgba(255, 255, 255, 0.14); position: relative; cursor: pointer; }
  .bar > i {
    position: absolute;
    inset: 0 auto 0 0;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--ytm-accent), var(--ytm-accent-2));
  }

  .empty { color: var(--ytm-dim); text-align: center; padding: 26px 14px; font-size: 13px; }

  /* Reusable bounded scroll region (queue + search lists). Thin themed scrollbar. */
  .scroll {
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.18) transparent;
  }
  .scroll::-webkit-scrollbar { width: 6px; }
  .scroll::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.18); border-radius: 99px; }
  .scroll::-webkit-scrollbar-track { background: transparent; }
`;
