"""Per-user RSS / podcast feeds.

Each feed is keyed by an ApiToken with the ``rss`` scope. The path-embedded
token authenticates without a session cookie, so podcast apps can subscribe.

Three scopes:
  - favorites: sets the user marked as favorites
  - recent: 30 most recently published sets in the library
  - everything: every published set, newest-first by date then created_at
"""
from __future__ import annotations

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from setvault_core.models.api_token import ApiToken
from setvault_core.models.catalog import LiveSet
from setvault_core.models.engagement import Favorite
from setvault_core.models.identity import User
from setvault_core.models.tracklist import TracklistEntry
from setvault_core.services.api_tokens import resolve_api_token, touch_last_used
from setvault_core.services.audit import log as audit_log
from setvault_core.services.feeds import build_feed
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.config import Settings, get_settings
from setvault_web.deps import db_session
from setvault_web.rate_limit import hit as _ratelimit_hit

logger = logging.getLogger(__name__)
router = APIRouter(tags=["feeds"])

FeedKind = Literal["favorites", "recent", "everything"]

_FEED_LIMIT_PER_HOUR = 60


async def _enforce_feed_rate_limit(token: ApiToken) -> None:
    count = await _ratelimit_hit(
        f"feed:{token.id}", limit=_FEED_LIMIT_PER_HOUR, window_seconds=3600,
    )
    if count > _FEED_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=429, detail="feed rate limited",
            headers={"Retry-After": "3600"},
        )


async def _resolve_rss_token(
    session: AsyncSession, token_plaintext: str,
) -> tuple[User, ApiToken]:
    """Return (user, token_row) for a valid RSS-scoped token. 404 otherwise.

    404 (not 401) deliberately — we never want to leak whether a given token
    string was once valid or what scopes a token carries.
    """
    row = await resolve_api_token(
        session, token_plaintext=token_plaintext, required_scope="rss",
    )
    if row is None:
        raise HTTPException(status_code=404)
    user = await session.get(User, row.user_id)
    if user is None or user.disabled_at is not None:
        raise HTTPException(status_code=404)
    return user, row


async def _items_for(
    session: AsyncSession, *, user: User, kind: FeedKind,
    limit: int, offset: int,
) -> list[tuple[LiveSet, list[TracklistEntry]]]:
    if kind == "favorites":
        q = (select(LiveSet)
             .join(Favorite, Favorite.live_set_id == LiveSet.id)
             .where(
                 Favorite.user_id == user.id,
                 LiveSet.deleted_at.is_(None),
                 LiveSet.status == "published",
             )
             .order_by(Favorite.created_at.desc())
             .limit(limit).offset(offset))
    elif kind == "recent":
        q = (select(LiveSet)
             .where(LiveSet.deleted_at.is_(None), LiveSet.status == "published")
             .order_by(LiveSet.created_at.desc())
             .limit(limit).offset(offset))
    else:  # everything
        q = (select(LiveSet)
             .where(LiveSet.deleted_at.is_(None), LiveSet.status == "published")
             .order_by(LiveSet.date.desc().nullslast(),
                       LiveSet.created_at.desc())
             .limit(limit).offset(offset))
    sets = (await session.execute(q)).scalars().all()
    if not sets:
        return []
    set_ids = [s.id for s in sets]
    entry_rows = (await session.execute(
        select(TracklistEntry)
        .where(TracklistEntry.live_set_id.in_(set_ids))
        .order_by(TracklistEntry.live_set_id, TracklistEntry.position)
    )).scalars().all()
    by_set: dict = {sid: [] for sid in set_ids}
    for ent in entry_rows:
        by_set[ent.live_set_id].append(ent)
    return [(s, by_set.get(s.id, [])) for s in sets]


@router.get("/api/feed/{kind}/{token}.xml")
async def feed(
    kind: FeedKind,
    token: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    page: int = 1,
):
    user, api_token = await _resolve_rss_token(session, token)
    await _enforce_feed_rate_limit(api_token)

    page_size = 30 if kind == "recent" else 50
    offset = max(0, (page - 1) * page_size)
    items = await _items_for(
        session, user=user, kind=kind, limit=page_size, offset=offset,
    )

    base_url = str(request.base_url).rstrip("/")
    title_for_kind = {
        "favorites": f"SetVault favorites - {user.display_name}",
        "recent": "SetVault recent sets",
        "everything": f"SetVault - {user.display_name}",
    }[kind]
    xml = build_feed(
        title=title_for_kind,
        self_link=f"{base_url}/api/feed/{kind}/{token}.xml",
        description=f"SetVault {kind} feed for {user.display_name}",
        items=items,
        base_url=base_url,
        signing_key=settings.secret_key,
    )

    first_use = api_token.last_used_at is None
    await touch_last_used(session, api_token)
    if first_use:
        await audit_log(
            session, actor_user_id=user.id, actor_kind="user",
            action="apitoken.rss_first_use",
            target_type="api_token", target_id=str(api_token.id),
        )
    await session.commit()

    return Response(content=xml, media_type="application/rss+xml")
