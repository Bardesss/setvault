import os
import uuid

# Settings.base_url has no default (fail-closed for the Secure-cookie logic), so
# tests must supply a canonical origin before get_settings() is first cached.
os.environ.setdefault("BASE_URL", "http://localhost:1970")

# Use NullPool for the shared engine in this suite: ~17 autouse fixtures each
# call init_engine() per test, and a real pool leaves idle asyncpg connections
# lingering until GC — enough to exhaust CI Postgres's default max_connections
# (100). NullPool releases connections immediately. Must be set before the first
# create_async_engine() call. Production never sets this, keeping its real pool.
os.environ.setdefault("SETVAULT_DB_NULLPOOL", "1")

import pytest
from httpx import ASGITransport, AsyncClient
from setvault_core.db import init_engine, session_factory
from setvault_core.models.api_token import ApiToken
from setvault_core.models.catalog import (
    Artist,
    LiveSet,
    MediaRoot,
    Party,
    Series,
    Tag,
    Venue,
)
from setvault_core.models.enrichment import ProviderConfig, ProviderResponse, ResolveJob
from setvault_core.models.identity import EmailToken, User
from setvault_core.models.ingest_sources import IngestSourceState
from setvault_core.models.library_webhook import LibraryWebhook
from setvault_core.models.system import AuditEvent, NotificationConnector
from setvault_core.models.tracklist import (
    Label,
    Release,
    Track,
    TracklistEntry,
    TracklistImportJob,
)
from setvault_core.models.url_rip import RipJob
from setvault_core.models.watch_folder import UnmatchedFile, WatchFolder
from setvault_core.services.passwords import hash_password
from sqlalchemy import delete, select


@pytest.fixture(autouse=True)
async def _dispose_engine_between_tests():
    """Dispose the SQLAlchemy engine after each test so its connection pool
    doesn't leak across pytest-asyncio's per-test event loops.

    pytest-asyncio runs each async test in a fresh event loop. The
    ``setvault_core.db`` module caches a singleton AsyncEngine; its pool
    holds asyncpg connections bound to whatever loop they were opened in.
    Without explicit disposal, the next test's loop receives stale
    connections on checkout and trips ``pool_pre_ping`` with
    ``Future ... attached to a different loop`` errors — surfacing as
    sporadic ``InternalClientError: got result for unknown protocol state``
    on whichever test happens to run after a comments / mention test.

    Defined first among the autouse fixtures so it teardowns LAST — after
    all other cleanup fixtures have finished using the engine. Setup is a
    no-op; the next ``init_engine`` call inside the cleanup fixtures
    recreates the engine for the new loop.
    """
    yield
    import setvault_core.db as _db_module
    if _db_module._engine is not None:
        try:
            await _db_module._engine.dispose()
        except Exception:
            # Best-effort: even if dispose raises, the next init_engine
            # call overwrites _engine anyway.
            pass


@pytest.fixture(autouse=True)
async def _reset_rate_limit():
    import setvault_web.rate_limit as _rl
    from redis.asyncio import Redis
    from setvault_web.config import get_settings

    # Reset the module-level singleton so each test gets a fresh connection
    # (each test runs in its own asyncio event loop; old transports are closed)
    if _rl._redis is not None:
        try:
            await _rl._redis.aclose()
        except Exception:
            pass
        _rl._redis = None

    r = Redis.from_url(get_settings().redis_url, decode_responses=True)
    keys = await r.keys("rl:*")
    if keys:
        await r.delete(*keys)
    await r.aclose()
    yield


@pytest.fixture
async def client():
    import os

    from setvault_core.db import init_engine
    from setvault_web.main import create_app

    app = create_app()
    # Override engine with test DB URL so tests never touch the docker-internal hostname
    test_db_url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    )
    init_engine(test_db_url)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="https://test", follow_redirects=False
    ) as ac:
        yield ac


