from setvault_core.models.catalog import LiveSet, MediaRoot
from setvault_core.models.engagement import ActivityEvent, Favorite, UserSetState
from setvault_core.models.identity import User
from setvault_core.models.system import AuditEvent, NotificationConnector


async def test_create_engagement_rows(session):
    user = User(email="u@x.test", username="u", display_name="u", password_hash="x", role="user")
    root = MediaRoot(name="r", host_path="/srv/r", default_for_ingest=True, enabled=True)
    session.add_all([user, root])
    await session.flush()
    live = LiveSet(slug="s", title="Set", media_root_id=root.id,
                   audio_path="originals/x", uploaded_by=user.id, source_type="upload")
    session.add(live)
    await session.flush()

    session.add_all([
        UserSetState(user_id=user.id, live_set_id=live.id, position_seconds=42, completed=False),
        Favorite(user_id=user.id, live_set_id=live.id),
        ActivityEvent(user_id=user.id, kind="set.published",
                      subject_type="LiveSet", subject_id=live.id, payload={}),
    ])
    await session.flush()


async def test_notification_connector_smtp(session):
    c = NotificationConnector(kind="smtp", name="default", enabled=True,
                              encrypted_config=b"\x00" * 16,
                              scope_filter={"kinds": ["*"]})
    session.add(c)
    await session.flush()
    assert c.id is not None


async def test_audit_event_minimal(session):
    e = AuditEvent(actor_kind="system", action="boot.completed", before=None, after=None)
    session.add(e)
    await session.flush()
