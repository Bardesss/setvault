from __future__ import annotations

import yt_dlp

from setvault_ingest_sources.base import Candidate, SourceError


def _thumb(entry: dict) -> str | None:
    if entry.get("thumbnail"):
        return entry["thumbnail"]
    thumbs = entry.get("thumbnails") or []
    return thumbs[-1]["url"] if thumbs else None


class YouTubeSource:
    kind = "youtube"
    name = "YouTube"

    def search(self, query: str, *, limit: int = 20) -> list[Candidate]:
        query = query.strip()
        if not query:
            return []
        limit = max(1, min(limit, 50))
        # extract_flat keeps this a lightweight search (no per-video extraction).
        opts = {"quiet": True, "no_warnings": True, "skip_download": True,
                "extract_flat": True, "default_search": "ytsearch"}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        except Exception as e:
            raise SourceError(f"youtube search failed: {e}") from e
        out: list[Candidate] = []
        for e in (info or {}).get("entries", []) or []:
            ext_id = e.get("id")
            if not ext_id:
                continue
            url = e.get("webpage_url") or e.get("url") or f"https://www.youtube.com/watch?v={ext_id}"
            dur = e.get("duration")
            out.append(Candidate(
                source_kind="youtube",
                external_id=ext_id,
                title=e.get("title") or "(untitled)",
                uploader=e.get("uploader") or e.get("channel"),
                duration_seconds=int(dur) if dur else None,
                thumbnail_url=_thumb(e),
                webpage_url=url,
            ))
        return out
