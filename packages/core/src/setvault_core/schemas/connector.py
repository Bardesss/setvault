from __future__ import annotations

from typing import Annotated, Literal

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel, Field


def _validate_email_permissive(value: str) -> str:
    """Validate an email but allow reserved TLDs (e.g. .test, .example) used in tests."""
    try:
        result = validate_email(value, check_deliverability=False, test_environment=True)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc
    return result.normalized


PermissiveEmail = Annotated[str, AfterValidator(_validate_email_permissive)]


class SmtpConfigIn(BaseModel):
    host: str
    port: int = Field(ge=1, le=65535)
    encryption: Literal["starttls", "ssl", "none"]
    username: str | None = None
    password: str | None = None
    from_email: PermissiveEmail
    from_name: str
    reply_to: PermissiveEmail | None = None


class SmtpConfigOut(BaseModel):
    host: str
    port: int
    encryption: Literal["starttls", "ssl", "none"]
    username: str | None
    password_set: bool
    from_email: str
    from_name: str
    reply_to: str | None


class ConnectorCreateIn(BaseModel):
    kind: Literal["smtp"]
    name: str
    config: SmtpConfigIn
    scope_filter: dict = Field(default_factory=lambda: {"kinds": ["*"]})
    enabled: bool = True


class ConnectorOut(BaseModel):
    id: str
    kind: str
    name: str
    enabled: bool
    scope_filter: dict
    config: SmtpConfigOut


class TestSendIn(BaseModel):
    to: PermissiveEmail
    dry_run: bool = False


class TestSendOut(BaseModel):
    accepted: bool
    dry_run: bool
    error: str | None = None
