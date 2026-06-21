# YouTube Music for Home Assistant

A from-scratch **YouTube Music** integration for Home Assistant — robust playback, durable authentication, and a family of purpose-built Lovelace cards.

It exposes a `media_player` entity that acts as a **source/proxy**: it resolves tracks and streams them to any of your real speakers (Cast, Sonos, etc.), with a play queue, radio/autoplay, search, and library browsing. Four bundled Lit dashboard cards (now-playing, search, queue, library) are auto-registered — no manual resource setup.

> **Not affiliated with, endorsed by, or sponsored by Google or YouTube.** "YouTube Music" is a trademark of Google LLC. This is an unofficial, community-built integration.
>
> Built as an alternative to `ytube_music_player`, focused on reliable playback (yt-dlp), durable OAuth, clean async code, and a real card UI.

## Features

- **Reliable playback** — stream extraction via `yt-dlp`. An HMAC-signed Home Assistant endpoint 302-redirects to a *freshly resolved* audio URL at fetch time, so the URL the speaker holds never goes stale (kills the 403 class of bugs).
- **Two auth backends:**
  - **OAuth** (recommended) — a durable device-flow login via a custom TVHTML5 youtubei backend. Generic (untyped) search; full library/browse/radio.
  - **Cookie** — paste a browser cookie. Adds typed search (songs/albums/artists/playlists) and lyrics.
- **Queue management** — enqueue, play-next, reorder, remove, jump, clear; radio/autoplay at queue end.
- **Media browser** — browse your library playlists and search from Home Assistant's native media browser.
- **WebSocket API** for the cards — `ytmusic/search`, `ytmusic/browse`, `ytmusic/lyrics`.
- **Four bundled dashboard cards** (Lit + TypeScript, single auto-registered bundle):
  - `ytmusic-now-playing` — immersive now-playing + transport, volume, sleep timer, lyrics (cookie auth)
  - `ytmusic-search` — search + queue actions
  - `ytmusic-queue` — drag-to-reorder queue
  - `ytmusic-library` — browse playlists → tracks

## Requirements

- Home Assistant **2026.6.0+**
- The integration declares its Python deps (`ytmusicapi`, `yt-dlp`) — Home Assistant installs them automatically.

## Installation

### HACS (custom repository)
1. HACS → ⋮ → **Custom repositories** → add `https://github.com/stomaskov/ha-ytmusic` as an **Integration**.
2. Install **YouTube Music**, then restart Home Assistant.

### Manual
Copy `custom_components/ytmusic/` into your Home Assistant `config/custom_components/` directory and restart.

## Setup

Settings → **Devices & Services** → **Add Integration** → **YouTube Music**, then pick an auth method:

- **OAuth (recommended):** create a Google Cloud OAuth client of type *“TVs & Limited Input devices”* and complete the device-code flow. See [`docs/oauth-setup.md`](docs/oauth-setup.md).
- **Cookie:** paste the full `Cookie` header from a logged-in `music.youtube.com` request (enables typed search + lyrics).

Optional: set a **default speaker** and **autoplay (radio at queue end)** in the integration's Options.

## The dashboard cards

The integration auto-registers the bundled card file (`/ytmusic/ytmusic-card.js`) on startup — no Lovelace resource setup needed. In your dashboard, **Add Card** and search for **“YouTube Music”**; all four cards appear. Each auto-detects the `ytmusic` entity (or set it explicitly in the card editor).

## Services

`ytmusic.enqueue`, `ytmusic.play_next`, `ytmusic.start_radio`, `ytmusic.clear_queue`, `ytmusic.remove`, `ytmusic.move`, `ytmusic.jump`, `ytmusic.set_sleep_timer` — plus the standard `media_player.*` transport/volume/seek/source services on the entity.

## Building the cards from source

The dashboard cards live in [`card/`](card/) (Lit + TypeScript + Vite) and build to a **single** committed file at `custom_components/ytmusic/frontend/ytmusic-card.js`.

```bash
cd card
npm install
npm run build      # → ../custom_components/ytmusic/frontend/ytmusic-card.js
npm test           # vitest
```

The committed bundle is what ships; rebuild it after changing anything under `card/src/`, and bump `_CARD_VERSION` in `custom_components/ytmusic/__init__.py` to bust the browser cache.

## Development

```bash
python -m pip install homeassistant pytest-homeassistant-custom-component ytmusicapi yt-dlp ruff
python -m pytest      # integration tests
ruff check .
```

## License

[MIT](LICENSE)
