"""Unit tests for the watchdog event handler.

The full ``run_watcher`` loop is integration-level (needs Redis + a real
filesystem observer + a Postgres-backed WatchFolder set). The pieces that
are pure logic — audio-file filtering and event-to-enqueue translation —
are tested here.
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

from setvault_core.services.watcher import (
    _is_audio_file,
    _WatchFolderHandler,
)


def test_audio_file_filter():
    assert _is_audio_file("/x/y/file.opus") is True
    assert _is_audio_file("/x/file.FLAC") is True   # case-insensitive
    assert _is_audio_file("/x/file.mp3") is True
    assert _is_audio_file("/x/readme.txt") is False
    assert _is_audio_file("/x/no_ext") is False
    assert _is_audio_file("/x/file.opus.tmp") is False  # not audio


def test_created_event_enqueues_audio_file():
    wf_id = uuid.uuid4()
    enqueue = MagicMock()
    handler = _WatchFolderHandler(watch_folder_id=wf_id, enqueue=enqueue)

    evt = MagicMock(spec=[])
    evt.is_directory = False
    evt.src_path = "/srv/incoming/track.flac"
    handler.on_created(evt)

    enqueue.assert_called_once_with(wf_id, "/srv/incoming/track.flac")


def test_created_event_skips_directories():
    enqueue = MagicMock()
    handler = _WatchFolderHandler(watch_folder_id=uuid.uuid4(), enqueue=enqueue)

    evt = MagicMock(spec=[])
    evt.is_directory = True
    evt.src_path = "/srv/incoming/subdir"
    handler.on_created(evt)

    enqueue.assert_not_called()


def test_created_event_skips_non_audio():
    enqueue = MagicMock()
    handler = _WatchFolderHandler(watch_folder_id=uuid.uuid4(), enqueue=enqueue)

    evt = MagicMock(spec=[])
    evt.is_directory = False
    evt.src_path = "/srv/incoming/notes.txt"
    handler.on_created(evt)

    enqueue.assert_not_called()


def test_moved_event_uses_dest_path():
    """A file MOVED INTO the watched tree should enqueue against its new path."""
    wf_id = uuid.uuid4()
    enqueue = MagicMock()
    handler = _WatchFolderHandler(watch_folder_id=wf_id, enqueue=enqueue)

    evt = MagicMock(spec=[])
    evt.is_directory = False
    evt.dest_path = "/srv/incoming/moved.opus"
    handler.on_moved(evt)

    enqueue.assert_called_once_with(wf_id, "/srv/incoming/moved.opus")
