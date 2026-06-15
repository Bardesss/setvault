from __future__ import annotations

from setvault_ingest_sources.ytdlp_source import _YtDlpSearchSource


class SoundCloudSource(_YtDlpSearchSource):
    kind = "soundcloud"
    name = "SoundCloud"
    search_prefix = "scsearch"
    # No _fallback_url: scsearch flat entries carry `url`; id-only entries are skipped.
