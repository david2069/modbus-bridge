"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64413.json)

from __future__ import annotations

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    float32,
    uint16,
)


class PVSimCurvesIV(Component):
    """One 'IV' block of SunSpec model 64413."""

    p = float32(5, unit='W')
    """Power."""

    i = float32(7, unit='A')
    """Current."""

    v = float32(9, unit='V')
    """Voltage."""


class PVSimCurves(SunSpecComponent):
    """SunSpec model 64413: PV Curves."""

    iv_len = uint16(2)
    """IV length. Number of points in the IV curve."""

    irr = uint16(3, scale_register=4, unit='W/m^2')
    """POA Irradiance. Plane of Array Irradiance."""

    iv = repeating_group(uint16(2), PVSimCurvesIV, stride=6)
