"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_121.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
    uint16,
)


class VArAct(IntEnum):
    SWITCH = 1
    MAINTAIN = 2


class ClcTotVA(IntEnum):
    VECTOR = 1
    ARITHMETIC = 2


class ConnPh(IntEnum):
    A = 1
    B = 2
    C = 3


class Settings(SunSpecComponent):
    """SunSpec model 121: Basic Settings."""

    w_max = uint16(2, scale_register=22, writable=True, unit='W')
    """WMax. Setting for maximum power output. Default to WRtg."""

    v_ref = uint16(3, scale_register=23, writable=True, unit='V')
    """VRef. Voltage at the PCC."""

    v_ref_ofs = int16(4, scale_register=24, writable=True, unit='V')
    """VRefOfs. Offset from PCC to inverter."""

    v_max = uint16(5, scale_register=25, writable=True, unit='V')
    """VMax. Setpoint for maximum voltage."""

    v_min = uint16(6, scale_register=25, writable=True, unit='V')
    """VMin. Setpoint for minimum voltage."""

    va_max = uint16(7, scale_register=26, writable=True, unit='VA')
    """VAMax. Setpoint for maximum apparent power. Default to VARtg."""

    v_ar_max_q1 = int16(8, scale_register=27, writable=True, unit='var')
    """VArMaxQ1. Setting for maximum reactive power in quadrant 1. Default to
    VArRtgQ1."""

    v_ar_max_q2 = int16(9, scale_register=27, writable=True, unit='var')
    """VArMaxQ2. Setting for maximum reactive power in quadrant 2. Default to
    VArRtgQ2."""

    v_ar_max_q3 = int16(10, scale_register=27, writable=True, unit='var')
    """VArMaxQ3. Setting for maximum reactive power in quadrant 3. Default to
    VArRtgQ3."""

    v_ar_max_q4 = int16(11, scale_register=27, writable=True, unit='var')
    """VArMaxQ4. Setting for maximum reactive power in quadrant 4. Default to
    VArRtgQ4."""

    w_gra = uint16(12, scale_register=28, writable=True, unit='% WMax/sec')
    """WGra. Default ramp rate of change of active power due to command or internal
    action."""

    pf_min_q1 = int16(13, scale_register=29, writable=True, unit='cos()')
    """PFMinQ1. Setpoint for minimum power factor value in quadrant 1. Default to
    PFRtgQ1."""

    pf_min_q2 = int16(14, scale_register=29, writable=True, unit='cos()')
    """PFMinQ2. Setpoint for minimum power factor value in quadrant 2. Default to
    PFRtgQ2."""

    pf_min_q3 = int16(15, scale_register=29, writable=True, unit='cos()')
    """PFMinQ3. Setpoint for minimum power factor value in quadrant 3. Default to
    PFRtgQ3."""

    pf_min_q4 = int16(16, scale_register=29, writable=True, unit='cos()')
    """PFMinQ4. Setpoint for minimum power factor value in quadrant 4. Default to
    PFRtgQ4."""

    v_ar_act = enum16(17, VArAct, writable=True)
    """VArAct. VAR action on change between charging and discharging: 1=switch
    2=maintain VAR characterization."""

    clc_tot_va = enum16(18, ClcTotVA, writable=True)
    """ClcTotVA. Calculation method for total apparent power. 1=vector 2=arithmetic."""

    max_rmp_rte = uint16(19, scale_register=30, writable=True, unit='% WGra')
    """MaxRmpRte. Setpoint for maximum ramp rate as percentage of nominal maximum
    ramp rate. This setting will limit the rate that watts delivery to the grid
    can increase or decrease in response to intermittent PV generation."""

    ecp_nom_hz = uint16(20, scale_register=31, writable=True, unit='Hz')
    """ECPNomHz. Setpoint for nominal frequency at the ECP."""

    conn_ph = enum16(21, ConnPh, writable=True)
    """ConnPh. Identity of connected phase for single phase inverters. A=1 B=2 C=3."""
