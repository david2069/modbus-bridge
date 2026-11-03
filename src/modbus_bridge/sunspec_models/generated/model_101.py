"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_101.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    enum16,
    int16,
    uint16,
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


class Event1(IntFlag):
    GROUND_FAULT = 1 << 0
    DC_OVER_VOLT = 1 << 1
    AC_DISCONNECT = 1 << 2
    DC_DISCONNECT = 1 << 3
    GRID_DISCONNECT = 1 << 4
    CABINET_OPEN = 1 << 5
    MANUAL_SHUTDOWN = 1 << 6
    OVER_TEMP = 1 << 7
    OVER_FREQUENCY = 1 << 8
    UNDER_FREQUENCY = 1 << 9
    AC_OVER_VOLT = 1 << 10
    AC_UNDER_VOLT = 1 << 11
    BLOWN_STRING_FUSE = 1 << 12
    UNDER_TEMP = 1 << 13
    MEMORY_LOSS = 1 << 14
    HW_TEST_FAILURE = 1 << 15


class InverterSinglePhase(SunSpecComponent):
    """SunSpec model 101: Inverter (Single Phase)."""

    a = uint16(2, scale_register=6, unit='A')
    """Amps. AC Current."""

    aph_a = uint16(3, scale_register=6, unit='A')
    """Amps PhaseA. Phase A Current."""

    aph_b = uint16(4, scale_register=6, unit='A')
    """Amps PhaseB. Phase B Current."""

    aph_c = uint16(5, scale_register=6, unit='A')
    """Amps PhaseC. Phase C Current."""

    pp_vph_ab = uint16(7, scale_register=13, unit='V')
    """Phase Voltage AB."""

    pp_vph_bc = uint16(8, scale_register=13, unit='V')
    """Phase Voltage BC."""

    pp_vph_ca = uint16(9, scale_register=13, unit='V')
    """Phase Voltage CA."""

    ph_vph_a = uint16(10, scale_register=13, unit='V')
    """Phase Voltage AN."""

    ph_vph_b = uint16(11, scale_register=13, unit='V')
    """Phase Voltage BN."""

    ph_vph_c = uint16(12, scale_register=13, unit='V')
    """Phase Voltage CN."""

    w = int16(14, scale_register=15, unit='W')
    """Watts. AC Power."""

    hz = uint16(16, scale_register=17, unit='Hz')
    """Hz. Line Frequency."""

    va = int16(18, scale_register=19, unit='VA')
    """VA. AC Apparent Power."""

    v_ar = int16(20, scale_register=21, unit='var')
    """VAr. AC Reactive Power."""

    pf = int16(22, scale_register=23, unit='Pct')
    """PF. AC Power Factor."""

    wh = acc32(24, scale_register=26, unit='Wh')
    """WattHours. AC Energy."""

    dca = uint16(27, scale_register=28, unit='A')
    """DC Amps. DC Current."""

    dcv = uint16(29, scale_register=30, unit='V')
    """DC Voltage."""

    dcw = int16(31, scale_register=32, unit='W')
    """DC Watts. DC Power."""

    tmp_cab = int16(33, scale_register=37, unit='C')
    """Cabinet Temperature."""

    tmp_snk = int16(34, scale_register=37, unit='C')
    """Heat Sink Temperature."""

    tmp_trns = int16(35, scale_register=37, unit='C')
    """Transformer Temperature."""

    tmp_ot = int16(36, scale_register=37, unit='C')
    """Other Temperature."""

    st = enum16(38, OperatingState)
    """Operating State."""

    st_vnd = enum16(39)
    """Vendor Operating State. Vendor specific operating state code."""

    evt1 = bitfield32(40, Event1)
    """Event1. Event fields."""

    evt2 = bitfield32(42)
    """Event Bitfield 2. Reserved for future use."""

    evt_vnd1 = bitfield32(44)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(46)
    """Vendor Event Bitfield 2. Vendor defined events."""

    evt_vnd3 = bitfield32(48)
    """Vendor Event Bitfield 3. Vendor defined events."""

    evt_vnd4 = bitfield32(50)
    """Vendor Event Bitfield 4. Vendor defined events."""
