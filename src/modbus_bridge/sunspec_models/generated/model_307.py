"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_307.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
)


class BaseMet(SunSpecComponent):
    """SunSpec model 307: Base Met."""

    tmp_amb = int16(2, scale=0.1, unit='C')
    """Ambient Temperature."""

    rh = int16(3, unit='Pct')
    """Relative Humidity."""

    pres = int16(4, unit='HPa')
    """Barometric Pressure."""

    wnd_spd = int16(5, unit='mps')
    """Wind Speed."""

    wnd_dir = int16(6, unit='deg')
    """Wind Direction."""

    rain = int16(7, unit='mm')
    """Rainfall."""

    snw = int16(8, unit='mm')
    """Snow Depth."""

    ppt = int16(9)
    """Precipitation Type. Precipitation Type (WMO 4680 SYNOP code reference)."""

    elec_fld = int16(10, unit='Vm')
    """Electric Field."""

    sur_wet = int16(11, unit='kO')
    """Surface Wetness."""

    soil_wet = int16(12, unit='Pct')
    """Soil Wetness."""
