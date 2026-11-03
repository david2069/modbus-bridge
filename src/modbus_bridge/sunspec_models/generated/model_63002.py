"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_63002.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
    model_length_group,
)


class Model63002Repeating(Component):
    """One 'repeating' block of SunSpec model 63002."""

    scale_in_block = True  # each instance carries its own scale factors

    int16_1 = int16(3, scale_register=2, writable=True)

    int16_2 = int16(4, scale_register=5)


class Model63002(SunSpecComponent):
    """SunSpec model 63002: SunSpec Test Model 2."""

    repeating = model_length_group(Model63002Repeating, start=2, stride=4)
