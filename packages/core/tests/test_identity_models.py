from setvault_core.models.identity import EmailToken, User


async def test_create_user_round_trip(session):
    user = User(email="bart@example.com", username="bart", display_name="Bart",
                password_hash="argon2id$...", role="admin")
    session.add(user)
    await session.flush()
    assert user.id is not None
    assert user.created_at is not None


async def test_create_invite_token(session):
    token = EmailToken(email="new@example.com", kind="invite",
                       token_hash="abc", expires_at=None, payload={"role": "user"})
    session.add(token)
    await session.flush()
    assert token.id is not None
