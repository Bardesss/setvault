async def test_create_and_get_artist(authed_admin_client):
    r = await authed_admin_client.post("/api/catalog/artists",
                                       json={"name": "Charlotte de Witte", "country": "BE"})
    assert r.status_code == 201
    slug = r.json()["slug"]
    assert slug == "charlotte-de-witte"
    show = await authed_admin_client.get(f"/api/catalog/artists/{slug}")
    assert show.status_code == 200 and show.json()["name"] == "Charlotte de Witte"


async def test_create_venue_with_kind(authed_admin_client):
    r = await authed_admin_client.post("/api/catalog/venues", json={
        "name": "De School", "kind": "club", "city_or_area": "Amsterdam", "country": "NL",
    })
    assert r.status_code == 201
    assert r.json()["kind"] == "club"


async def test_create_party_with_venue_and_series(authed_admin_client):
    series = await authed_admin_client.post("/api/catalog/series",
                                            json={"name": "Essential Mix"})
    venue = await authed_admin_client.post("/api/catalog/venues",
                                           json={"name": "BBC Radio 1", "kind": "studio"})
    r = await authed_admin_client.post("/api/catalog/parties", json={
        "name": "EM 2024-06-29", "venue_id": venue.json()["id"],
        "series_id": series.json()["id"], "date": "2024-06-29",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["venue"]["name"] == "BBC Radio 1"
    assert body["series"]["name"] == "Essential Mix"


async def test_duplicate_slug_returns_409(authed_admin_client):
    await authed_admin_client.post("/api/catalog/artists", json={"name": "Aphex Twin"})
    again = await authed_admin_client.post("/api/catalog/artists",
                                           json={"name": "Aphex Twin"})
    assert again.status_code == 409
