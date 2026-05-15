from datetime import date

from setvault_core.models.catalog import Artist, LiveSet, LiveSetArtist, MediaRoot, Party, Venue
from setvault_core.models.identity import User


async def test_live_set_with_artist_and_venue(session):
    user = User(email="u@x.test", username="u", display_name="u", password_hash="x", role="admin")
    session.add(user)
    await session.flush()

    artist = Artist(name="Carl Cox", slug="carl-cox")
    venue = Venue(name="Awakenings", slug="awakenings", kind="outdoor",
                  city_or_area="Recreatiegebied Spaarnwoude", country="NL")
    party = Party(name="Awakenings Festival", slug="awakenings-festival-2024",
                  venue=venue, date=date(2024, 6, 29))
    root = MediaRoot(name="primary", host_path="/srv/media/primary",
                     enabled=True, default_for_ingest=True)
    session.add_all([artist, venue, party, root])
    await session.flush()

    live = LiveSet(
        slug="carl-cox-awakenings-2024",
        title="Carl Cox @ Awakenings Festival 2024",
        party=party, venue=venue, date=date(2024, 6, 29),
        set_type="headline", duration_seconds=7200, source_type="upload",
        media_root_id=root.id,
        audio_path="originals/carl/orig.flac",
        streaming_path="stream/carl.opus",
        waveform_path="waveform/carl.json",
        uploaded_by=user.id,
    )
    live.artists.append(LiveSetArtist(artist=artist, position=0, role="main"))
    session.add(live)
    await session.flush()

    assert live.id is not None
    assert live.artists[0].artist.name == "Carl Cox"
