"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_809.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    model_length_group,
    uint16,
)


class FlowBatteryStackCell(Component):
    """One 'cell' block of SunSpec model 809."""

    cell_tbd = uint16(3)
    """Cell Points To Be Determined."""


class FlowBatteryStack(SunSpecComponent):
    """SunSpec model 809: Flow Battery Stack Model."""

    stack_tbd = uint16(2)
    """Stack Points To Be Determined."""

    cell = model_length_group(FlowBatteryStackCell, start=3, stride=1)
