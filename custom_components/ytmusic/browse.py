"""Media browse tree for the ytmusic entity."""

from __future__ import annotations

from homeassistant.components.media_player import BrowseMedia, MediaClass


async def async_browse(player, media_content_type, media_content_id) -> BrowseMedia:
    if media_content_id in (None, "root"):
        playlists = player._entry.runtime_data.coordinator.data or []
        children = [
            BrowseMedia(
                title=p["title"],
                media_class=MediaClass.PLAYLIST,
                media_content_type="playlist",
                media_content_id=p["id"],
                can_play=True,
                can_expand=False,
                thumbnail=p.get("thumbnail"),
            )
            for p in playlists
        ]
        return BrowseMedia(
            title="YouTube Music",
            media_class=MediaClass.DIRECTORY,
            media_content_type="root",
            media_content_id="root",
            can_play=False,
            can_expand=True,
            children=children,
        )
    raise ValueError(f"Unknown browse id: {media_content_id}")
