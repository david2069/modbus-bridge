"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_714.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    string,
    uint16,
    uint64,
)


class PortType(IntEnum):
    PV = 0
    ESS = 1
    EV = 2
    INJ = 3
    ABS = 4
    BIDIR = 5
    DC_DC = 6


class DCPortStatus(IntEnum):
    OFF = 0
    ON = 1
    WARNING = 2
    ERROR = 3


class DCPortAlarm(IntFlag):
    GROUND_FAULT = 1 << 0
    INPUT_OVER_VOLTAGE = 1 << 1
    DC_DISCONNECT = 1 << 3
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    BLOWN_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    ARC_DETECTION = 1 << 15
    RESERVED = 1 << 19
    TEST_FAILED = 1 << 20
    INPUT_UNDER_VOLTAGE = 1 << 21
    INPUT_OVER_CURRENT = 1 << 22


class DERMeasureDCPrt(Component):
    """One 'Prt' block of SunSpec model 714."""

    prt_typ = enum16(20, PortType)
    """Port Type."""

    id = uint16(21)
    """Port ID."""

    id_str = string(22, 8)
    """Port ID String."""

    dca = int16(30, scale_register=15, unit='A')
    """DC Current. DC current for the port."""

    dcv = uint16(31, scale_register=16, unit='V')
    """DC Voltage. DC voltage for the port."""

    dcw = int16(32, scale_register=17, unit='W')
    """DC Power. DC power for the port."""

    dc_wh_inj = uint64(33, scale_register=18, unit='Wh')
    """DC Energy Injected. Total cumulative DC energy injected for the port."""

    dc_wh_abs = uint64(37, scale_register=18, unit='Wh')
    """DC Energy Absorbed. Total cumulative DC energy absorbed for the port."""

    tmp = int16(41, scale_register=19, unit='C')
    """DC Port Temperature."""

    dc_sta = enum16(42, DCPortStatus)
    """DC Port Status."""

    dc_alrm = bitfield32(43, DCPortAlarm)
    """DC Port Alarm."""


class DERMeasureDC(SunSpecComponent):
    """SunSpec model 714: DER DC Measurement."""

    prt_alrms = bitfield32(2)
    """Port Alarms. Bitfield of ports with active alarms. Bit is 1 if port has an
    active alarm. Bit 0 is first port."""

    n_prt = uint16(4)
    """Number Of Ports. Number of DC ports."""

    dca = int16(5, scale_register=15, unit='A')
    """DC Current. Total DC current for all ports."""

    dcw = int16(6, scale_register=17, unit='W')
    """DC Power. Total DC power for all ports."""

    dc_wh_inj = uint64(7, scale_register=18, unit='Wh')
    """DC Energy Injected. Total cumulative DC energy injected for all ports."""

    dc_wh_abs = uint64(11, scale_register=18, unit='Wh')
    """DC Energy Absorbed. Total cumulative DC energy absorbed for all ports."""

    prt = repeating_group(uint16(4), DERMeasureDCPrt, stride=25)
