"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_1.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    string,
    uint16,
)


class Common(SunSpecComponent):
    """SunSpec model 1: Common."""

    mn = string(2, 16)
    """Manufacturer. Well known value registered with SunSpec for compliance."""

    md = string(18, 16)
    """Model. Manufacturer specific value (32 chars)."""

    opt = string(34, 8)
    """Options. Manufacturer specific value (16 chars)."""

    vr = string(42, 8)
    """Version. Manufacturer specific value (16 chars)."""

    sn = string(50, 16)
    """Serial Number. Manufacturer specific value (32 chars)."""

    da = uint16(66, writable=True)
    """Device Address. Modbus device address."""
