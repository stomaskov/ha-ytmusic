from custom_components.ytmusic.models import Track, RepeatMode
from custom_components.ytmusic.queue import PlayQueue


def _t(vid):
    return Track(
        video_id=vid,
        title=f"t{vid}",
        artists="a",
        album=None,
        thumbnail=None,
        duration=180,
    )


def test_track_as_dict():
    d = _t("x").as_dict()
    assert d["video_id"] == "x"
    assert d["title"] == "tx"


def test_empty_queue_current_is_none():
    q = PlayQueue()
    assert q.current() is None
    assert q.next() is None
    assert q.previous() is None
    assert q.tracks_remaining() == 0


def test_set_queue_and_navigation():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")])
    assert q.current().video_id == "1"
    assert q.next().video_id == "2"
    assert q.next().video_id == "3"
    assert q.next() is None  # end, repeat OFF
    assert q.previous().video_id == "2"


def test_previous_at_start_stays():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2")])
    assert q.previous().video_id == "1"
    assert q.index == 0


def test_repeat_all_wraps():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2")])
    q.set_repeat(RepeatMode.ALL)
    q.next()  # ->2
    assert q.next().video_id == "1"  # wrap


def test_repeat_one_stays():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2")])
    q.set_repeat(RepeatMode.ONE)
    assert q.next().video_id == "1"


def test_enqueue_next_inserts_after_current():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2")])
    q.enqueue_next([_t("9")])
    assert [t.video_id for t in q._items] == ["1", "9", "2"]
    assert q.next().video_id == "9"


def test_remove_before_current_shifts_index():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")], start=2)
    q.remove(0)
    assert q.current().video_id == "3"


def test_remove_current_midlist_advances_to_next():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")], start=1)  # playing "2"
    q.remove(1)
    assert q.index == 1
    assert q.current().video_id == "3"


def test_remove_current_last_clamps():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")], start=2)  # playing last
    q.remove(2)
    assert q.index == 1
    assert q.current().video_id == "2"


def test_remove_after_current_is_noop_on_index():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")], start=0)  # playing "1"
    q.remove(2)  # remove a later track
    assert q.index == 0
    assert q.current().video_id == "1"


def test_move_keeps_playing_track():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3")], start=1)  # playing "2"
    q.move(2, 0)  # move "3" to front -> [3,1,2]
    assert [t.video_id for t in q._items] == ["3", "1", "2"]
    assert q.current().video_id == "2"  # still playing "2"


def test_move_with_duplicate_tracks_tracks_correct_position():
    q = PlayQueue()
    a1, a2, b = _t("dup"), _t("dup"), _t("other")  # a1 == a2 by value
    q.set_queue([a1, a2, b], start=1)  # playing the SECOND "dup" (index 1)
    q.move(2, 0)  # move "other" to front -> [other, dup, dup]
    assert [t.video_id for t in q._items] == ["other", "dup", "dup"]
    assert q.index == 2  # still the second dup, not the first


def test_shuffle_keeps_current_first_and_is_deterministic():
    q = PlayQueue()
    q.set_queue([_t("1"), _t("2"), _t("3"), _t("4")], start=1)  # playing "2"
    q.set_shuffle(True, shuffler=lambda lst: lst.reverse())
    assert q.current().video_id == "2"
    assert q.index == 0
    assert [t.video_id for t in q._items] == ["2", "4", "3", "1"]
