"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_304.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int32,
    model_length_group,
)


class InclinometerIncl(Component):
    """One 'incl' block of SunSpec model 304."""

    inclx = int32(2, scale=0.01, unit='Degrees')
    """X. X-Axis inclination."""

    incly = int32(4, scale=0.01, unit='Degrees')
    """Y. Y-Axis inclination."""

    inclz = int32(6, scale=0.01, unit='Degrees')
    """Z. Z-Axis inclination."""


class Inclinometer(SunSpecComponent):
    """SunSpec model 304: Inclinometer Model."""

    incl = model_length_group(InclinometerIncl, start=2, stride=6)
