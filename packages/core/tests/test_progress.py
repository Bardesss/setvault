from setvault_core.progress import ProgressEvent, channel_for_set


def test_channel_for_set_namespaces_by_id():
    assert channel_for_set("abc") == "sv:progress:set:abc"


def test_event_round_trips_through_json():
    e = ProgressEvent(kind="transcode", live_set_id="abc",
                      job_id="j1", progress_pct=42, message="encoding…")
    raw = e.model_dump_json()
    parsed = ProgressEvent.model_validate_json(raw)
    assert parsed == e
