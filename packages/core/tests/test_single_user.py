from setvault_core.services.single_user import should_auto_login


def test_auto_login_only_when_enabled_and_exactly_one_user():
    assert should_auto_login(enabled=True, active_user_count=1) is True


def test_no_auto_login_when_disabled():
    assert should_auto_login(enabled=False, active_user_count=1) is False


def test_no_auto_login_with_multiple_users():
    assert should_auto_login(enabled=True, active_user_count=2) is False


def test_no_auto_login_with_zero_users():
    assert should_auto_login(enabled=True, active_user_count=0) is False
