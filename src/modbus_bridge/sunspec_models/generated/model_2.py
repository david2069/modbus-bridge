"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_2.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    enum32,
    uint16,
)


class Status(IntEnum):
    OFF = 1
    ON = 2
    FULL = 3
    FAULT = 4


class EventCode(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    RESERVED_2 = 1 << 2
    DC_DISCONNECT = 1 << 3
    RESERVED_4 = 1 << 4
    RESERVED_5 = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMPERATURE = 1 << 7
    RESERVED_8 = 1 << 8
    RESERVED_9 = 1 << 9
    RESERVED_10 = 1 << 10
    RESERVED_11 = 1 << 11
    BLOWN_FUSE = 1 << 12
    UNDER_TEMPERATURE = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    THEFT_DETECTION = 1 << 16
    OUTPUT_OVER_CURRENT = 1 << 17
    OUTPUT_OVER_VOLTAGE = 1 << 18
    OUTPUT_UNDER_VOLTAGE = 1 << 19
    TEST_FAILED = 1 << 20


class Control(IntEnum):
    NONE = 0
    AUTOMATIC = 1
    FORCE_OFF = 2
    TEST = 3
    THROTTLE = 4


class Aggregator(SunSpecComponent):
    """SunSpec model 2: Basic Aggregator."""

    aid = uint16(2)
    """AID. Aggregated model id."""

    n = uint16(3)
    """N. Number of aggregated models."""

    un = uint16(4)
    """UN. Update Number. Incrementing number each time the mapping is changed. If
    the number is not changed from the last reading the direct access to a
    specific offset will result in reading the same logical model as before.
    Otherwise the entire model must be read to refresh the changes."""

    st = enum16(5, Status)
    """Status. Enumerated status code."""

    st_vnd = enum16(6)
    """Vendor Status. Vendor specific status code."""

    evt = bitfield32(7, EventCode)
    """Event Code. Bitmask event code."""

    evt_vnd = bitfield32(9)
    """Vendor Event Code. Vendor specific event code."""

    ctl = enum16(11, Control)
    """Control. Control register for all aggregated devices."""

    ctl_vnd = enum32(12)
    """Vendor Control. Vendor control register for all aggregated devices."""

    ctl_vl = enum32(14)
    """Control Value. Numerical value used as a parameter to the control."""
