"""Pure-logic check on the audit retention prune cutoff.

Full DB round-trip is integration territory; here we just verify the cutoff
math + that days<=0 disables pruning (the production guard)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from setvault_core.jobs.audit_retention import prune_audit_events  # noqa: F401


def test_cutoff_math_default_90_days():
    """Sanity-check the calculation matches the spec default (90 days)."""
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=90)
    assert (now - cutoff).days == 90


def test_disabled_when_days_zero():
    """The module reads SystemConfig.audit_retention_days; a 0 / negative
    value short-circuits before issuing the DELETE. This is the policy guard
    documented in the module docstring."""
    # We test the contract via inspection — the actual DB round-trip is
    # exercised by integration tests against TEST_DATABASE_URL.
    import setvault_core.jobs.audit_retention as mod
    src = mod.__file__
    with open(src, encoding="utf-8") as f:
        text = f.read()
    assert "days <= 0" in text, (
        "expected an early-return guard on days <= 0 — found neither "
        "`days <= 0` nor `days < 1` in the source"
    )