@pytest.fixture
async def seeded_admin():
    init_engine(__import__("os").environ["TEST_DATABASE_URL"])
    # Idempotent: remove any stale "admin@example.test" / "admin" user that may
    # have been left behind by the dev-seed e2e endpoint (or a prior crashed
    # test run). LiveSets created by that user are cleared first to avoid the
    # ON DELETE RESTRICT on LiveSet.uploaded_by.
    async with session_factory()() as s:
        existing = (await s.execute(
            select(User).where(
                (User.email == "admin@example.test") | (User.username == "admin")
            )
        )).scalars().all()
        for prior in existing:
            await s.execute(delete(LiveSet).where(LiveSet.uploaded_by == prior.id))
            await s.delete(prior)
        await s.commit()

        user = User(
            email="admin@example.test", username="admin", display_name="Admin",
            password_hash=hash_password("hunter2hunter2"), role="admin",
        )
        s.add(user)
        await s.commit()
        user_id = user.id
        yield user
    # Re-open a session for teardown — the yielded session may be stale, and we
    # must clear LiveSets first (LiveSet.uploaded_by has ON DELETE RESTRICT).
    async with session_factory()() as s:
        await s.execute(delete(LiveSet).where(LiveSet.uploaded_by == user_id))
        row = await s.get(User, user_id)
        if row is not None:
            await s.delete(row)
        await s.commit()


@pytest.fixture
async def authed_admin_client(client, seeded_admin):
    login = await client.post("/api/auth/login",
                              json={"email": "admin@example.test", "password": "hunter2hunter2"})
    client.cookies = login.cookies
    client.headers["X-CSRF-Token"] = login.cookies["csrf_token"]
    yield client


@pytest.fixture
async def seeded_live_set(authed_admin_client, tmp_path):
    """Seed a published LiveSet with a MediaRoot; returns {slug, id}.

    Creates the MediaRoot via the public API (covers health probing) and the
    LiveSet directly via the session — no public POST /api/sets exists yet.
    Cleanup of the LiveSet/MediaRoot is handled by the autouse
    ``_cleanup_media_roots`` fixture (which wipes both tables)."""
    mr = await authed_admin_client.post("/api/media-roots", json={
        "name": "seed-primary",
        "host_path": str(tmp_path),
        "default_for_ingest": True,
        "naming_template": None,
        "max_bytes": None,
    })
    mr_id = mr.json()["id"]

    async with session_factory()() as s:
        admin = (await s.execute(
            select(User).where(User.email == "admin@example.test")
        )).scalar_one()
        live = LiveSet(
            slug=f"seeded-set-{uuid.uuid4().hex[:6]}",
            title="seeded set",
            media_root_id=uuid.UUID(mr_id),
            audio_path="originals/seed/audio.flac",
            status="published",
            source_type="upload",
            uploaded_by=admin.id,
        )
        s.add(live)
        await s.commit()
        sid = live.id
        slug = live.slug
    yield {"id": str(sid), "slug": slug}


