"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_123.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
    uint16,
)


class Conn(IntEnum):
    DISCONNECT = 0
    CONNECT = 1


class WMaxLimEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class OutPFSetEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class VArPctMod(IntEnum):
    NONE = 0
    WMax = 1
    VArMax = 2
    VArAval = 3


class VArPctEna(IntEnum):
    DISABLED = 0
    ENABLED = 1


class Controls(SunSpecComponent):
    """SunSpec model 123: Immediate Controls."""

    conn_win_tms = uint16(2, writable=True, unit='Secs')
    """Conn_WinTms. Time window for connect/disconnect."""

    conn_rvrt_tms = uint16(3, writable=True, unit='Secs')
    """Conn_RvrtTms. Timeout period for connect/disconnect."""

    conn = enum16(4, Conn, writable=True)
    """Conn. Connection control."""

    w_max_lim_pct = uint16(5, scale_register=23, writable=True, unit='% WMax')
    """WMaxLimPct. Set power output to specified level."""

    w_max_lim_pct_win_tms = uint16(6, writable=True, unit='Secs')
    """WMaxLimPct_WinTms. Time window for power limit change."""

    w_max_lim_pct_rvrt_tms = uint16(7, writable=True, unit='Secs')
    """WMaxLimPct_RvrtTms. Timeout period for power limit."""

    w_max_lim_pct_rmp_tms = uint16(8, writable=True, unit='Secs')
    """WMaxLimPct_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    w_max_lim_ena = enum16(9, WMaxLimEna, writable=True)
    """WMaxLim_Ena. Throttle enable/disable control."""

    out_pf_set = int16(10, scale_register=24, writable=True, unit='cos()')
    """OutPFSet. Set power factor to specific value - cosine of angle."""

    out_pf_set_win_tms = uint16(11, writable=True, unit='Secs')
    """OutPFSet_WinTms. Time window for power factor change."""

    out_pf_set_rvrt_tms = uint16(12, writable=True, unit='Secs')
    """OutPFSet_RvrtTms. Timeout period for power factor."""

    out_pf_set_rmp_tms = uint16(13, writable=True, unit='Secs')
    """OutPFSet_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    out_pf_set_ena = enum16(14, OutPFSetEna, writable=True)
    """OutPFSet_Ena. Fixed power factor enable/disable control."""

    v_ar_w_max_pct = int16(15, scale_register=25, writable=True, unit='% WMax')
    """VArWMaxPct. Reactive power in percent of WMax."""

    v_ar_max_pct = int16(16, scale_register=25, writable=True, unit='% VArMax')
    """VArMaxPct. Reactive power in percent of VArMax."""

    v_ar_aval_pct = int16(17, scale_register=25, writable=True, unit='% VArAval')
    """VArAvalPct. Reactive power in percent of VArAval."""

    v_ar_pct_win_tms = uint16(18, writable=True, unit='Secs')
    """VArPct_WinTms. Time window for VAR limit change."""

    v_ar_pct_rvrt_tms = uint16(19, writable=True, unit='Secs')
    """VArPct_RvrtTms. Timeout period for VAR limit."""

    v_ar_pct_rmp_tms = uint16(20, writable=True, unit='Secs')
    """VArPct_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    v_ar_pct_mod = enum16(21, VArPctMod, writable=True)
    """VArPct_Mod. VAR percent limit mode."""

    v_ar_pct_ena = enum16(22, VArPctEna, writable=True)
    """VArPct_Ena. Percent limit VAr enable/disable control."""
