"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_18.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    string,
    uint32,
)


class Model18(SunSpecComponent):
    """SunSpec model 18: Cellular Link."""

    nam = string(2, 4, writable=True)
    """Name. Interface name."""

    imei = uint32(6, writable=True)
    """IMEI. International Mobile Equipment Identifier for the interface."""

    apn = string(8, 4, writable=True)
    """APN. Access Point Name for the interface."""

    num = string(12, 6, writable=True)
    """Number. Phone number for the interface."""

    pin = string(18, 6, writable=True)
    """PIN. Personal Identification Number for the interface."""
