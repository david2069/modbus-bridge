"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_17.json)

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


class InterfaceType(IntEnum):
    UNKNOWN = 0
    RS232 = 1
    RS485 = 2


class Protocol(IntEnum):
    UNKNOWN = 0
    MODBUS = 1
    VENDOR = 2


class Model17(SunSpecComponent):
    """SunSpec model 17: Serial Interface."""

    nam = string(2, 4, writable=True)
    """Name. Interface name (8 chars)."""

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

    typ = enum16(12, InterfaceType)
    """Interface Type."""

    pcol = enum16(13, Protocol)
    """Protocol. Serial protocol selection."""
