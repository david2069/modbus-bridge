"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_211.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    float32,
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


class AcMeterAnOrAbFloat(SunSpecComponent):
    """SunSpec model 211: single phase (AN or AB) meter."""

    a = float32(2, unit='A')
    """Amps. Total AC Current."""

    aph_a = float32(4, unit='A')
    """Amps PhaseA. Phase A Current."""

    aph_b = float32(6, unit='A')
    """Amps PhaseB. Phase B Current."""

    aph_c = float32(8, unit='A')
    """Amps PhaseC. Phase C Current."""

    ph_v = float32(10, unit='V')
    """Voltage LN. Line to Neutral AC Voltage (average of active phases)."""

    ph_vph_a = float32(12, unit='V')
    """Phase Voltage AN."""

    ph_vph_b = float32(14, unit='V')
    """Phase Voltage BN."""

    ph_vph_c = float32(16, unit='V')
    """Phase Voltage CN."""

    ppv = float32(18, unit='V')
    """Voltage LL. Line to Line AC Voltage (average of active phases)."""

    pp_vph_ab = float32(20, unit='V')
    """Phase Voltage AB."""

    pp_vph_bc = float32(22, unit='V')
    """Phase Voltage BC."""

    pp_vph_ca = float32(24, unit='V')
    """Phase Voltage CA."""

    hz = float32(26, unit='Hz')
    """Hz. Frequency."""

    w = float32(28, unit='W')
    """Watts. Total Real Power."""

    wph_a = float32(30, unit='W')
    """Watts phase A."""

    wph_b = float32(32, unit='W')
    """Watts phase B."""

    wph_c = float32(34, unit='W')
    """Watts phase C."""

    va = float32(36, unit='VA')
    """VA. AC Apparent Power."""

    v_aph_a = float32(38, unit='VA')
    """VA phase A."""

    v_aph_b = float32(40, unit='VA')
    """VA phase B."""

    v_aph_c = float32(42, unit='VA')
    """VA phase C."""

    var = float32(44, unit='var')
    """VAR. Reactive Power."""

    va_rph_a = float32(46, unit='var')
    """VAR phase A."""

    va_rph_b = float32(48, unit='var')
    """VAR phase B."""

    va_rph_c = float32(50, unit='var')
    """VAR phase C."""

    pf = float32(52, unit='PF')
    """PF. Power Factor."""

    p_fph_a = float32(54, unit='PF')
    """PF phase A."""

    p_fph_b = float32(56, unit='PF')
    """PF phase B."""

    p_fph_c = float32(58, unit='PF')
    """PF phase C."""

    tot_wh_exp = float32(60, unit='Wh')
    """Total Watt-hours Exported. Total Real Energy Exported."""

    tot_wh_exp_ph_a = float32(62, unit='Wh')
    """Total Watt-hours Exported phase A."""

    tot_wh_exp_ph_b = float32(64, unit='Wh')
    """Total Watt-hours Exported phase B."""

    tot_wh_exp_ph_c = float32(66, unit='Wh')
    """Total Watt-hours Exported phase C."""

    tot_wh_imp = float32(68, unit='Wh')
    """Total Watt-hours Imported. Total Real Energy Imported."""

    tot_wh_imp_ph_a = float32(70, unit='Wh')
    """Total Watt-hours Imported phase A."""

    tot_wh_imp_ph_b = float32(72, unit='Wh')
    """Total Watt-hours Imported phase B."""

    tot_wh_imp_ph_c = float32(74, unit='Wh')
    """Total Watt-hours Imported phase C."""

    tot_v_ah_exp = float32(76, unit='VAh')
    """Total VA-hours Exported. Total Apparent Energy Exported."""

    tot_v_ah_exp_ph_a = float32(78, unit='VAh')
    """Total VA-hours Exported phase A."""

    tot_v_ah_exp_ph_b = float32(80, unit='VAh')
    """Total VA-hours Exported phase B."""

    tot_v_ah_exp_ph_c = float32(82, unit='VAh')
    """Total VA-hours Exported phase C."""

    tot_v_ah_imp = float32(84, unit='VAh')
    """Total VA-hours Imported. Total Apparent Energy Imported."""

    tot_v_ah_imp_ph_a = float32(86, unit='VAh')
    """Total VA-hours Imported phase A."""

    tot_v_ah_imp_ph_b = float32(88, unit='VAh')
    """Total VA-hours Imported phase B."""

    tot_v_ah_imp_ph_c = float32(90, unit='VAh')
    """Total VA-hours Imported phase C."""

    tot_v_arh_imp_q1 = float32(92, unit='varh')
    """Total VAR-hours Imported Q1. Total Reactive Energy Imported Quadrant 1."""

    tot_v_arh_imp_q1ph_a = float32(94, unit='varh')
    """Total VAr-hours Imported Q1 phase A."""

    tot_v_arh_imp_q1ph_b = float32(96, unit='varh')
    """Total VAr-hours Imported Q1 phase B."""

    tot_v_arh_imp_q1ph_c = float32(98, unit='varh')
    """Total VAr-hours Imported Q1 phase C."""

    tot_v_arh_imp_q2 = float32(100, unit='varh')
    """Total VAr-hours Imported Q2. Total Reactive Power Imported Quadrant 2."""

    tot_v_arh_imp_q2ph_a = float32(102, unit='varh')
    """Total VAr-hours Imported Q2 phase A."""

    tot_v_arh_imp_q2ph_b = float32(104, unit='varh')
    """Total VAr-hours Imported Q2 phase B."""

    tot_v_arh_imp_q2ph_c = float32(106, unit='varh')
    """Total VAr-hours Imported Q2 phase C."""

    tot_v_arh_exp_q3 = float32(108, unit='varh')
    """Total VAr-hours Exported Q3. Total Reactive Power Exported Quadrant 3."""

    tot_v_arh_exp_q3ph_a = float32(110, unit='varh')
    """Total VAr-hours Exported Q3 phase A."""

    tot_v_arh_exp_q3ph_b = float32(112, unit='varh')
    """Total VAr-hours Exported Q3 phase B."""

    tot_v_arh_exp_q3ph_c = float32(114, unit='varh')
    """Total VAr-hours Exported Q3 phase C."""

    tot_v_arh_exp_q4 = float32(116, unit='varh')
    """Total VAr-hours Exported Q4. Total Reactive Power Exported Quadrant 4."""

    tot_v_arh_exp_q4ph_a = float32(118, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase A."""

    tot_v_arh_exp_q4ph_b = float32(120, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase B."""

    tot_v_arh_exp_q4ph_c = float32(122, unit='varh')
    """Total VAr-hours Exported Q4 Imported phase C."""

    evt = bitfield32(124, Events)
    """Events. Meter Event Flags."""
