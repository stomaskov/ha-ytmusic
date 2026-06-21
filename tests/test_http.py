from unittest.mock import AsyncMock


from custom_components.ytmusic.http import (
    YtMusicStreamView,
    build_stream_path,
    sign,
)


def test_sign_is_stable_and_distinct():
    a = sign("secret", "e1", "v1")
    assert a == sign("secret", "e1", "v1")
    assert a != sign("secret", "e1", "v2")
    assert a != sign("other", "e1", "v1")


def test_build_stream_path_shape():
    sig = sign("secret", "e1", "v1")
    assert build_stream_path("e1", "v1", "secret") == f"/api/ytmusic/stream/e1/v1/{sig}"


async def test_view_redirects_on_valid_signature():
    resolver = AsyncMock()
    resolver.resolve.return_value = "https://g/audio"
    view = YtMusicStreamView({"e1": resolver}, {"e1": "secret"})
    sig = sign("secret", "e1", "v1")
    resp = await view.get(object(), "e1", "v1", sig)
    assert resp.status == 302
    assert resp.headers["Location"] == "https://g/audio"


async def test_view_rejects_bad_signature():
    view = YtMusicStreamView({"e1": AsyncMock()}, {"e1": "secret"})
    resp = await view.get(object(), "e1", "v1", "deadbeef")
    assert resp.status == 403
    view._resolvers["e1"].resolve.assert_not_called()


async def test_view_502_on_resolve_failure():
    resolver = AsyncMock()
    resolver.resolve.side_effect = RuntimeError("nope")
    view = YtMusicStreamView({"e1": resolver}, {"e1": "secret"})
    sig = sign("secret", "e1", "v1")
    resp = await view.get(object(), "e1", "v1", sig)
    assert resp.status == 502


async def test_view_404_unknown_entry():
    view = YtMusicStreamView({}, {})
    resp = await view.get(object(), "missing", "v1", "x")
    assert resp.status == 404
