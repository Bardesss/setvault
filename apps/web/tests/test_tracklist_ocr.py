import base64
from io import BytesIO

import pytest
from PIL import Image


def _white_png_b64() -> str:
    buf = BytesIO()
    Image.new("L", (32, 32), color=255).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.mark.asyncio
async def test_ocr_import_returns_parsed(monkeypatch, authed_admin_client, seeded_live_set):
    # Stub pytesseract so CI doesn't need the binary installed
    import pytesseract
    monkeypatch.setattr(
        pytesseract, "image_to_string",
        lambda img: "0:00 OCR Artist - First Track\n5:30 Second - Track",
    )
    slug = seeded_live_set["slug"]
    r = await authed_admin_client.post(
        f"/api/sets/{slug}/tracklist/import",
        json={"kind": "ocr", "payload": {"image_b64": _white_png_b64()}},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "succeeded"
    assert len(body["parsed"]) == 2
    assert body["parsed"][0]["raw_label"] == "OCR Artist - First Track"


@pytest.mark.asyncio
async def test_ocr_import_rejects_bad_b64(authed_admin_client, seeded_live_set):
    r = await authed_admin_client.post(
        f"/api/sets/{seeded_live_set['slug']}/tracklist/import",
        json={"kind": "ocr", "payload": {"image_b64": "@@@@"}},
    )
    assert r.status_code == 400
