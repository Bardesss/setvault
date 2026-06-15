"""Unit tests for the session-cookie ``Secure`` policy.

``cookie_secure()`` derives the flag from the ``BASE_URL`` scheme so it can't
drift from the origin the app is actually served on, with
``SETVAULT_ALLOW_INSECURE_COOKIE`` as an explicit force-off override.
"""

import pytest

from setvault_web import cookies
from setvault_web.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    # get_settings() is lru_cached; clear around each test so per-test BASE_URL
    # env changes take effect and don't leak into other tests.
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _env(monkeypatch, base_url, flag=None):
    monkeypatch.setenv("BASE_URL", base_url)
    if flag is None:
        monkeypatch.delenv("SETVAULT_ALLOW_INSECURE_COOKIE", raising=False)
    else:
        monkeypatch.setenv("SETVAULT_ALLOW_INSECURE_COOKIE", flag)
    get_settings.cache_clear()


def test_https_base_url_keeps_secure(monkeypatch):
    _env(monkeypatch, "https://setvault.example.com")
    assert cookies.cookie_secure() is True


def test_http_base_url_drops_secure(monkeypatch):
    # VPN/LAN-only: a Secure cookie would be silently dropped on a plain-HTTP
    # origin, so login must work without it.
    _env(monkeypatch, "http://10.0.0.5:1970")
    assert cookies.cookie_secure() is False


def test_https_is_case_insensitive(monkeypatch):
    _env(monkeypatch, "HTTPS://SetVault.example.com")
    assert cookies.cookie_secure() is True


@pytest.mark.parametrize("flag", ["1", "true", "yes", "TRUE", "Yes"])
def test_flag_forces_off_even_with_https(monkeypatch, flag):
    _env(monkeypatch, "https://setvault.example.com", flag=flag)
    assert cookies.cookie_secure() is False


def test_flag_off_value_does_not_force(monkeypatch):
    # An explicit falsey/other value must not override scheme detection.
    _env(monkeypatch, "https://setvault.example.com", flag="0")
    assert cookies.cookie_secure() is True


@pytest.mark.parametrize("base_url", ["", "   ", "ftp://nope", "setvault.example.com"])
def test_unset_or_malformed_base_url_fails_closed(monkeypatch, base_url):
    # A forgotten/garbage BASE_URL must keep Secure on so a public deployment
    # never silently downgrades the cookie.
    _env(monkeypatch, base_url)
    assert cookies.cookie_secure() is True
