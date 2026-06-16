"""Unit tests for the CSP inline-script hashing that unblocks SvelteKit.

The bundled image serves SvelteKit's ``adapter-static`` output, whose
``index.html`` contains an inline bootstrap ``<script>``. The strict
``script-src 'self'`` CSP blocks inline scripts, so without the script's
SHA-256 in ``script-src`` the app never hydrates (blank page). These tests
pin the hash computation and its injection into the CSP, with no DB needed.
"""
from __future__ import annotations

import base64
import hashlib

from setvault_web.middleware.security_headers import (
    SecurityHeadersMiddleware,
    _build_csp,
    compute_inline_script_hashes,
)


def _sha256_token(body: bytes) -> str:
    return "sha256-" + base64.b64encode(hashlib.sha256(body).digest()).decode("ascii")


def test_hashes_inline_script_exact_bytes():
    body = b'\n  const a = 1;\n  start(a);\n'
    html = b"<!doctype html><html><body>x" + b"<script>" + body + b"</script></body></html>"
    assert compute_inline_script_hashes(html) == [_sha256_token(body)]


def test_skips_external_scripts():
    html = b'<script src="/_app/start.js"></script>'
    assert compute_inline_script_hashes(html) == []


def test_handles_attributes_on_inline_script_and_dedupes():
    body = b'console.log(1)'
    # Same content twice + an inline module script: hash is over content only,
    # so the two identical bodies collapse to a single token.
    html = (
        b'<script type="module">' + body + b"</script>"
        b"<script>" + body + b"</script>"
    )
    assert compute_inline_script_hashes(html) == [_sha256_token(body)]


def test_placeholder_shell_has_no_inline_scripts():
    # The source-controlled placeholder index.html must yield no hashes, so the
    # CSP stays exactly `script-src 'self'` in dev/source checkouts.
    html = b"<!doctype html><html><head><title>SetVault</title></head>"
    html += b"<body>SetVault shell</body></html>"
    assert compute_inline_script_hashes(html) == []


def test_build_csp_injects_hashes_into_script_src():
    token = _sha256_token(b"x")
    csp = _build_csp("'none'", [token])
    assert f"script-src 'self' '{token}'" in csp
    # Unrelated directives are untouched.
    assert "frame-ancestors 'none'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp


def test_build_csp_without_hashes_is_strict_self_only():
    csp = _build_csp("'none'", [])
    assert "script-src 'self';" in csp
    assert "sha256-" not in csp


def test_middleware_bakes_hashes_into_both_default_and_embed():
    token = _sha256_token(b"x")
    mw = SecurityHeadersMiddleware(app=None, script_hashes=[token])
    assert f"'{token}'" in mw._default_csp.decode("latin-1")
    assert f"'{token}'" in mw._embed_csp.decode("latin-1")
    # Frame policy still differs between the two.
    assert "frame-ancestors 'none'" in mw._default_csp.decode("latin-1")
    assert "frame-ancestors *" in mw._embed_csp.decode("latin-1")
