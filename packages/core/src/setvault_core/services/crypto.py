from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet


def _key_from_secret(secret_key: str) -> bytes:
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class Crypter:
    def __init__(self, secret_key: str) -> None:
        if len(secret_key) < 16:
            raise ValueError("SECRET_KEY must be at least 16 chars (recommended: 48+)")
        self._fernet = Fernet(_key_from_secret(secret_key))

    def encrypt(self, payload: bytes) -> bytes:
        return self._fernet.encrypt(payload)

    def decrypt(self, token: bytes) -> bytes:
        return self._fernet.decrypt(token)
