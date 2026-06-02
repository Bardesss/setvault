from setvault_core.services.tracklist_parse import parse_tracklist_text


def test_parses_mm_ss_format():
    raw = "0:00 Aphex Twin - Xtal\n3:45 Boards of Canada - Roygbiv"
    out = parse_tracklist_text(raw)
    assert len(out) == 2
    assert out[0].start_seconds == 0
    assert out[0].raw_label == "Aphex Twin - Xtal"
    assert out[1].start_seconds == 225
    assert out[1].raw_label == "Boards of Canada - Roygbiv"


def test_parses_hh_mm_ss_format():
    raw = "01:23:45 Floating Points - Last Bloom"
    out = parse_tracklist_text(raw)
    assert out[0].start_seconds == 5025


def test_parses_bracketed_timestamp_format():
    # YouTube-style chapter markers: timestamp wrapped in [ ], em-dash label.
    raw = "[00:00] Aphex Twin — Xtal\n[1:23:45] Floating Points — Last Bloom"
    out = parse_tracklist_text(raw)
    assert len(out) == 2
    assert out[0].start_seconds == 0
    assert out[0].raw_label == "Aphex Twin — Xtal"
    assert out[1].start_seconds == 5025
    assert out[1].raw_label == "Floating Points — Last Bloom"


def test_handles_numbered_list_without_timestamp():
    raw = "1. Artist - Title\n2. Other - Thing"
    out = parse_tracklist_text(raw)
    assert len(out) == 2
    assert out[0].start_seconds is None
    assert out[0].raw_label == "Artist - Title"


def test_strips_label_brackets_kept_in_raw_label():
    raw = "0:00 Artist - Title (Mix Name) [Label]"
    out = parse_tracklist_text(raw)
    assert out[0].raw_label == "Artist - Title (Mix Name) [Label]"


def test_skips_blank_and_metadata_lines():
    raw = "Tracklist:\n\n0:00 A - B\n---\n5:00 C - D\n"
    out = parse_tracklist_text(raw)
    assert len(out) == 2
    assert [e.raw_label for e in out] == ["A - B", "C - D"]


def test_empty_input_returns_empty_list():
    assert parse_tracklist_text("") == []
    assert parse_tracklist_text("   \n  ") == []
