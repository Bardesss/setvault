from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import timedelta

from itsdangerous import BadSignature, TimestampSigner

SESSION_COOKIE = "session"
SESSION_TTL = timedelta(days=30)


@dataclass
class SessionData:
    user_id: str


class SessionSigner:
    def __init__(self, secret_key: str) -> None:
        self._signer = TimestampSigner(secret_key, salt="setvault.session")

    def issue(self, user_id: str) -> str:
        nonce = secrets.token_urlsafe(16)
        payload = f"{user_id}:{nonce}"
        return self._signer.sign(payload).decode("ascii")

    def read(self, raw: str) -> SessionData | None:
        try:
            value = self._signer.unsign(
                raw, max_age=int(SESSION_TTL.total_seconds()),
            ).decode("ascii")
        except BadSignature:
            return None
        user_id, _ = value.split(":", 1)
        return SessionData(user_id=user_id)
