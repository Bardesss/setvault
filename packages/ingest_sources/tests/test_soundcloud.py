from unittest.mock import patch

import pytest
from setvault_ingest_sources.base import IngestSource, SourceError
from setvault_ingest_sources.soundcloud import SoundCloudSource


class _FakeYDL:
    def __init__(self, info): self._info = info
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def extract_info(self, target, download=False):
        assert target.startswith("scsearch")
        return self._info


def test_soundcloud_satisfies_protocol():
    src = SoundCloudSource()
    assert isinstance(src, IngestSource)
    assert src.kind == "soundcloud"
    assert src.name == "SoundCloud"


def test_soundcloud_maps_entries():
    info = {"entries": [
        {"id": "111", "title": "SC Set", "uploader": "DJ S", "duration": 1800,
         "thumbnails": [{"url": "https://t"}], "url": "https://soundcloud.com/dj-s/sc-set"},
    ]}
    src = SoundCloudSource()
    with patch(
        "setvault_ingest_sources.ytdlp_source.yt_dlp.YoutubeDL",
        return_value=_FakeYDL(info),
    ):
        out = src.search("sc set", limit=1)
    assert out[0].source_kind == "soundcloud"
    assert out[0].external_id == "111"
    assert out[0].webpage_url == "https://soundcloud.com/dj-s/sc-set"
    assert out[0].duration_seconds == 1800


def test_soundcloud_raises_sourceerror():
    src = SoundCloudSource()
    with patch(
        "setvault_ingest_sources.ytdlp_source.yt_dlp.YoutubeDL",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(SourceError):
            src.search("x")
