from setvault_ingest_sources.base import Candidate, IngestSource, SourceError


class _StubSource:
    kind = "stub"
    name = "Stub"

    def search(self, query: str, *, limit: int = 20) -> list[Candidate]:
        return []


def test_stub_source_satisfies_protocol():
    src = _StubSource()
    assert isinstance(src, IngestSource)
    assert src.kind == "stub"
    assert src.name


def test_candidate_is_a_dataclass():
    c = Candidate(
        source_kind="youtube", external_id="abc123", title="Some Set",
        uploader="DJ X", duration_seconds=3600,
        thumbnail_url="https://img", webpage_url="https://youtu.be/abc123",
    )
    assert c.external_id == "abc123"
    assert c.webpage_url.endswith("abc123")


def test_source_error_is_exception():
    assert issubclass(SourceError, Exception)
