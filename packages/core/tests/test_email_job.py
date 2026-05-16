from setvault_core.jobs.email import build_message


def test_build_message_sets_required_headers():
    msg = build_message(
        from_email="noreply@setvault.test", from_name="SetVault",
        to="user@example.test", subject="Hello", text="Body here",
        reply_to=None,
    )
    assert msg["From"] == "SetVault <noreply@setvault.test>"
    assert msg["To"] == "user@example.test"
    assert msg["Subject"] == "Hello"
    assert msg.get_content().strip() == "Body here"


def test_build_message_includes_reply_to_when_set():
    msg = build_message(from_email="n@x.test", from_name="N", to="t@x.test",
                        subject="S", text="B", reply_to="ops@x.test")
    assert msg["Reply-To"] == "ops@x.test"
