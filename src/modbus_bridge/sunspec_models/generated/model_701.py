"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_701.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    string,
    uint16,
    uint32,
    uint64,
)


class ACWiringType(IntEnum):
    SINGLE_PHASE = 0
    SPLIT_PHASE = 1
    THREE_PHASE = 2


class OperatingState(IntEnum):
    OFF = 0
    ON = 1


class InverterState(IntEnum):
    OFF = 0
    SLEEPING = 1
    STARTING = 2
    RUNNING = 3
    THROTTLED = 4
    SHUTTING_DOWN = 5
    FAULT = 6
    STANDBY = 7


class GridConnectionState(IntEnum):
    DISCONNECTED = 0
    CONNECTED = 1


class AlarmBitfield(IntFlag):
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
    MANUFACTURER_ALRM = 1 << 16


class DEROperationalCharacteristics(IntFlag):
    GRID_FOLLOWING = 1 << 0
    GRID_FORMING = 1 << 1
    PV_CLIPPED = 1 << 2


class ThrottleSourceInformation(IntFlag):
    MAX_W = 1 << 0
    FIXED_W = 1 << 1
    FIXED_VAR = 1 << 2
    FIXED_PF = 1 << 3
    VOLT_VAR = 1 << 4
    FREQ_WATT = 1 << 5
    DYN_REACT_CURR = 1 << 6
    LVRT = 1 << 7
    HVRT = 1 << 8
    WATT_VAR = 1 << 9
    VOLT_WATT = 1 << 10
    SCHEDULED = 1 << 11
    LFRT = 1 << 12
    HFRT = 1 << 13
    DERATED = 1 << 14


