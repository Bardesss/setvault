"""Tests for storage.place_audio_file — hardlink + atomic-move placement."""
from __future__ import annotations

from pathlib import Path

import pytest
from setvault_core.services.storage import place_audio_file


def _write(path: Path, content: bytes = b"hello") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_same_fs_uses_hardlink(tmp_path: Path):
    src = tmp_path / "src" / "audio.opus"
    dst = tmp_path / "dst" / "audio.opus"
    _write(src, b"x" * 64)

    mode = place_audio_file(src, dst)

    assert mode == "hardlinked"
    assert dst.exists()
    assert dst.read_bytes() == b"x" * 64
    # Hardlink semantics: both names refer to the same inode
    assert src.stat().st_ino == dst.stat().st_ino


def test_creates_destination_parent_dirs(tmp_path: Path):
    src = tmp_path / "audio.opus"
    dst = tmp_path / "a" / "b" / "c" / "audio.opus"
    _write(src)

    place_audio_file(src, dst)

    assert dst.exists()


def test_missing_source_raises(tmp_path: Path):
    src = tmp_path / "nope.opus"
    dst = tmp_path / "dst.opus"
    with pytest.raises(FileNotFoundError):
        place_audio_file(src, dst)


def test_overwrites_stale_dst_on_hardlink(tmp_path: Path):
    src = tmp_path / "audio.opus"
    dst = tmp_path / "dst.opus"
    _write(src, b"new")
    _write(dst, b"old")

    mode = place_audio_file(src, dst)

    assert mode == "hardlinked"
    assert dst.read_bytes() == b"new"


def test_cross_fs_falls_back_to_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """If hardlink-time stat reports different st_dev values, we copy + rename."""
    src = tmp_path / "audio.opus"
    dst = tmp_path / "dst" / "audio.opus"
    _write(src, b"y" * 32)

    # Force os.link to never be tried by making the device-IDs look different.
    real_stat = Path.stat

    def fake_stat(self, *args, **kw):
        st = real_stat(self, *args, **kw)
        if self == src:
            # Pretend src lives on device 999
            class _Stat:
                pass
            for attr in dir(st):
                if not attr.startswith("__"):
                    try:
                        setattr(_Stat, attr, getattr(st, attr))
                    except (AttributeError, TypeError):
                        pass
            _Stat.st_dev = 999
            _Stat.st_ino = st.st_ino
            _Stat.st_size = st.st_size
            return _Stat
        return st

    monkeypatch.setattr(Path, "stat", fake_stat)

    mode = place_audio_file(src, dst)

    assert mode == "copied"
    assert dst.exists()
    assert dst.read_bytes() == b"y" * 32
    # No leftover .tmp file
    assert not list(dst.parent.glob("*.tmp"))
    # Different inodes (copy, not hardlink)
    real_src_ino = real_stat(src).st_ino
    real_dst_ino = real_stat(dst).st_ino
    assert real_src_ino != real_dst_ino
