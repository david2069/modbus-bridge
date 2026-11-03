"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_308.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
    uint16,
)


class MiniMet(SunSpecComponent):
    """SunSpec model 308: Mini Met Model."""

    ghi = uint16(2, unit='W/m2')
    """GHI. Global Horizontal Irradiance."""

    tmp_bom = int16(3, scale=0.1, unit='C')
    """Temp. Back of module temperature measurement."""

    tmp_amb = int16(4, scale=0.1, unit='C')
    """Ambient Temperature."""

    wnd_spd = uint16(5, unit='m/s')
    """Wind Speed."""
