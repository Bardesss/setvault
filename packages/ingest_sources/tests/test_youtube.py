from unittest.mock import patch

import pytest
from setvault_ingest_sources.base import IngestSource, SourceError
from setvault_ingest_sources.youtube import YouTubeSource


class _FakeYDL:
    def __init__(self, info): self._info = info
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def extract_info(self, target, download=False):
        assert target.startswith("ytsearch")
        assert "best dj set" in target
        return self._info


def test_youtube_source_satisfies_protocol():
    src = YouTubeSource()
    assert isinstance(src, IngestSource)
    assert src.kind == "youtube"
    assert src.name


def test_youtube_search_maps_entries_to_candidates():
    info = {"entries": [
        {"id": "vid1", "title": "Best DJ Set 2024", "uploader": "DJ X",
         "duration": 3600, "thumbnails": [{"url": "https://t1"}],
         "url": "https://www.youtube.com/watch?v=vid1"},
        {"id": "vid2", "title": "Another Set", "channel": "DJ Y",
         "duration": None, "thumbnail": "https://t2",
         "webpage_url": "https://youtu.be/vid2"},
    ]}
    src = YouTubeSource()
    with patch("setvault_ingest_sources.ytdlp_source.yt_dlp.YoutubeDL",
               return_value=_FakeYDL(info)):
        out = src.search("best dj set", limit=2)
    assert [c.external_id for c in out] == ["vid1", "vid2"]
    assert out[0].uploader == "DJ X"
    assert out[0].duration_seconds == 3600
    assert out[0].thumbnail_url == "https://t1"
    assert out[0].webpage_url == "https://www.youtube.com/watch?v=vid1"
    assert out[1].uploader == "DJ Y"          # falls back to `channel`
    assert out[1].webpage_url == "https://youtu.be/vid2"


def test_youtube_search_raises_sourceerror_on_ydl_failure():
    src = YouTubeSource()
    with patch("setvault_ingest_sources.ytdlp_source.yt_dlp.YoutubeDL",
               side_effect=RuntimeError("boom")):
        with pytest.raises(SourceError):
            src.search("x")
