import pytest

from setvault_core.services.crypto import Crypter


def test_encrypt_decrypt_round_trip():
    c = Crypter(secret_key="a" * 48)
    blob = c.encrypt(b"hello")
    assert blob != b"hello"
    assert c.decrypt(blob) == b"hello"


def test_decrypt_with_wrong_key_raises():
    c1 = Crypter(secret_key="a" * 48)
    c2 = Crypter(secret_key="b" * 48)
    blob = c1.encrypt(b"hello")
    with pytest.raises(Exception):
        c2.decrypt(blob)
