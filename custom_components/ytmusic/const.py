"""Constants for the YouTube Music integration."""

from __future__ import annotations

DOMAIN = "ytmusic"
PLATFORMS = ["media_player"]

# Auth method
CONF_AUTH_METHOD = "auth_method"
AUTH_OAUTH = "oauth"
AUTH_COOKIE = "cookie"

# Auth payload keys (stored in entry.data)
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_OAUTH_TOKEN = "oauth_token"  # dict from token_from_code
CONF_COOKIE = "cookie"  # browser Cookie header (API browser auth)
CONF_STREAM_COOKIE = "stream_cookie"  # browser cookie used for yt-dlp (optional)
CONF_ENTRY_SECRET = "entry_secret"  # per-entry HMAC secret for stream URLs

# Options keys
CONF_DEFAULT_SOURCE = "default_source"  # entity_id of the downstream speaker
CONF_RESULT_LIMIT = "result_limit"
CONF_AUTOPLAY = "autoplay"  # radio at queue end
DEFAULT_RESULT_LIMIT = 20
DEFAULT_AUTOPLAY = True

# Stream
STREAM_FORMAT = "bestaudio[ext=m4a]/bestaudio/best"
STREAM_CACHE_TTL = 300  # seconds; well under Google URL lifetime
STREAM_URL_BASE = "/api/ytmusic/stream"

# Search filters accepted by ytmusicapi
SEARCH_FILTERS = ("songs", "playlists", "albums", "artists")

# TV (youtubei) backend
TV_BASE_API = "https://music.youtube.com/youtubei/v1/"
TV_CLIENT_NAME = "TVHTML5"
TV_CLIENT_VERSION = "7.20240701.00.00"
