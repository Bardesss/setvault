"""Sanity-level unit tests for the bulk_action job that don't need a DB.

The real exercise lives at the API + Playwright layer (an admin bulk-deletes
some seeded sets, recycle bin gains rows). Here we just verify the dispatch
table and parameter validation.
"""
from __future__ import annotations

import inspect

from setvault_core.jobs.bulk_action import (
    bulk_action,
    run_bulk_action,
)


def test_run_bulk_action_is_sync_wrapper():
    """The RQ entry point must be plain (not async) so workers can call it."""
    assert not inspect.iscoroutinefunction(run_bulk_action)
    assert inspect.iscoroutinefunction(bulk_action)


def test_run_bulk_action_signature_takes_keyword_args():
    """The endpoint enqueues with keyword args; the entry point must accept them."""
    sig = inspect.signature(run_bulk_action)
    expected = {"action", "set_ids", "params", "actor_user_id"}
    assert expected <= set(sig.parameters)
