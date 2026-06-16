import pytest
from pydantic import ValidationError
from setvault_core.schemas.monitors import MonitorCreate


def test_query_create_valid():
    mc = MonitorCreate(kind="query", query_text="Bicep")
    assert mc.kind == "query"
    assert mc.source_kind is None


def test_query_create_requires_query_text():
    with pytest.raises(ValidationError):
        MonitorCreate(kind="query")


def test_entity_create_requires_source_and_external():
    with pytest.raises(ValidationError):
        MonitorCreate(kind="entity", source_kind="youtube")


def test_invalid_kind_rejected():
    with pytest.raises(ValidationError):
        MonitorCreate(kind="bogus", query_text="x")
