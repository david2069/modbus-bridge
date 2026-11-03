"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_202.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    int16,
)


class Events(IntFlag):
    M_EVENT_Power_Failure = 1 << 2
    M_EVENT_Under_Voltage = 1 << 3
    M_EVENT_Low_PF = 1 << 4
    M_EVENT_Over_Current = 1 << 5
    M_EVENT_Over_Voltage = 1 << 6
    M_EVENT_Missing_Sensor = 1 << 7
    M_EVENT_Reserved1 = 1 << 8
    M_EVENT_Reserved2 = 1 << 9
    M_EVENT_Reserved3 = 1 << 10
    M_EVENT_Reserved4 = 1 << 11
    M_EVENT_Reserved5 = 1 << 12
    M_EVENT_Reserved6 = 1 << 13
    M_EVENT_Reserved7 = 1 << 14
    M_EVENT_Reserved8 = 1 << 15
    M_EVENT_OEM01 = 1 << 16
    M_EVENT_OEM02 = 1 << 17
    M_EVENT_OEM03 = 1 << 18
    M_EVENT_OEM04 = 1 << 19
    M_EVENT_OEM05 = 1 << 20
    M_EVENT_OEM06 = 1 << 21
    M_EVENT_OEM07 = 1 << 22
    M_EVENT_OEM08 = 1 << 23
    M_EVENT_OEM09 = 1 << 24
    M_EVENT_OEM10 = 1 << 25
    M_EVENT_OEM11 = 1 << 26
    M_EVENT_OEM12 = 1 << 27
    M_EVENT_OEM13 = 1 << 28
    M_EVENT_OEM14 = 1 << 29
    M_EVENT_OEM15 = 1 << 30


