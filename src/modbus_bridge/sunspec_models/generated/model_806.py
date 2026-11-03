"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_806.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    model_length_group,
    uint16,
)


class FlowBatteryBatteryString(Component):
    """One 'battery_string' block of SunSpec model 806."""

    bat_st_tbd = uint16(3)
    """Battery String Points To Be Determined."""


class FlowBattery(SunSpecComponent):
    """SunSpec model 806: Flow Battery Model."""

    bat_tbd = uint16(2)
    """Battery Points To Be Determined."""

    battery_string = model_length_group(FlowBatteryBatteryString, start=3, stride=1)
