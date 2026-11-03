"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_306.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    uint16,
)


class RefPoint(SunSpecComponent):
    """SunSpec model 306: Reference Point Model."""

    ghi = uint16(2, unit='W/m2')
    """GHI. Global Horizontal Irradiance."""

    a = uint16(3, unit='W/m2')
    """Amps. Current measurement at reference point."""

    v = uint16(4, unit='W/m2')
    """Voltage. Voltage measurement at reference point."""

    tmp = uint16(5, unit='W/m2')
    """Temperature. Temperature measurement at reference point."""
