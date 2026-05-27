from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CommentAuthor(BaseModel):
    id: str
    username: str
    display_name: str | None = None


class CommentOut(BaseModel):
    id: str
    parent_id: str | None = None
    position_seconds: int | None = None
    body_html: str
    body_md: str
    author: CommentAuthor
    mentions: list[CommentAuthor] = Field(default_factory=list)
    edited_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime


class CommentCreateIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    parent_id: str | None = None
    position_seconds: int | None = Field(default=None, ge=0)


class CommentEditIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class CommentsListOut(BaseModel):
    items: list[CommentOut]
    total: int
