"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_808.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    model_length_group,
    uint16,
)


class FlowBatteryModuleStack(Component):
    """One 'stack' block of SunSpec model 808."""

    stack_tbd = uint16(3)
    """Stack Points To Be Determined."""


class FlowBatteryModule(SunSpecComponent):
    """SunSpec model 808: Flow Battery Module Model."""

    module_tbd = uint16(2)
    """Module Points To Be Determined."""

    stack = model_length_group(FlowBatteryModuleStack, start=3, stride=1)
