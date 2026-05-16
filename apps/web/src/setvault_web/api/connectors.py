from __future__ import annotations

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.system import NotificationConnector
from setvault_core.schemas.connector import (
    ConnectorCreateIn,
    ConnectorOut,
    SmtpConfigOut,
    TestSendIn,
    TestSendOut,
)
from setvault_core.services.crypto import Crypter
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import Settings, get_settings
from setvault_web.deps import db_session, require_admin

router = APIRouter(prefix="/api/connectors", tags=["admin"])


def _to_out(c: NotificationConnector, crypter: Crypter) -> ConnectorOut:
    config = json.loads(crypter.decrypt(c.encrypted_config).decode("utf-8"))
    return ConnectorOut(
        id=str(c.id), kind=c.kind, name=c.name, enabled=c.enabled,
        scope_filter=c.scope_filter,
        config=SmtpConfigOut(
            host=config["host"], port=config["port"], encryption=config["encryption"],
            username=config.get("username"),
            password_set=bool(config.get("password")),
            from_email=config["from_email"], from_name=config["from_name"],
            reply_to=config.get("reply_to"),
        ),
    )


@router.post("", response_model=ConnectorOut, status_code=201)
async def create_connector(
    body: ConnectorCreateIn,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    crypter = Crypter(settings.secret_key)
    blob = crypter.encrypt(body.config.model_dump_json().encode("utf-8"))
    row = NotificationConnector(
        kind=body.kind, name=body.name, encrypted_config=blob,
        scope_filter=body.scope_filter, enabled=body.enabled,
    )
    session.add(row)
    await session.commit()
    return _to_out(row, crypter)


@router.get("/{connector_id}", response_model=ConnectorOut)
async def show_connector(
    connector_id: uuid.UUID,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    row = await session.get(NotificationConnector, connector_id)
    if row is None:
        raise HTTPException(status_code=404, detail="not found")
    return _to_out(row, Crypter(settings.secret_key))


@router.post("/{connector_id}/test-send", response_model=TestSendOut)
async def test_send(
    connector_id: uuid.UUID,
    body: TestSendIn,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(require_admin)],
):
    row = await session.get(NotificationConnector, connector_id)
    if row is None or row.kind != "smtp":
        raise HTTPException(status_code=404, detail="smtp connector not found")
    config = json.loads(
        Crypter(settings.secret_key).decrypt(row.encrypted_config).decode("utf-8")
    )
    if body.dry_run:
        return TestSendOut(accepted=True, dry_run=True)
    try:
        from setvault_core.jobs.email import send_email_sync
        send_email_sync(
            config=config, to=body.to,
            subject="SetVault test message",
            text="If you can read this, SMTP works.\n",
        )
        return TestSendOut(accepted=True, dry_run=False)
    except Exception as exc:
        return TestSendOut(accepted=False, dry_run=False, error=str(exc))
