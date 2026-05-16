from __future__ import annotations


async def test_search_finds_set_by_title(authed_admin_client, seeded_live_set):
    response = await authed_admin_client.get("/api/search?q=seeded")
    assert response.status_code == 200
    body = response.json()
    titles = [r["title"] for r in body["sets"]]
    assert any("seeded" in t.lower() for t in titles)


async def test_search_finds_artist(authed_admin_client):
    await authed_admin_client.post("/api/catalog/artists", json={"name": "Helena Hauff"})
    response = await authed_admin_client.get("/api/search?q=hauff")
    assert response.status_code == 200
    assert any("Hauff" in a["name"] for a in response.json()["artists"])
