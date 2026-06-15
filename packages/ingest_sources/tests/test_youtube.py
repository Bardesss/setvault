from setvault_ingest_sources.base import Candidate, IngestSource
from setvault_ingest_sources.youtube import YouTubeSource


def test_youtube_source_satisfies_protocol():
    src = YouTubeSource()
    assert isinstance(src, IngestSource)
    assert src.kind == "youtube"
    assert src.name


def test_candidate_is_a_dataclass():
    c = Candidate(
        source_kind="youtube", external_id="abc123", title="Some Set",
        uploader="DJ X", duration_seconds=3600,
        thumbnail_url="https://img", webpage_url="https://youtu.be/abc123",
    )
    assert c.external_id == "abc123"
    assert c.webpage_url.endswith("abc123")
