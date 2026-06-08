from __future__ import annotations

import os

import pytest
from setvault_core.db import init_engine, session_factory
from setvault_core.models.identity import User
from setvault_core.services.passwords import hash_password, verify_password
from setvault_web.create_admin import CreateAdminError, create_or_promote_admin
from sqlalchemy import delete, select

BOOTSTRAP_EMAIL = "bootstrap-admin@example.test"
STRONG_PASSWORD = "correct-horse-battery"  # >= 12 chars


def _db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    )


@pytest.fixture
async def db_session():
    init_engine(_db_url())
    async with session_factory()() as s:
        # Idempotent: drop any leftover bootstrap user from a prior run.
        await s.execute(delete(User).where(User.email == BOOTSTRAP_EMAIL))
        await s.commit()
        yield s
    async with session_factory()() as s:
        await s.execute(delete(User).where(User.email == BOOTSTRAP_EMAIL))
        await s.commit()


async def _get(session, email: str) -> User | None:
    return (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()


async def test_creates_fresh_admin(db_session):
    user, action = await create_or_promote_admin(
        db_session, BOOTSTRAP_EMAIL, STRONG_PASSWORD
    )
    assert action == "created"
    assert user.role == "admin"
    assert user.email_verified_at is not None
    # username defaults to the email local-part
    assert user.username == "bootstrap-admin"
    assert user.display_name == "bootstrap-admin"

    row = await _get(db_session, BOOTSTRAP_EMAIL)
    assert row is not None
    assert row.role == "admin"
    assert row.password_hash and verify_password(STRONG_PASSWORD, row.password_hash)


async def test_username_and_display_name_overrides(db_session):
    user, action = await create_or_promote_admin(
        db_session,
        BOOTSTRAP_EMAIL,
        STRONG_PASSWORD,
        username="rootadmin",
        display_name="Root Admin",
    )
    assert action == "created"
    assert user.username == "rootadmin"
    assert user.display_name == "Root Admin"


async def test_idempotent_second_run_is_noop(db_session):
    _, first = await create_or_promote_admin(
        db_session, BOOTSTRAP_EMAIL, STRONG_PASSWORD
    )
    assert first == "created"

    _, second = await create_or_promote_admin(
        db_session, BOOTSTRAP_EMAIL, STRONG_PASSWORD
    )
    assert second == "exists"

    rows = (
        await db_session.execute(select(User).where(User.email == BOOTSTRAP_EMAIL))
    ).scalars().all()
    assert len(rows) == 1


async def test_promotes_existing_non_admin(db_session):
    db_session.add(
        User(
            email=BOOTSTRAP_EMAIL,
            username="bootstrap-admin",
            display_name="Bootstrap",
            password_hash=hash_password(STRONG_PASSWORD),
            role="user",
        )
    )
    await db_session.commit()

    user, action = await create_or_promote_admin(
        db_session, BOOTSTRAP_EMAIL, STRONG_PASSWORD
    )
    assert action == "promoted"
    assert user.role == "admin"

    row = await _get(db_session, BOOTSTRAP_EMAIL)
    assert row is not None and row.role == "admin"


async def test_missing_email_raises(db_session):
    with pytest.raises(CreateAdminError):
        await create_or_promote_admin(db_session, "", STRONG_PASSWORD)


async def test_missing_password_raises(db_session):
    with pytest.raises(CreateAdminError):
        await create_or_promote_admin(db_session, BOOTSTRAP_EMAIL, "")


async def test_short_password_raises(db_session):
    with pytest.raises(CreateAdminError):
        await create_or_promote_admin(db_session, BOOTSTRAP_EMAIL, "short")