class AcMeterAbn(SunSpecComponent):
    """SunSpec model 202: split single phase (ABN) meter."""

    a = int16(2, scale_register=6, unit='A')
    """Amps. Total AC Current."""

    aph_a = int16(3, scale_register=6, unit='A')
    """Amps PhaseA. Phase A Current."""

    aph_b = int16(4, scale_register=6, unit='A')
    """Amps PhaseB. Phase B Current."""

    aph_c = int16(5, scale_register=6, unit='A')
    """Amps PhaseC. Phase C Current."""

    ph_v = int16(7, scale_register=15, unit='V')
    """Voltage LN. Line to Neutral AC Voltage (average of active phases)."""

    ph_vph_a = int16(8, scale_register=15, unit='V')
    """Phase Voltage AN."""

    ph_vph_b = int16(9, scale_register=15, unit='V')
    """Phase Voltage BN."""

    ph_vph_c = int16(10, scale_register=15, unit='V')
    """Phase Voltage CN."""

    ppv = int16(11, scale_register=15, unit='V')
    """Voltage LL. Line to Line AC Voltage (average of active phases)."""

    ph_vph_ab = int16(12, scale_register=15, unit='V')
    """Phase Voltage AB."""

    ph_vph_bc = int16(13, scale_register=15, unit='V')
    """Phase Voltage BC."""

    ph_vph_ca = int16(14, scale_register=15, unit='V')
    """Phase Voltage CA."""

    hz = int16(16, scale_register=17, unit='Hz')
    """Hz. Frequency."""

    w = int16(18, scale_register=22, unit='W')
    """Watts. Total Real Power."""

    wph_a = int16(19, scale_register=22, unit='W')
    """Watts phase A."""

    wph_b = int16(20, scale_register=22, unit='W')
    """Watts phase B."""

    wph_c = int16(21, scale_register=22, unit='W')
    """Watts phase C."""

    va = int16(23, scale_register=27, unit='VA')
    """VA. AC Apparent Power."""

    v_aph_a = int16(24, scale_register=27, unit='VA')
    """VA phase A."""

    v_aph_b = int16(25, scale_register=27, unit='VA')
    """VA phase B."""

    v_aph_c = int16(26, scale_register=27, unit='VA')
    """VA phase C."""

    var = int16(28, scale_register=32, unit='var')
    """VAR. Reactive Power."""

    va_rph_a = int16(29, scale_register=32, unit='var')
    """VAR phase A."""

    va_rph_b = int16(30, scale_register=32, unit='var')
    """VAR phase B."""

    va_rph_c = int16(31, scale_register=32, unit='var')
    """VAR phase C."""

    pf = int16(33, scale_register=37, unit='Pct')
    """PF. Power Factor."""

    p_fph_a = int16(34, scale_register=37, unit='Pct')
    """PF phase A."""

    p_fph_b = int16(35, scale_register=37, unit='Pct')
    """PF phase B."""

    p_fph_c = int16(36, scale_register=37, unit='Pct')
    """PF phase C."""

    tot_wh_exp = acc32(38, scale_register=54, unit='Wh')
    """Total Watt-hours Exported. Total Real Energy Exported."""

    tot_wh_exp_ph_a = acc32(40, scale_register=54, unit='Wh')
    """Total Watt-hours Exported phase A."""

    tot_wh_exp_ph_b = acc32(42, scale_register=54, unit='Wh')
    """Total Watt-hours Exported phase B."""

    tot_wh_exp_ph_c = acc32(44, scale_register=54, unit='Wh')
    """Total Watt-hours Exported phase C."""

    tot_wh_imp = acc32(46, scale_register=54, unit='Wh')
    """Total Watt-hours Imported. Total Real Energy Imported."""

    tot_wh_imp_ph_a = acc32(48, scale_register=54, unit='Wh')
    """Total Watt-hours Imported phase A."""

    tot_wh_imp_ph_b = acc32(50, scale_register=54, unit='Wh')
    """Total Watt-hours Imported phase B."""

    tot_wh_imp_ph_c = acc32(52, scale_register=54, unit='Wh')
    """Total Watt-hours Imported phase C."""

    tot_v_ah_exp = acc32(55, scale_register=71, unit='VAh')
    """Total VA-hours Exported. Total Apparent Energy Exported."""

    tot_v_ah_exp_ph_a = acc32(57, scale_register=71, unit='VAh')
    """Total VA-hours Exported phase A."""

    tot_v_ah_exp_ph_b = acc32(59, scale_register=71, unit='VAh')
    """Total VA-hours Exported phase B."""

    tot_v_ah_exp_ph_c = acc32(61, scale_register=71, unit='VAh')
    """Total VA-hours Exported phase C."""

    tot_v_ah_imp = acc32(63, scale_register=71, unit='VAh')
    """Total VA-hours Imported. Total Apparent Energy Imported."""

    tot_v_ah_imp_ph_a = acc32(65, scale_register=71, unit='VAh')
    """Total VA-hours Imported phase A."""

    tot_v_ah_imp_ph_b = acc32(67, scale_register=71, unit='VAh')
    """Total VA-hours Imported phase B."""

    tot_v_ah_imp_ph_c = acc32(69, scale_register=71, unit='VAh')
    """Total VA-hours Imported phase C."""

    tot_v_arh_imp_q1 = acc32(72, scale_register=104, unit='varh')
    """Total VAR-hours Imported Q1. Total Reactive Energy Imported Quadrant 1."""

    tot_v_arh_imp_q1_ph_a = acc32(74, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q1 phase A."""

    tot_v_arh_imp_q1_ph_b = acc32(76, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q1 phase B."""

    tot_v_arh_imp_q1_ph_c = acc32(78, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q1 phase C."""

    tot_v_arh_imp_q2 = acc32(80, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q2. Total Reactive Power Imported Quadrant 2."""

    tot_v_arh_imp_q2_ph_a = acc32(82, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q2 phase A."""

    tot_v_arh_imp_q2_ph_b = acc32(84, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q2 phase B."""

    tot_v_arh_imp_q2_ph_c = acc32(86, scale_register=104, unit='varh')
    """Total VAr-hours Imported Q2 phase C."""

    tot_v_arh_exp_q3 = acc32(88, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q3. Total Reactive Power Exported Quadrant 3."""

    tot_v_arh_exp_q3_ph_a = acc32(90, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q3 phase A."""

    tot_v_arh_exp_q3_ph_b = acc32(92, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q3 phase B."""

    tot_v_arh_exp_q3_ph_c = acc32(94, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q3 phase C."""

    tot_v_arh_exp_q4 = acc32(96, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q4. Total Reactive Power Exported Quadrant 4."""

    tot_v_arh_exp_q4_ph_a = acc32(98, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase A."""

    tot_v_arh_exp_q4_ph_b = acc32(100, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase B."""

    tot_v_arh_exp_q4_ph_c = acc32(102, scale_register=104, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase C."""

    evt = bitfield32(105, Events)
    """Events. Meter Event Flags."""
