from unittest.mock import MagicMock, patch

import pytest
from setvault_ingest_sources.base import IngestSource, SourceError
from setvault_ingest_sources.mixcloud import MixcloudSource


def _resp(json_body):
    r = MagicMock()
    r.json.return_value = json_body
    r.raise_for_status.return_value = None
    return r


def test_mixcloud_satisfies_protocol():
    src = MixcloudSource()
    assert isinstance(src, IngestSource)
    assert src.kind == "mixcloud"
    assert src.name == "Mixcloud"


def test_mixcloud_maps_data():
    body = {"data": [
        {"key": "/dj-m/great-mix/", "name": "Great Mix",
         "url": "https://www.mixcloud.com/dj-m/great-mix/",
         "audio_length": 3600, "user": {"name": "DJ M"},
         "pictures": {"large": "https://pic-l", "medium": "https://pic-m"}},
        {"name": "no key skipped", "url": "https://x"},  # no key -> skipped
    ]}
    src = MixcloudSource()
    with patch("setvault_ingest_sources.mixcloud.httpx.get", return_value=_resp(body)) as g:
        out = src.search("great mix", limit=5)
    _, kwargs = g.call_args
    assert kwargs["params"]["q"] == "great mix"
    assert kwargs["params"]["type"] == "cloudcast"
    assert len(out) == 1
    assert out[0].source_kind == "mixcloud"
    assert out[0].external_id == "dj-m/great-mix"
    assert out[0].title == "Great Mix"
    assert out[0].uploader == "DJ M"
    assert out[0].duration_seconds == 3600
    assert out[0].thumbnail_url == "https://pic-l"
    assert out[0].webpage_url == "https://www.mixcloud.com/dj-m/great-mix/"


def test_mixcloud_empty_query_returns_empty():
    assert MixcloudSource().search("   ") == []


def test_mixcloud_raises_sourceerror():
    src = MixcloudSource()
    with patch("setvault_ingest_sources.mixcloud.httpx.get", side_effect=RuntimeError("net")):
        with pytest.raises(SourceError):
            src.search("x")
