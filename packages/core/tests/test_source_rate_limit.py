import pytest
from setvault_core.services import source_rate_limit as srl


async def _purge(kind: str, window: int):
    # Delete this test's bucket key(s) so reruns within the expiry window are clean.
    redis = srl._client()
    bucket = int(srl.time.time() // window)
    await redis.delete(f"srcrl:{kind}:{bucket}")


@pytest.mark.asyncio
async def test_under_limit_allows_then_blocks(monkeypatch):
    monkeypatch.setattr(srl.time, "time", lambda: 1_000_000.0)  # pin clock to one bucket
    kind = "test-rl-allow"
    await _purge(kind, 60)
    for _ in range(3):
        assert await srl.allow(kind, limit=3, window_seconds=60) is True
    assert await srl.allow(kind, limit=3, window_seconds=60) is False
    await _purge(kind, 60)


@pytest.mark.asyncio
async def test_separate_kinds_have_separate_buckets(monkeypatch):
    monkeypatch.setattr(srl.time, "time", lambda: 1_000_000.0)
    a, b = "test-rl-a", "test-rl-b"
    await _purge(a, 60)
    await _purge(b, 60)
    assert await srl.allow(a, limit=1, window_seconds=60) is True
    assert await srl.allow(a, limit=1, window_seconds=60) is False
    assert await srl.allow(b, limit=1, window_seconds=60) is True
    await _purge(a, 60)
    await _purge(b, 60)


@pytest.mark.asyncio
async def test_zero_limit_always_allows(monkeypatch):
    monkeypatch.setattr(srl.time, "time", lambda: 1_000_000.0)
    assert await srl.allow("test-rl-zero", limit=0, window_seconds=60) is True
