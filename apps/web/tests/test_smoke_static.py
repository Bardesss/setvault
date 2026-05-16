async def test_root_index_html_served(client):
    response = await client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "<!doctype html>" in body.lower()
    assert "setvault" in body.lower()
