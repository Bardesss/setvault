import pytest


@pytest.fixture(autouse=True)
def _db():
    import os
    os.environ.setdefault(
        "TEST_DATABASE_URL", "postgresql+asyncpg://setvault:setvault@localhost:5432/setvault"
    )


async def test_mutation_without_csrf_token_is_rejected(client, seeded_admin):
    login = await client.post("/api/auth/login",
                              json={"email": "admin@example.test", "password": "hunter2hunter2"})
    client.cookies = login.cookies
    response = await client.post("/api/auth/logout")  # no X-CSRF-Token header
    assert response.status_code == 403
    assert "csrf" in response.text.lower()


async def test_mutation_with_matching_csrf_token_is_allowed(client, seeded_admin):
    login = await client.post("/api/auth/login",
                              json={"email": "admin@example.test", "password": "hunter2hunter2"})
    client.cookies = login.cookies
    csrf = login.cookies.get("csrf_token")
    assert csrf
    response = await client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 204
