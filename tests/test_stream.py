from unittest.mock import patch

import pytest

from custom_components.ytmusic.stream import StreamResolver


@pytest.fixture
def fake_time():
    clock = {"t": 1000.0}
    return clock


async def test_resolve_returns_url_and_caches(hass, fake_time):
    resolver = StreamResolver(hass, time_fn=lambda: fake_time["t"])
    with patch("custom_components.ytmusic.stream.YoutubeDL") as ydl_cls:
        ydl = ydl_cls.return_value.__enter__.return_value
        ydl.extract_info.return_value = {"url": "https://g/audio.m4a"}
        url1 = await resolver.resolve("vid1")
        url2 = await resolver.resolve("vid1")  # cached, no second extract
    assert url1 == "https://g/audio.m4a"
    assert url2 == "https://g/audio.m4a"
    assert ydl.extract_info.call_count == 1


async def test_cache_expires(hass, fake_time):
    resolver = StreamResolver(hass, ttl=60, time_fn=lambda: fake_time["t"])
    with patch("custom_components.ytmusic.stream.YoutubeDL") as ydl_cls:
        ydl = ydl_cls.return_value.__enter__.return_value
        ydl.extract_info.return_value = {"url": "https://g/a"}
        await resolver.resolve("v")
        fake_time["t"] += 120  # past ttl
        await resolver.resolve("v")
    assert ydl.extract_info.call_count == 2


async def test_retry_alt_format_on_failure(hass, fake_time):
    resolver = StreamResolver(hass, time_fn=lambda: fake_time["t"])
    with patch("custom_components.ytmusic.stream.YoutubeDL") as ydl_cls:
        ydl = ydl_cls.return_value.__enter__.return_value
        ydl.extract_info.side_effect = [Exception("403"), {"url": "https://g/fallback"}]
        url = await resolver.resolve("v")
    assert url == "https://g/fallback"
    assert ydl.extract_info.call_count == 2


async def test_raises_when_both_formats_fail(hass, fake_time):
    resolver = StreamResolver(hass, time_fn=lambda: fake_time["t"])
    with patch("custom_components.ytmusic.stream.YoutubeDL") as ydl_cls:
        ydl = ydl_cls.return_value.__enter__.return_value
        ydl.extract_info.side_effect = Exception("403")
        with pytest.raises(RuntimeError):
            await resolver.resolve("v")
    assert ydl.extract_info.call_count == 2
