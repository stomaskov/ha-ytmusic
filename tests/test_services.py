from unittest.mock import AsyncMock, MagicMock, patch


from custom_components.ytmusic.media_player import YtMusicPlayer
from custom_components.ytmusic.models import Track


def _player(hass):
    runtime = MagicMock()
    runtime.api = AsyncMock()
    runtime.entry_secret = "s"
    entry = MagicMock()
    entry.entry_id = "e1"
    entry.runtime_data = runtime
    entry.options = {}
    p = YtMusicPlayer(hass, entry)
    p.hass = hass
    p.async_write_ha_state = MagicMock()
    return p


async def test_enqueue_appends(hass):
    p = _player(hass)
    p._queue.set_queue([Track("a", "A", "x", None, None, 1)])
    await p.svc_enqueue(video_id="b", title="B", artist="y")
    assert [t.video_id for t in p._queue._items] == ["a", "b"]


async def test_play_next_inserts_after_current(hass):
    p = _player(hass)
    p._queue.set_queue(
        [Track("a", "A", "x", None, None, 1), Track("c", "C", "z", None, None, 1)]
    )
    await p.svc_play_next(video_id="b", title="B", artist="y")
    assert [t.video_id for t in p._queue._items] == ["a", "b", "c"]


async def test_clear_queue(hass):
    p = _player(hass)
    p._queue.set_queue([Track("a", "A", "x", None, None, 1)])
    await p.svc_clear_queue()
    assert p._queue.current() is None


async def test_remove_index_zero(hass):
    p = _player(hass)
    p._queue.set_queue(
        [Track("a", "A", "x", None, None, 1), Track("b", "B", "y", None, None, 1)]
    )
    await p.svc_remove(index=0)
    assert [t.video_id for t in p._queue._items] == ["b"]


async def test_move_from_zero(hass):
    p = _player(hass)
    p._queue.set_queue(
        [Track("a", "A", "x", None, None, 1), Track("b", "B", "y", None, None, 1)]
    )
    await p.svc_move(from_index=0, to_index=1)
    assert [t.video_id for t in p._queue._items] == ["b", "a"]


async def test_start_radio_replaces_queue(hass):
    p = _player(hass)
    p._api.get_radio.return_value = [Track("r1", "R", "x", None, None, 1)]
    p._push_current = AsyncMock()
    await p.svc_start_radio(video_id="seed")
    p._api.get_radio.assert_awaited_once_with("seed")
    assert p._queue.current().video_id == "r1"
    p._push_current.assert_awaited_once()


async def test_jump_plays_index(hass):
    p = _player(hass)
    p._queue.set_queue(
        [Track("a", "A", "x", None, None, 1), Track("b", "B", "y", None, None, 1), Track("c", "C", "z", None, None, 1)]
    )
    p._push_current = AsyncMock()
    await p.svc_jump(index=2)
    assert p._queue.current().video_id == "c"
    p._push_current.assert_awaited_once()


async def test_jump_out_of_range_noop(hass):
    p = _player(hass)
    p._queue.set_queue([Track("a", "A", "x", None, None, 1)])
    p._push_current = AsyncMock()
    await p.svc_jump(index=5)
    assert p._queue.current().video_id == "a"
    p._push_current.assert_not_awaited()


async def test_sleep_timer_timed_arms_and_fires(hass):
    p = _player(hass)
    captured = {}

    def fake_call_later(hass_, delay, cb):
        captured["delay"] = delay
        captured["cb"] = cb
        return MagicMock()  # cancel handle

    with patch("custom_components.ytmusic.media_player.async_call_later", fake_call_later):
        await p.svc_set_sleep_timer(minutes=30)
    assert captured["delay"] == 1800
    assert p.extra_state_attributes["sleep_timer_ends_at"] is not None

    # fire the scheduled callback -> pauses + clears
    p._source_call = AsyncMock()
    captured["cb"](None)
    await hass.async_block_till_done()
    p._source_call.assert_awaited_with("media_pause")
    assert p.extra_state_attributes["sleep_timer_ends_at"] is None


async def test_sleep_timer_cancel(hass):
    p = _player(hass)
    with patch("custom_components.ytmusic.media_player.async_call_later", return_value=MagicMock()):
        await p.svc_set_sleep_timer(minutes=15)
    await p.svc_set_sleep_timer(minutes=0)
    assert p.extra_state_attributes["sleep_timer_ends_at"] is None
    assert p.extra_state_attributes["sleep_timer_end_of_track"] is False


async def test_sleep_timer_end_of_track_pauses_on_track_end(hass):
    from homeassistant.core import State
    p = _player(hass)
    p._queue.set_queue([Track("a", "A", "x", None, None, 1), Track("b", "B", "y", None, None, 1)])
    p._active = True
    await p.svc_set_sleep_timer(end_of_track=True)
    assert p.extra_state_attributes["sleep_timer_end_of_track"] is True
    p._source_call = AsyncMock()
    event = MagicMock()
    event.data = {
        "old_state": State("media_player.speaker", "playing"),
        "new_state": State("media_player.speaker", "idle"),
    }
    p._handle_source_state(event)
    await hass.async_block_till_done()
    p._source_call.assert_awaited_with("media_pause")
    assert p._queue.current().video_id == "a"  # did NOT advance to b
    assert p.extra_state_attributes["sleep_timer_end_of_track"] is False


async def test_clear_queue_cancels_sleep_timer(hass):
    p = _player(hass)
    with patch("custom_components.ytmusic.media_player.async_call_later", return_value=MagicMock()):
        await p.svc_set_sleep_timer(minutes=15)
    await p.svc_clear_queue()
    assert p.extra_state_attributes["sleep_timer_ends_at"] is None
