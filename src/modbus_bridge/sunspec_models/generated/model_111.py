"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_111.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    float32,
)


class OperatingState(IntEnum):
    ggOFF = 1
    ggSLEEPING = 2
    ggSTARTING = 3
    ggMPPT = 4
    ggTHROTTLED = 5
    ggSHUTTING_DOWN = 6
    ggFAULT = 7
    ggSTANDBY = 8


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


class InverterSinglePhaseFloat(SunSpecComponent):
    """SunSpec model 111: Inverter (Single Phase) FLOAT."""

    a = float32(2, unit='A')
    """Amps. AC Current."""

    aph_a = float32(4, unit='A')
    """Amps PhaseA. Phase A Current."""

    aph_b = float32(6, unit='A')
    """Amps PhaseB. Phase B Current."""

    aph_c = float32(8, unit='A')
    """Amps PhaseC. Phase C Current."""

    pp_vph_ab = float32(10, unit='V')
    """Phase Voltage AB."""

    pp_vph_bc = float32(12, unit='V')
    """Phase Voltage BC."""

    pp_vph_ca = float32(14, unit='V')
    """Phase Voltage CA."""

    ph_vph_a = float32(16, unit='V')
    """Phase Voltage AN."""

    ph_vph_b = float32(18, unit='V')
    """Phase Voltage BN."""

    ph_vph_c = float32(20, unit='V')
    """Phase Voltage CN."""

    w = float32(22, unit='W')
    """Watts. AC Power."""

    hz = float32(24, unit='Hz')
    """Hz. Line Frequency."""

    va = float32(26, unit='VA')
    """VA. AC Apparent Power."""

    v_ar = float32(28, unit='var')
    """VAr. AC Reactive Power."""

    pf = float32(30, unit='Pct')
    """PF. AC Power Factor."""

    wh = float32(32, unit='Wh')
    """WattHours. AC Energy."""

    dca = float32(34, unit='A')
    """DC Amps. DC Current."""

    dcv = float32(36, unit='V')
    """DC Voltage."""

    dcw = float32(38, unit='W')
    """DC Watts. DC Power."""

    tmp_cab = float32(40, unit='C')
    """Cabinet Temperature."""

    tmp_snk = float32(42, unit='C')
    """Heat Sink Temperature."""

    tmp_trns = float32(44, unit='C')
    """Transformer Temperature."""

    tmp_ot = float32(46, unit='C')
    """Other Temperature."""

    st = enum16(48, OperatingState)
    """Operating State."""

    st_vnd = enum16(49)
    """Vendor Operating State. Vendor specific operating state code."""

    evt1 = bitfield32(50, Event1)
    """Event1. Event fields."""

    evt2 = bitfield32(52)
    """Event Bitfield 2. Reserved for future use."""

    evt_vnd1 = bitfield32(54)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(56)
    """Vendor Event Bitfield 2. Vendor defined events."""

    evt_vnd3 = bitfield32(58)
    """Vendor Event Bitfield 3. Vendor defined events."""

    evt_vnd4 = bitfield32(60)
    """Vendor Event Bitfield 4. Vendor defined events."""