@pytest.fixture(autouse=True)
async def _cleanup_invite_users():
    """Delete users and email_tokens created by invite tests so runs are idempotent."""
    yield
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        # Remove any users that were created via redeem (not seeded fixtures)
        # Emails used by invite tests: *@example.test (excl admin) and *@x.test
        await s.execute(
            delete(User).where(
                (User.email.like("%@example.test") & (User.username != "admin"))
                | User.email.like("%@x.test")
            )
        )
        # Remove lingering invite tokens for those domains
        await s.execute(
            delete(EmailToken).where(
                EmailToken.email.like("%@example.test")
                | EmailToken.email.like("%@x.test")
            )
        )
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_api_tokens():
    """Delete ApiToken rows so RSS-token tests can rerun. CASCADE handles
    token cleanup when test users are deleted, but admin survives across tests
    and his tokens would accumulate."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(ApiToken))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(ApiToken))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_rip_jobs():
    """Delete RipJob rows so URL-rip tests can rerun. RipJob.live_set_id has
    ondelete=CASCADE so rows tied to LiveSets get cleaned when LiveSets are
    deleted, but unattached (queued-only) rows need explicit removal."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(RipJob))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(RipJob))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_ingest_source_state():
    """Delete IngestSourceState rows so admin source-toggle tests can rerun.

    The admin PUT that toggles a source to disabled COMMITS the row; without
    this cleanup the stale (e.g. youtube, enabled=False, manually_disabled)
    row persists in the shared test DB and breaks the core ingest-source
    service tests (and reruns of these tests). Cleans both before and after
    to clear leftovers from prior sessions."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(IngestSourceState))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(IngestSourceState))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_library_webhooks():
    """Delete LibraryWebhook rows so admin-webhook tests can rerun."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(LibraryWebhook))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(LibraryWebhook))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_watch_folders():
    """Delete WatchFolder + UnmatchedFile rows so reruns stay idempotent.

    UnmatchedFile.watch_folder_id has ondelete=CASCADE so removing watch
    folders takes the matching unmatched rows too — clearing UnmatchedFile
    first is just belt-and-suspenders for any test that detaches them.
    WatchFolder.target_media_root_id is RESTRICT, so this must run BEFORE
    the media-roots cleanup."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(UnmatchedFile))
        await s.execute(delete(WatchFolder))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(UnmatchedFile))
        await s.execute(delete(WatchFolder))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_media_roots():
    """Delete LiveSet + MediaRoot rows so leftover rows don't break reruns.

    LiveSet.media_root_id has ON DELETE RESTRICT, so any LiveSet rows from the
    upload tests must be deleted first or the MediaRoot delete fails.
    """
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(LiveSet))
        await s.execute(delete(MediaRoot))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(LiveSet))
        await s.execute(delete(MediaRoot))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_notification_connectors():
    """Delete NotificationConnector rows so connector leftovers don't enable
    SMTP-send paths in unrelated tests (e.g. invite tests expect smtp_sent=False
    when no connector exists). Cleans both before and after to handle leftovers
    from prior test sessions."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(NotificationConnector))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(NotificationConnector))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_audit_events():
    """Delete AuditEvent rows so audit tests can rerun and the test DB stays tidy."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(AuditEvent))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(AuditEvent))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_provider_configs():
    """Wipe provider configs / response cache / resolve jobs between tests."""
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(ResolveJob))
        await s.execute(delete(ProviderResponse))
        await s.execute(delete(ProviderConfig))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(ResolveJob))
        await s.execute(delete(ProviderResponse))
        await s.execute(delete(ProviderConfig))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_tracklist():
    """Wipe tracklist + Track DB rows between tests so reruns stay idempotent.

    TracklistEntry / TracklistImportJob cascade off LiveSet deletes, but Track,
    Release and Label are independent and must be cleared explicitly. Order:
    entries reference tracks (SET NULL) and tracks reference releases/labels
    (SET NULL), so child rows first is safe either way — kept explicit anyway.
    """
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(TracklistEntry))
        await s.execute(delete(TracklistImportJob))
        await s.execute(delete(Track))
        await s.execute(delete(Release))
        await s.execute(delete(Label))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(TracklistEntry))
        await s.execute(delete(TracklistImportJob))
        await s.execute(delete(Track))
        await s.execute(delete(Release))
        await s.execute(delete(Label))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_engagement_3c():
    from setvault_core.models.engagement_3c import (
        Bookmark,
        Comment,
        InAppNotification,
        PrivateNote,
    )
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(InAppNotification))
        await s.execute(delete(Bookmark))
        await s.execute(delete(PrivateNote))
        await s.execute(delete(Comment))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(InAppNotification))
        await s.execute(delete(Bookmark))
        await s.execute(delete(PrivateNote))
        await s.execute(delete(Comment))
        await s.commit()


@pytest.fixture(autouse=True)
async def _cleanup_catalog():
    """Delete Party/Series/Venue/Artist/Tag rows so catalog tests can rerun.

    The catalog CRUD tests rely on unique slug constraints (see the 409 test),
    so leftover rows from a prior run would otherwise turn the create asserts
    into spurious 409s. Order matters: Party has FKs to Venue and Series, so
    delete parties first; Artist is independent. Tag rows are also cleaned so
    set-edit tests that create tags by name (e.g. "techno", "vinyl") stay
    idempotent — LiveSetTag rows cascade on Tag delete via FK.
    """
    init_engine(__import__("os").environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault",
    ))
    async with session_factory()() as s:
        await s.execute(delete(Party))
        await s.execute(delete(Series))
        await s.execute(delete(Venue))
        await s.execute(delete(Artist))
        await s.execute(delete(Tag))
        await s.commit()
    yield
    async with session_factory()() as s:
        await s.execute(delete(Party))
        await s.execute(delete(Series))
        await s.execute(delete(Venue))
        await s.execute(delete(Artist))
        await s.execute(delete(Tag))
        await s.commit()
