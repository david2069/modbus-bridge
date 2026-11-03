"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_8.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    model_length_group,
    uint16,
)


class Format(IntEnum):
    NONE = 0
    X509_PEM = 1
    X509_DER = 2


class Model8Repeating(Component):
    """One 'repeating' block of SunSpec model 8."""

    cert = uint16(4)
    """Cert. X.509 Certificate of the device."""


class Model8(SunSpecComponent):
    """SunSpec model 8: Get Device Security Certificate."""

    fmt = enum16(2, Format)
    """Format. X.509 format of the certificate. DER or PEM."""

    n = uint16(3)
    """N. Number of registers to follow for the certificate."""

    repeating = model_length_group(Model8Repeating, start=4, stride=1)
