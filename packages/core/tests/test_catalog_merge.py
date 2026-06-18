# packages/core/tests/test_catalog_merge.py
import os
import uuid

import pytest
from setvault_core.db import init_engine
from setvault_core.models.catalog import (
    Artist,
    LiveSet,
    LiveSetArtist,
    MediaRoot,
    Party,
    Series,
    Venue,
)
from setvault_core.models.identity import User
from setvault_core.models.tracklist import Track
from setvault_core.services.catalog_merge import merge_entities, unmerge_entity
from setvault_core.services.passwords import hash_password


@pytest.fixture(autouse=True)
def _engine():
    init_engine(os.environ["TEST_DATABASE_URL"])


async def _scaffold(s):
    root = MediaRoot(name=f"r-{uuid.uuid4().hex[:6]}", host_path="/srv/test-media")
    s.add(root)
    await s.flush()
    u = User(email=f"u-{uuid.uuid4().hex[:6]}@x.test", username=f"u{uuid.uuid4().hex[:6]}",
             display_name="u", password_hash=hash_password("aaaaaaaa"))
    s.add(u)
    await s.flush()
    return root.id, u.id


async def test_merge_artist_repoints_refs_and_tombstones_loser(session):
    s = session
    root_id, uid = await _scaffold(s)
    survivor = Artist(name="DJ X", slug=f"x-{uuid.uuid4().hex[:6]}", bio="canonical")
    loser = Artist(name="DJ X (alt)", slug=f"xa-{uuid.uuid4().hex[:6]}", country="BE")
    s.add_all([survivor, loser])
    await s.flush()

    ls = LiveSet(slug=f"s-{uuid.uuid4().hex[:8]}", title="t", media_root_id=root_id,
                 audio_path="a/b.flac", status="published", source_type="upload", uploaded_by=uid)
    s.add(ls)
    await s.flush()
    s.add(LiveSetArtist(live_set_id=ls.id, artist_id=loser.id, position=0))
    track = Track(title="T", primary_artist_id=loser.id)
    s.add(track)
    await s.commit()
    survivor_id, loser_id, ls_id, track_id = survivor.id, loser.id, ls.id, track.id

    await merge_entities(s, kind="artist", survivor_id=survivor_id, loser_id=loser_id, actor_id=uid)
    await s.commit()

    # references now point at survivor
    lsa = (await s.execute(
        LiveSetArtist.__table__.select().where(LiveSetArtist.live_set_id == ls_id)
    )).first()
    assert lsa.artist_id == survivor_id
    assert (await s.get(Track, track_id)).primary_artist_id == survivor_id
    # loser tombstoned
    dead = await s.get(Artist, loser_id)
    assert dead.merged_into_id == survivor_id and dead.merged_at is not None
    # gap-fill: survivor had no country, takes loser's
    surv = await s.get(Artist, survivor_id)
    assert surv.country == "BE"
    assert surv.bio == "canonical"  # survivor's own non-empty field wins
    # loser name folded into survivor aliases
    assert "DJ X (alt)" in surv.aliases


async def test_merge_artist_dedupes_join_pk_collision(session):
    s = session
    root_id, uid = await _scaffold(s)
    survivor = Artist(name="A", slug=f"a-{uuid.uuid4().hex[:6]}")
    loser = Artist(name="A dup", slug=f"ad-{uuid.uuid4().hex[:6]}")
    s.add_all([survivor, loser])
    await s.flush()
    ls = LiveSet(slug=f"s-{uuid.uuid4().hex[:8]}", title="t", media_root_id=root_id,
                 audio_path="a/b.flac", status="published", source_type="upload", uploaded_by=uid)
    s.add(ls)
    await s.flush()
    # BOTH artists on the same set -> merging would collide on (live_set_id, artist_id)
    s.add(LiveSetArtist(live_set_id=ls.id, artist_id=survivor.id, position=0))
    s.add(LiveSetArtist(live_set_id=ls.id, artist_id=loser.id, position=1))
    await s.commit()
    sid, lid, ls_id = survivor.id, loser.id, ls.id

    await merge_entities(s, kind="artist", survivor_id=sid, loser_id=lid, actor_id=uid)
    await s.commit()

    rows = (await s.execute(
        LiveSetArtist.__table__.select().where(LiveSetArtist.live_set_id == ls_id)
    )).all()
    artist_ids = {r.artist_id for r in rows}
    assert artist_ids == {sid}  # the colliding loser row was dropped, not duplicated


