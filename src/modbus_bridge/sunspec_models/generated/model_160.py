"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_160.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    enum16,
    int16,
    string,
    uint16,
    uint32,
)


class OperatingState(IntEnum):
    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8
    TEST = 9
    RESERVED_10 = 10


class ModuleEvents(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    RESERVED_2 = 1 << 2
    DC_DISCONNECT = 1 << 3
    RESERVED_4 = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    RESERVED_8 = 1 << 8
    RESERVED_9 = 1 << 9
    RESERVED_10 = 1 << 10
    RESERVED_11 = 1 << 11
    BLOWN_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    RESERVED_16 = 1 << 16
    RESERVED_17 = 1 << 17
    RESERVED_18 = 1 << 18
    RESERVED_19 = 1 << 19
    TEST_FAILED = 1 << 20
    INPUT_UNDER_VOLTAGE = 1 << 21
    INPUT_OVER_CURRENT = 1 << 22


class GlobalEvents(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    RESERVED_2 = 1 << 2
    DC_DISCONNECT = 1 << 3
    RESERVED_4 = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    RESERVED_8 = 1 << 8
    RESERVED_9 = 1 << 9
    RESERVED_10 = 1 << 10
    RESERVED_11 = 1 << 11
    BLOWN_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    RESERVED_16 = 1 << 16
    RESERVED_17 = 1 << 17
    RESERVED_18 = 1 << 18
    RESERVED_19 = 1 << 19
    TEST_FAILED = 1 << 20
    INPUT_UNDER_VOLTAGE = 1 << 21
    INPUT_OVER_CURRENT = 1 << 22


class MpptModule(Component):
    """One 'module' block of SunSpec model 160."""

    id = uint16(10)
    """Input ID."""

    id_str = string(11, 8)
    """Input ID String."""

    dca = uint16(19, scale_register=2, unit='A')
    """DC Current."""

    dcv = uint16(20, scale_register=3, unit='V')
    """DC Voltage."""

    dcw = uint16(21, scale_register=4, unit='W')
    """DC Power."""

    dcwh = acc32(22, scale_register=5, unit='Wh')
    """Lifetime Energy."""

    tms = uint32(24, unit='Secs')
    """Timestamp."""

    tmp = int16(26, unit='C')
    """Temperature."""

    dc_st = enum16(27, OperatingState)
    """Operating State."""

    dc_evt = bitfield32(28, ModuleEvents)
    """Module Events."""


class Mppt(SunSpecComponent):
    """SunSpec model 160: Multiple MPPT Inverter Extension Model."""

    evt = bitfield32(6, GlobalEvents)
    """Global Events."""

    n = uint16(8)
    """Number of Modules."""

    tms_per = uint16(9)
    """Timestamp Period."""

    module = repeating_group(uint16(8), MpptModule, stride=20)
