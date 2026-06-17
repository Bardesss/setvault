from __future__ import annotations

import httpx
import respx
from setvault_core.services.signed_urls import sign_image_url
from setvault_web.api.images import build_proxied_image_url
from setvault_web.config import get_settings

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
REMOTE = "https://i.ytimg.com/vi/abc123/hqdefault.jpg"


def _proxy_path_for(url: str) -> str:
    """Build a validly-signed proxy path for an arbitrary url (test helper)."""
    sig, exp = sign_image_url(secret_key=get_settings().secret_key, url=url)
    from urllib.parse import quote
    return f"/api/images/proxy?url={quote(url, safe='')}&exp={exp}&sig={sig}"


@respx.mock
async def test_proxies_a_signed_image(authed_admin_client, monkeypatch):
    # Keep the test hermetic: skip the real-DNS SSRF guard for this public host
    # (the SSRF guard itself is covered by test_blocks_ssrf_to_private_host).
    monkeypatch.setattr("setvault_web.api.images._is_blocked_host", lambda h: False)
    respx.get(REMOTE).mock(
        return_value=httpx.Response(200, content=PNG, headers={"content-type": "image/png"})
    )
    r = await authed_admin_client.get(build_proxied_image_url(REMOTE))
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")
    assert r.content == PNG


async def test_rejects_bad_signature(authed_admin_client):
    from urllib.parse import quote
    bad = f"/api/images/proxy?url={quote(REMOTE, safe='')}&exp=9999999999&sig=forged"
    r = await authed_admin_client.get(bad)
    assert r.status_code == 401


async def test_requires_authentication(client):
    r = await client.get(build_proxied_image_url(REMOTE))
    assert r.status_code == 401


@respx.mock
async def test_rejects_non_image_upstream(authed_admin_client, monkeypatch):
    monkeypatch.setattr("setvault_web.api.images._is_blocked_host", lambda h: False)
    respx.get(REMOTE).mock(
        return_value=httpx.Response(
            200, content=b"<html>nope", headers={"content-type": "text/html"}
        )
    )
    r = await authed_admin_client.get(build_proxied_image_url(REMOTE))
    assert r.status_code == 502


async def test_blocks_ssrf_to_private_host(authed_admin_client):
    # A signed URL pointing at a link-local metadata address must still be
    # refused by the proxy's IP guard (defence-in-depth beyond signing).
    meta = "http://169.254.169.254/latest/meta-data/"
    r = await authed_admin_client.get(_proxy_path_for(meta))
    assert r.status_code == 400


def test_build_proxied_image_url_passthrough_for_empty():
    assert build_proxied_image_url(None) is None
    assert build_proxied_image_url("") is None
