"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_303.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
    model_length_group,
)


class BomTempTemp(Component):
    """One 'temp' block of SunSpec model 303."""

    tmp_bom = int16(2, scale=0.1, unit='C')
    """Temp. Back of module temperature measurement."""


class BomTemp(SunSpecComponent):
    """SunSpec model 303: Back of Module Temperature Model."""

    temp = model_length_group(BomTempTemp, start=2, stride=1)
