from __future__ import annotations

from setvault_ingest_sources.base import IngestSource
from setvault_ingest_sources.youtube import YouTubeSource

# 7A ships one source. 7B adds SoundCloud/Mixcloud/Internet Archive and may
# switch this to entry-point discovery; the get_source() contract stays.
_SOURCES: dict[str, IngestSource] = {YouTubeSource().kind: YouTubeSource()}


def all_source_kinds() -> list[str]:
    return sorted(_SOURCES)


def get_source(kind: str) -> IngestSource | None:
    return _SOURCES.get(kind)
