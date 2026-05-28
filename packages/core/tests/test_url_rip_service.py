from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from setvault_core.services.url_rip import (
    extract_platform_and_id,
    probe_url,
)


@pytest.mark.parametrize(("url", "expected_platform", "expected_id"), [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "youtube", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ?t=42", "youtube", "dQw4w9WgXcQ"),
    ("https://soundcloud.com/foo/bar", "soundcloud", None),
    ("https://www.mixcloud.com/foo/bar/", "mixcloud", None),
    ("https://archive.org/details/foo-bar", "internet_archive", "foo-bar"),
    ("https://random.example.com/x", "other", None),
])
def test_extract_platform_and_id(url: str, expected_platform: str, expected_id: str | None):
    platform, ext_id = extract_platform_and_id(url)
    assert platform == expected_platform
    assert ext_id == expected_id


def test_probe_url_returns_metadata():
    """probe_url() calls yt_dlp.YoutubeDL.extract_info(download=False) and
    normalises the result into a ProbeResult dataclass."""
    fake_info = {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "uploader": "Rick Astley",
        "duration": 213,
        "thumbnail": "https://example.com/thumb.jpg",
        "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "extractor_key": "Youtube",
    }
    mock_ydl_ctx = MagicMock()
    mock_ydl_ctx.__enter__.return_value.extract_info.return_value = fake_info
    with patch("setvault_core.services.url_rip.yt_dlp.YoutubeDL", return_value=mock_ydl_ctx):
        result = probe_url("https://youtu.be/dQw4w9WgXcQ")
    assert result.platform == "youtube"
    assert result.external_id == "dQw4w9WgXcQ"
    assert result.title == "Rick Astley - Never Gonna Give You Up"
    assert result.duration_seconds == 213
    assert result.uploader == "Rick Astley"
