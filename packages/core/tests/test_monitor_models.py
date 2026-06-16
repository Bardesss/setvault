from __future__ import annotations

import uuid

from setvault_core.models.monitors import Monitor, MonitorDiscovery


def test_monitor_constructs():
    m = Monitor(kind="query", query_text="Bicep", owner_user_id=uuid.uuid4())
    assert m.kind == "query"
    assert m.query_text == "Bicep"
    assert m.source_kind is None
    assert m.external_id is None


def test_discovery_constructs():
    d = MonitorDiscovery(
        monitor_id=uuid.uuid4(), source_kind="soundcloud", external_id="abc123",
        title="Bicep @ Field Day", uploader="Bicep",
        webpage_url="https://soundcloud.com/bicep/field-day",
        confidence="high", status="auto_ingested",
    )
    assert d.source_kind == "soundcloud"
    assert d.confidence == "high"
    assert d.status == "auto_ingested"
    assert d.url_rip_id is None
