"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_502.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    enum16,
    enum32,
    int16,
    int32,
    uint32,
)


class Status(IntEnum):
    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8
    TEST = 9
    OTHER = 10


class Events(IntFlag):
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


class SolarModule(SunSpecComponent):
    """SunSpec model 502: Solar Module."""

    stat = enum16(6, Status)
    """Status. Module Status Code."""

    stat_vend = enum16(7)
    """Vendor Status. Module Vendor Status Code."""

    evt = bitfield32(8, Events)
    """Events. Module Event Flags."""

    evt_vend = bitfield32(10)
    """Vendor Module Event Flags. Vendor specific flags."""

    ctl = enum16(12, writable=True)
    """Control. Module Control."""

    ctl_vend = enum32(13, writable=True)
    """Vendor Control. Vendor Module Control."""

    ctl_val = int32(15, writable=True)
    """Control Value. Module Control Value."""

    tms = uint32(17, unit='Secs')
    """Timestamp. Time in seconds since 2000 epoch."""

    out_a = int16(19, scale_register=2, unit='A')
    """Output Current."""

    out_v = int16(20, scale_register=3, unit='V')
    """Output Voltage."""

    out_wh = acc32(21, scale_register=5, unit='Wh')
    """Output Energy."""

    out_pw = int16(23, scale_register=4, unit='W')
    """Output Power."""

    tmp = int16(24, unit='C')
    """Temp. Module Temperature."""

    in_a = int16(25, scale_register=2, unit='A')
    """Input Current."""

    in_v = int16(26, scale_register=3, unit='V')
    """Input Voltage."""

    in_wh = acc32(27, scale_register=5, unit='Wh')
    """Input Energy."""

    in_w = int16(29, scale_register=4, unit='W')
    """Input Power."""
