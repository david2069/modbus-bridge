"""Shared test settings."""

import pytest


@pytest.fixture(autouse=True)
def _fast_retained_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reading back retained MQTT configs waits for quiet; keep that short in tests."""
    from modbus_bridge import mqtt

    monkeypatch.setattr(mqtt, "RETAINED_QUIET", 0.05)
