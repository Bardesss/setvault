from __future__ import annotations

from setvault_ingest_sources.ytdlp_source import _YtDlpSearchSource


class YouTubeSource(_YtDlpSearchSource):
    kind = "youtube"
    name = "YouTube"
    search_prefix = "ytsearch"

    def _fallback_url(self, ext_id: str) -> str:
        return f"https://www.youtube.com/watch?v={ext_id}"