class DERMeasureAC(SunSpecComponent):
    """SunSpec model 701: DER AC Measurement."""

    ac_type = enum16(2, ACWiringType)
    """AC Wiring Type."""

    st = enum16(3, OperatingState)
    """Operating State. Operating state of the DER."""

    inv_st = enum16(4, InverterState)
    """Inverter State."""

    conn_st = enum16(5, GridConnectionState)
    """Grid Connection State. Grid connection state of the DER."""

    alrm = bitfield32(6, AlarmBitfield)
    """Alarm Bitfield. Active alarms for the DER."""

    der_mode = bitfield32(8, DEROperationalCharacteristics)
    """DER Operational Characteristics. Current operational characteristics of the
    DER."""

    w = int16(10, scale_register=116, unit='W')
    """Active Power. Total active power. Active power is positive for DER generation
    and negative for absorption."""

    va = int16(11, scale_register=118, unit='VA')
    """Apparent Power. Total apparent power."""

    var = int16(12, scale_register=119, unit='Var')
    """Reactive Power. Total reactive power."""

    pf = int16(13, scale_register=117)
    """Power Factor. Power factor. The sign of power factor should be the sign of
    active power."""

    a = int16(14, scale_register=113, unit='A')
    """Total AC Current."""

    llv = uint16(15, scale_register=114, unit='V')
    """Voltage LL. Line to line AC voltage as an average of active phases."""

    lnv = uint16(16, scale_register=114, unit='V')
    """Voltage LN. Line to neutral AC voltage as an average of active phases."""

    hz = uint32(17, scale_register=115, unit='Hz')
    """Frequency. AC frequency."""

    tot_wh_inj = uint64(19, scale_register=120, unit='Wh')
    """Total Energy Injected. Total active energy injected (Quadrants 1 & 4)."""

    tot_wh_abs = uint64(23, scale_register=120, unit='Wh')
    """Total Energy Absorbed. Total active energy absorbed (Quadrants 2 & 3)."""

    tot_varh_inj = uint64(27, scale_register=121, unit='Varh')
    """Total Reactive Energy Inj. Total reactive energy injected (Quadrants 1 & 2)."""

    tot_varh_abs = uint64(31, scale_register=121, unit='Varh')
    """Total Reactive Energy Abs. Total reactive energy absorbed (Quadrants 3 & 4)."""

    tmp_amb = int16(35, scale_register=122, unit='C')
    """Ambient Temperature."""

    tmp_cab = int16(36, scale_register=122, unit='C')
    """Cabinet Temperature."""

    tmp_snk = int16(37, scale_register=122, unit='C')
    """Heat Sink Temperature."""

    tmp_trns = int16(38, scale_register=122, unit='C')
    """Transformer Temperature."""

    tmp_sw = int16(39, scale_register=122, unit='C')
    """IGBT/MOSFET Temperature."""

    tmp_ot = int16(40, scale_register=122, unit='C')
    """Other Temperature."""

    wl1 = int16(41, scale_register=116, unit='W')
    """Watts L1. Active power L1."""

    val1 = int16(42, scale_register=118, unit='VA')
    """VA L1. Apparent power L1."""

    var_l1 = int16(43, scale_register=119, unit='Var')
    """Var L1. Reactive power L1."""

    pfl1 = int16(44, scale_register=117)
    """PF L1. Power factor phase L1."""

    al1 = int16(45, scale_register=113, unit='A')
    """Amps L1. Current phase L1."""

    vl1_l2 = uint16(46, scale_register=114, unit='V')
    """Phase Voltage L1-L2."""

    vl1 = uint16(47, scale_register=114, unit='V')
    """Phase Voltage L1-N."""

    tot_wh_inj_l1 = uint64(48, scale_register=120, unit='Wh')
    """Total Watt-Hours Inj L1. Total active energy injected L1."""

    tot_wh_abs_l1 = uint64(52, scale_register=120, unit='Wh')
    """Total Watt-Hours Abs L1. Total active energy absorbed L1."""

    tot_varh_inj_l1 = uint64(56, scale_register=121, unit='Varh')
    """Total Var-Hours Inj L1. Total reactive energy injected L1."""

    tot_varh_abs_l1 = uint64(60, scale_register=121, unit='Varh')
    """Total Var-Hours Abs L1. Total reactive energy absorbed L1."""

    wl2 = int16(64, scale_register=116, unit='W')
    """Watts L2. Active power L2."""

    val2 = int16(65, scale_register=118, unit='VA')
    """VA L2. Apparent power L2."""

    var_l2 = int16(66, scale_register=119, unit='Var')
    """Var L2. Reactive power L2."""

    pfl2 = int16(67, scale_register=117)
    """PF L2. Power factor L2."""

    al2 = int16(68, scale_register=113, unit='A')
    """Amps L2. Current L2."""

    vl2_l3 = uint16(69, scale_register=114, unit='V')
    """Phase Voltage L2-L3."""

    vl2 = uint16(70, scale_register=114, unit='V')
    """Phase Voltage L2-N."""

    tot_wh_inj_l2 = uint64(71, scale_register=120, unit='Wh')
    """Total Watt-Hours Inj L2. Total active energy injected L2."""

    tot_wh_abs_l2 = uint64(75, scale_register=120, unit='Wh')
    """Total Watt-Hours Abs L2. Total active energy absorbed L2."""

    tot_varh_inj_l2 = uint64(79, scale_register=121, unit='Varh')
    """Total Var-Hours Inj L2. Total reactive energy injected L2."""

    tot_varh_abs_l2 = uint64(83, scale_register=121, unit='Varh')
    """Total Var-Hours Abs L2. Total reactive energy absorbed L2."""

    wl3 = int16(87, scale_register=116, unit='W')
    """Watts L3. Active power L3."""

    val3 = int16(88, scale_register=118, unit='VA')
    """VA L3. Apparent power L3."""

    var_l3 = int16(89, scale_register=119, unit='Var')
    """Var L3. Reactive power L3."""

    pfl3 = int16(90, scale_register=117)
    """PF L3. Power factor L3."""

    al3 = int16(91, scale_register=113, unit='A')
    """Amps L3. Current L3."""

    vl3_l1 = uint16(92, scale_register=114, unit='V')
    """Phase Voltage L3-L1."""

    vl3 = uint16(93, scale_register=114, unit='V')
    """Phase Voltage L3-N."""

    tot_wh_inj_l3 = uint64(94, scale_register=120, unit='Wh')
    """Total Watt-Hours Inj L3. Total active energy injected L3."""

    tot_wh_abs_l3 = uint64(98, scale_register=120, unit='Wh')
    """Total Watt-Hours Abs L3. Total active energy absorbed L3."""

    tot_varh_inj_l3 = uint64(102, scale_register=121, unit='Varh')
    """Total Var-Hours Inj L3. Total reactive energy injected L3."""

    tot_varh_abs_l3 = uint64(106, scale_register=121, unit='Varh')
    """Total Var-Hours Abs L3. Total reactive energy absorbed L3."""

    throt_pct = uint16(110, unit='Pct')
    """Throttling In Pct. Throttling in pct of maximum active power."""

    throt_src = bitfield32(111, ThrottleSourceInformation)
    """Throttle Source Information. Active throttling source."""

    mn_alrm_info = string(123, 32)
    """Manufacturer Alarm Info. Manufacturer alarm information. Valid if
    MANUFACTURER_ALRM indication is active."""
