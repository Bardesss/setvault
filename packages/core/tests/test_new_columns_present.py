from setvault_core.models.ingest_sources import IngestSourceState
from setvault_core.models.system_config import SystemConfig


def test_ingest_source_state_has_rate_limit_columns():
    cols = IngestSourceState.__table__.columns
    assert "rate_limit_max" in cols
    assert "rate_limit_window_seconds" in cols


def test_system_config_has_monitor_settings():
    cols = SystemConfig.__table__.columns
    assert "monitors_allow_all_users" in cols
    assert "monitor_interval_seconds" in cols