async def test_merge_rejects_same_id(session):
    s = session
    a = Artist(name="Z", slug=f"z-{uuid.uuid4().hex[:6]}")
    s.add(a)
    await s.commit()
    with pytest.raises(ValueError):
        await merge_entities(s, kind="artist", survivor_id=a.id, loser_id=a.id, actor_id=None)


async def test_merge_rejects_unknown_kind(session):
    s = session
    a = Artist(name="K", slug=f"k-{uuid.uuid4().hex[:6]}")
    b = Artist(name="K2", slug=f"k2-{uuid.uuid4().hex[:6]}")
    s.add_all([a, b])
    await s.commit()
    with pytest.raises(ValueError):
        await merge_entities(s, kind="bogus", survivor_id=a.id, loser_id=b.id, actor_id=None)


async def test_merge_venue_repoints_sets_and_parties(session):
    s = session
    root_id, uid = await _scaffold(s)
    keep = Venue(name="Club", slug=f"c-{uuid.uuid4().hex[:6]}", kind="club")
    dup = Venue(name="Club dup", slug=f"cd-{uuid.uuid4().hex[:6]}", kind="club")
    s.add_all([keep, dup])
    await s.flush()
    ls = LiveSet(slug=f"s-{uuid.uuid4().hex[:8]}", title="t", media_root_id=root_id,
                 audio_path="a/b.flac", status="published", source_type="upload",
                 uploaded_by=uid, venue_id=dup.id)
    party = Party(name="P", slug=f"p-{uuid.uuid4().hex[:6]}", venue_id=dup.id)
    s.add_all([ls, party])
    await s.commit()
    keep_id, dup_id, ls_id, party_id = keep.id, dup.id, ls.id, party.id

    await merge_entities(s, kind="venue", survivor_id=keep_id, loser_id=dup_id, actor_id=uid)
    await s.commit()
    assert (await s.get(LiveSet, ls_id)).venue_id == keep_id
    assert (await s.get(Party, party_id)).venue_id == keep_id
    assert (await s.get(Venue, dup_id)).merged_into_id == keep_id


async def test_merge_series_repoints_parties(session):
    s = session
    keep = Series(name="Ser", slug=f"ser-{uuid.uuid4().hex[:6]}")
    dup = Series(name="Ser dup", slug=f"serd-{uuid.uuid4().hex[:6]}")
    s.add_all([keep, dup])
    await s.flush()
    party = Party(name="P", slug=f"p-{uuid.uuid4().hex[:6]}", series_id=dup.id)
    s.add(party)
    await s.commit()
    keep_id, dup_id, party_id = keep.id, dup.id, party.id

    await merge_entities(s, kind="series", survivor_id=keep_id, loser_id=dup_id, actor_id=None)
    await s.commit()
    assert (await s.get(Party, party_id)).series_id == keep_id
    assert (await s.get(Series, dup_id)).merged_into_id == keep_id


async def test_unmerge_restores_references(session):
    s = session
    root_id, uid = await _scaffold(s)
    survivor = Artist(name="DJ X", slug=f"x-{uuid.uuid4().hex[:6]}")
    loser = Artist(name="DJ X alt", slug=f"xa-{uuid.uuid4().hex[:6]}")
    s.add_all([survivor, loser])
    await s.flush()
    ls = LiveSet(slug=f"s-{uuid.uuid4().hex[:8]}", title="t", media_root_id=root_id,
                 audio_path="a/b.flac", status="published", source_type="upload", uploaded_by=uid)
    s.add(ls)
    await s.flush()
    s.add(LiveSetArtist(live_set_id=ls.id, artist_id=loser.id, position=0))
    await s.commit()
    sid, lid, ls_id = survivor.id, loser.id, ls.id

    await merge_entities(s, kind="artist", survivor_id=sid, loser_id=lid, actor_id=uid)
    await s.commit()
    await unmerge_entity(s, kind="artist", loser_id=lid, actor_id=uid)
    await s.commit()

    revived = await s.get(Artist, lid)
    assert revived.merged_into_id is None and revived.merge_manifest is None
    lsa = (await s.execute(
        LiveSetArtist.__table__.select().where(LiveSetArtist.live_set_id == ls_id)
    )).first()
    assert lsa.artist_id == lid  # reference moved back to the revived entity
