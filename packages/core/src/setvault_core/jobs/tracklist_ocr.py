"""OCR for tracklist images via Tesseract.

Caller supplies a local image path; we run pytesseract and hand the result
to the regex paste parser. No DB interaction here.
"""
from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image

from setvault_core.services.tracklist_parse import ParsedEntry, parse_tracklist_text


class OcrFailed(RuntimeError):
    pass


def run_ocr(image_path: Path) -> str:
    try:
        with Image.open(image_path) as img:
            return pytesseract.image_to_string(img)
    except Exception as exc:
        raise OcrFailed(f"tesseract failed: {exc}") from exc


def ocr_to_entries(image_path: Path) -> list[ParsedEntry]:
    return parse_tracklist_text(run_ocr(image_path))
