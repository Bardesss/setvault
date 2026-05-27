"""Notification dispatcher — extends Phase 2B notification-connector framework
with in-app delivery and the new `mention` / `comment_reply` kinds.

NOTE: Email delivery is intentionally NOT wired here yet. The enqueue helper
lives in `apps/web/services/notifications.py` (it depends on the web Settings
object for Redis URL) which packages/core can't import. A follow-up will
either move enqueue_email into packages/core or have the API layer call it
separately after dispatch. For now, only in-app InAppNotification rows are
written — the notification bell + dropdown in the frontend (C13) is the
primary delivery channel for the small private group target.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.engagement_3c import InAppNotification
from setvault_core.models.identity import NotificationPreference

if TYPE_CHECKING:
    from setvault_core.models.catalog import LiveSet
    from setvault_core.models.engagement_3c import Comment
    from setvault_core.models.identity import User


async def _preference_for(
    session: AsyncSession, user_id: uuid.UUID, kind: str,
) -> NotificationPreference | None:
    """Returns the user's NotificationPreference for this kind, or None (default: both)."""
    return (await session.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == user_id,
            NotificationPreference.kind == kind,
        )
    )).scalar_one_or_none()


async def _deliver_in_app(
    session: AsyncSession, *, user_id: uuid.UUID, kind: str,
    subject_type: str, subject_id: uuid.UUID, payload: dict,
) -> None:
    n = InAppNotification(
        user_id=user_id, kind=kind, subject_type=subject_type,
        subject_id=subject_id, payload=payload, created_at=datetime.now(UTC),
    )
    session.add(n)
    await session.flush()


async def dispatch_for_comment(
    session: AsyncSession,
    comment: Comment,
    *, author: User, live_set: LiveSet,
) -> None:
    # Build the recipient set: mentions + parent author (excluding the author themselves)
    recipients: set[uuid.UUID] = set(comment.mentions_user_ids or [])
    kind_for: dict[uuid.UUID, str] = {uid: "mention" for uid in recipients}
    if comment.parent_id:
        from setvault_core.models.engagement_3c import Comment as CommentModel
        parent = await session.get(CommentModel, comment.parent_id)
        if parent and parent.user_id != author.id:
            recipients.add(parent.user_id)
            kind_for.setdefault(parent.user_id, "comment_reply")
    recipients.discard(author.id)
    for uid in recipients:
        kind = kind_for[uid]
        pref = await _preference_for(session, uid, kind)
        channel = pref.channel if pref else "both"
        payload = {
            "set_slug": live_set.slug,
            "set_title": live_set.title,
            "comment_id": str(comment.id),
            "author_username": author.username,
            "excerpt": comment.body[:200],
        }
        if channel in ("in_app", "both"):
            await _deliver_in_app(
                session, user_id=uid, kind=kind,
                subject_type="comment", subject_id=comment.id, payload=payload,
            )
        # Email delivery: deferred — see module docstring.
