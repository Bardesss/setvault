from setvault_ingest_sources.registry import (
    all_source_kinds,
    get_source,
)
from setvault_ingest_sources.youtube import YouTubeSource


def test_get_source_returns_youtube():
    src = get_source("youtube")
    assert isinstance(src, YouTubeSource)
    assert src.kind == "youtube"


def test_unknown_kind_returns_none():
    assert get_source("nope") is None


def test_all_source_kinds_includes_youtube():
    assert "youtube" in all_source_kinds()
