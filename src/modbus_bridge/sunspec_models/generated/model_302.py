"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_302.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    model_length_group,
    uint16,
)


class IrradianceRepeating(Component):
    """One 'repeating' block of SunSpec model 302."""

    ghi = uint16(2, unit='W/m2')
    """GHI. Global Horizontal Irradiance."""

    poai = uint16(3, unit='W/m2')
    """POAI. Plane-of-Array Irradiance."""

    dfi = uint16(4, unit='W/m2')
    """DFI. Diffuse Irradiance."""

    dni = uint16(5, unit='W/m2')
    """DNI. Direct Normal Irradiance."""

    oti = uint16(6, unit='W/m2')
    """OTI. Other Irradiance."""


class Irradiance(SunSpecComponent):
    """SunSpec model 302: Irradiance Model."""

    repeating = model_length_group(IrradianceRepeating, start=2, stride=5)
