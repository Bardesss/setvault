from setvault_core.services.passwords import hash_password, verify_password


def test_hash_and_verify_round_trip():
    h = hash_password("correct horse battery staple")
    assert h.startswith("$argon2id$")
    assert verify_password("correct horse battery staple", h) is True
    assert verify_password("wrong", h) is False


def test_needs_rehash_returns_bool():
    from setvault_core.services.passwords import needs_rehash
    h = hash_password("x")
    assert isinstance(needs_rehash(h), bool)
