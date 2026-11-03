"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_19.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    string,
    uint16,
    uint32,
)


class Parity(IntEnum):
    NONE = 0
    ODD = 1
    EVEN = 2


class Duplex(IntEnum):
    FULL = 0
    HALF = 1


class FlowControl(IntEnum):
    NONE = 0
    HW = 1
    XONXOFF = 2


class Authentication(IntEnum):
    NONE = 0
    PAP = 1
    CHAP = 2


class Model19(SunSpecComponent):
    """SunSpec model 19: PPP Link."""

    nam = string(2, 4, writable=True)
    """Name. Interface name."""

    rte = uint32(6, writable=True, unit='bps')
    """Rate. Interface baud rate in bits per second."""

    bits = uint16(8, writable=True)
    """Bits. Number of data bits per character."""

    pty = enum16(9, Parity, writable=True)
    """Parity. Parity setting."""

    dup = enum16(10, Duplex, writable=True)
    """Duplex. Duplex mode."""

    flw = enum16(11, FlowControl, writable=True)
    """Flow Control. Flow Control Method."""

    auth = enum16(12, Authentication)
    """Authentication. Authentication method."""

    usr_nam = string(13, 12)
    """Username. Username for authentication."""

    pw = string(25, 6)
    """Password. Password for authentication."""
