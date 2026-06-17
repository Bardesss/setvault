from __future__ import annotations

import time

from setvault_core.services.signed_urls import (
    sign_image_url,
    sign_stream_url,
    verify_image_sig,
    verify_stream_sig,
)

KEY = "test-secret-XXXXXXXXXXXXXXXX"
IMG = "https://i.ytimg.com/vi/abc123/hqdefault.jpg"


def test_round_trip_signs_and_verifies():
    sig, exp = sign_stream_url(secret_key=KEY, slug="foo")
    assert verify_stream_sig(secret_key=KEY, slug="foo", exp=exp, sig=sig) is True


def test_signature_is_slug_bound():
    """A signature for slug A must not verify against slug B."""
    sig, exp = sign_stream_url(secret_key=KEY, slug="foo")
    assert verify_stream_sig(secret_key=KEY, slug="bar", exp=exp, sig=sig) is False


def test_signature_is_key_bound():
    """A different secret key must invalidate the signature."""
    sig, exp = sign_stream_url(secret_key=KEY, slug="foo")
    assert verify_stream_sig(
        secret_key="different-secret-XXXXXXXX",
        slug="foo", exp=exp, sig=sig,
    ) is False


def test_expired_signature_rejected():
    """exp in the past must reject even if the signature is valid for that exp."""
    past = int(time.time()) - 5
    sig, _ = sign_stream_url(secret_key=KEY, slug="foo", exp=past)
    assert verify_stream_sig(secret_key=KEY, slug="foo", exp=past, sig=sig) is False


def test_tampered_exp_rejected():
    """Bumping exp in the URL without re-signing must reject."""
    sig, exp = sign_stream_url(secret_key=KEY, slug="foo")
    assert verify_stream_sig(
        secret_key=KEY, slug="foo", exp=exp + 1000, sig=sig,
    ) is False


def test_empty_inputs_rejected():
    assert verify_stream_sig(secret_key=KEY, slug="", exp=int(time.time()) + 60, sig="x") is False
    assert verify_stream_sig(secret_key=KEY, slug="foo", exp=int(time.time()) + 60, sig="") is False


def test_default_ttl_is_in_the_future():
    """The default TTL puts exp comfortably in the future."""
    now = int(time.time())
    _, exp = sign_stream_url(secret_key=KEY, slug="foo")
    assert exp > now + 1000  # at least ~17min in the future


# --- image-proxy signing -------------------------------------------------

def test_image_round_trip_signs_and_verifies():
    sig, exp = sign_image_url(secret_key=KEY, url=IMG)
    assert verify_image_sig(secret_key=KEY, url=IMG, exp=exp, sig=sig) is True


def test_image_signature_is_url_bound():
    sig, exp = sign_image_url(secret_key=KEY, url=IMG)
    other = "https://i.ytimg.com/vi/evil/hqdefault.jpg"
    assert verify_image_sig(secret_key=KEY, url=other, exp=exp, sig=sig) is False


def test_image_signature_is_key_bound():
    sig, exp = sign_image_url(secret_key=KEY, url=IMG)
    assert verify_image_sig(
        secret_key="different-secret-XXXXXXXX", url=IMG, exp=exp, sig=sig,
    ) is False


def test_image_expired_signature_rejected():
    past = int(time.time()) - 5
    sig, _ = sign_image_url(secret_key=KEY, url=IMG, exp=past)
    assert verify_image_sig(secret_key=KEY, url=IMG, exp=past, sig=sig) is False


def test_image_tampered_exp_rejected():
    sig, exp = sign_image_url(secret_key=KEY, url=IMG)
    assert verify_image_sig(secret_key=KEY, url=IMG, exp=exp + 1000, sig=sig) is False


def test_image_empty_inputs_rejected():
    future = int(time.time()) + 60
    assert verify_image_sig(secret_key=KEY, url="", exp=future, sig="x") is False
    assert verify_image_sig(secret_key=KEY, url=IMG, exp=future, sig="") is False


def test_image_and_stream_sigs_do_not_cross_verify():
    """Domain separation: a stream sig must not verify as an image sig for the
    same string, and vice-versa."""
    s_sig, exp = sign_stream_url(secret_key=KEY, slug=IMG)
    assert verify_image_sig(secret_key=KEY, url=IMG, exp=exp, sig=s_sig) is False
