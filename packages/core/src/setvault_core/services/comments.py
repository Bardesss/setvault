from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime, timedelta

import bleach
import markdown
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_core.models.engagement_3c import Comment
from setvault_core.models.identity import User

# Spec 2026-05-17 §5.3.1: bleach whitelist is emphasis / strong / links /
# code spans+blocks / paragraphs / lists. Headings, images, and raw HTML are
# deliberately excluded — `# Heading` renders as inline text (the `<h1>` tag
# is stripped and the content remains). Document this in the composer help
# if it ever surprises a user.
ALLOWED_TAGS = {
    "p", "br", "em", "strong", "a", "code", "pre", "ul", "ol", "li", "blockquote",
}
ALLOWED_ATTRIBUTES = {"a": ["href", "rel", "title"]}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}
EDIT_WINDOW = timedelta(minutes=5)

# Matches @username where username = letters/digits/underscore, NOT preceded by a word char
# (so "user@example.com" doesn't match the "@example" part).
_MENTION = re.compile(r"(?<![\w@])@([a-zA-Z][a-zA-Z0-9_]{1,29})\b")


class CommentValidationError(ValueError):
    pass


def render_markdown_safe(body_md: str) -> str:
    html = markdown.markdown(body_md, extensions=["fenced_code", "nl2br"])
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES,
                           protocols=ALLOWED_PROTOCOLS, strip=True)
    # Force rel="noopener noreferrer" on links
    cleaned = re.sub(r'<a\s+href="([^"]*)"', r'<a href="\1" rel="noopener noreferrer"', cleaned)
    return cleaned


def extract_mention_usernames(body: str) -> list[str]:
    seen: list[str] = []
    for m in _MENTION.finditer(body):
        uname = m.group(1)
        if uname not in seen:
            seen.append(uname)
    return seen


async def resolve_mentions_to_user_ids(
    session: AsyncSession, usernames: list[str],
) -> list[uuid.UUID]:
    if not usernames:
        return []
    rows = (await session.execute(
        select(User.id).where(User.username.in_(usernames))
    )).scalars().all()
    return list(rows)


async def create_comment(
    session: AsyncSession,
    *,
    live_set_id: uuid.UUID,
    user_id: uuid.UUID,
    body: str,
    parent_id: uuid.UUID | None = None,
    position_seconds: int | None = None,
) -> Comment:
    # Enforce one-level nesting
    if parent_id is not None:
        parent = await session.get(Comment, parent_id)
        if parent is None or parent.live_set_id != live_set_id:
            raise CommentValidationError("parent not found in this set")
        if parent.parent_id is not None:
            raise CommentValidationError("only one level of nesting")
    usernames = extract_mention_usernames(body)
    mention_ids = await resolve_mentions_to_user_ids(session, usernames)
    c = Comment(
        live_set_id=live_set_id, user_id=user_id, parent_id=parent_id,
        position_seconds=position_seconds, body=body,
        mentions_user_ids=mention_ids, created_at=datetime.now(UTC),
    )
    session.add(c)
    await session.flush()
    return c


async def edit_comment(
    session: AsyncSession, comment: Comment, *, user_id: uuid.UUID,
    body: str, is_admin: bool = False,
) -> None:
    if comment.user_id != user_id and not is_admin:
        raise CommentValidationError("not your comment")
    if not is_admin and (datetime.now(UTC) - comment.created_at) > EDIT_WINDOW:
        raise CommentValidationError("edit window closed")
    comment.body = body
    comment.edited_at = datetime.now(UTC)
    # Re-parse mentions on edit
    usernames = extract_mention_usernames(body)
    comment.mentions_user_ids = await resolve_mentions_to_user_ids(session, usernames)
    await session.flush()


async def soft_delete_comment(
    session: AsyncSession, comment: Comment, *, user_id: uuid.UUID, is_admin: bool = False,
) -> None:
    if comment.user_id != user_id and not is_admin:
        raise CommentValidationError("not your comment")
    comment.deleted_at = datetime.now(UTC)
    await session.flush()
