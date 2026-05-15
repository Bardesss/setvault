from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Tuned per OWASP 2024 guidance for argon2id (m=64 MiB, t=3, p=4)
_hasher = PasswordHasher(
    time_cost=3, memory_cost=64 * 1024, parallelism=4, hash_len=32, salt_len=16,
)


def hash_password(plaintext: str) -> str:
    return _hasher.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, plaintext)
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(hashed: str) -> bool:
    try:
        return _hasher.check_needs_rehash(hashed)
    except InvalidHashError:
        return True
