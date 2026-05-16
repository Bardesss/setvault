from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from setvault_core.models.catalog import Artist, Party, Series, Venue
from setvault_core.schemas.catalog import (
    ArtistIn,
    ArtistOut,
    PartyIn,
    PartyOut,
    SeriesIn,
    SeriesOut,
    VenueIn,
    VenueOut,
)
from setvault_core.services.catalog import slugify
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from setvault_web.deps import current_user, db_session

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


def _artist_out(a: Artist) -> ArtistOut:
    return ArtistOut(
        id=str(a.id),
        name=a.name,
        slug=a.slug,
        country=a.country,
        bio=a.bio,
        aliases=list(a.aliases or []),
        image_url=a.image_url,
    )


def _venue_out(v: Venue) -> VenueOut:
    return VenueOut(
        id=str(v.id),
        slug=v.slug,
        name=v.name,
        kind=v.kind,
        city_or_area=v.city_or_area,
        country=v.country,
        capacity=v.capacity,
        website=v.website,
    )


def _series_out(s: Series) -> SeriesOut:
    return SeriesOut(
        id=str(s.id),
        slug=s.slug,
        name=s.name,
        description=s.description,
        image_url=s.image_url,
    )


def _party_out(p: Party) -> PartyOut:
    return PartyOut(
        id=str(p.id),
        name=p.name,
        slug=p.slug,
        venue=_venue_out(p.venue) if p.venue is not None else None,
        series=_series_out(p.series) if p.series is not None else None,
        date=p.date,
        description=p.description,
    )


# -------- Artists --------


@router.post("/artists", response_model=ArtistOut, status_code=201)
async def create_artist(
    body: ArtistIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = Artist(
        name=body.name,
        slug=slugify(body.name),
        country=body.country,
        bio=body.bio,
        aliases=list(body.aliases),
        image_url=body.image_url,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="artist slug already exists") from exc
    return _artist_out(row)


@router.get("/artists/{slug}", response_model=ArtistOut)
async def get_artist(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(select(Artist).where(Artist.slug == slug))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="artist not found")
    return _artist_out(row)


# -------- Venues --------


@router.post("/venues", response_model=VenueOut, status_code=201)
async def create_venue(
    body: VenueIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = Venue(
        name=body.name,
        slug=slugify(body.name),
        kind=body.kind,
        city_or_area=body.city_or_area,
        country=body.country,
        capacity=body.capacity,
        website=body.website,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="venue slug already exists") from exc
    return _venue_out(row)


@router.get("/venues/{slug}", response_model=VenueOut)
async def get_venue(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(select(Venue).where(Venue.slug == slug))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="venue not found")
    return _venue_out(row)


# -------- Series --------


@router.post("/series", response_model=SeriesOut, status_code=201)
async def create_series(
    body: SeriesIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = Series(
        name=body.name,
        slug=slugify(body.name),
        description=body.description,
        image_url=body.image_url,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="series slug already exists") from exc
    return _series_out(row)


@router.get("/series/{slug}", response_model=SeriesOut)
async def get_series(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(select(Series).where(Series.slug == slug))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="series not found")
    return _series_out(row)


# -------- Parties --------


@router.post("/parties", response_model=PartyOut, status_code=201)
async def create_party(
    body: PartyIn,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    venue_uuid = uuid.UUID(body.venue_id) if body.venue_id else None
    series_uuid = uuid.UUID(body.series_id) if body.series_id else None
    row = Party(
        name=body.name,
        slug=slugify(body.name),
        venue_id=venue_uuid,
        series_id=series_uuid,
        date=body.date,
        description=body.description,
    )
    session.add(row)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="party slug already exists") from exc
    await session.refresh(row, attribute_names=["venue", "series"])
    return _party_out(row)


@router.get("/parties/{slug}", response_model=PartyOut)
async def get_party(
    slug: str,
    session: Annotated[AsyncSession, Depends(db_session)],
    _: Annotated[object, Depends(current_user)],
):
    row = (
        await session.execute(select(Party).where(Party.slug == slug))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="party not found")
    return _party_out(row)
