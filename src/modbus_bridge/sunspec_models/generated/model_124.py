"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_124.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    int16,
    uint16,
)


class StorCtlMod(IntFlag):
    CHARGE = 1 << 0
    DiSCHARGE = 1 << 1


class ChaSt(IntEnum):
    OFF = 1
    EMPTY = 2
    DISCHARGING = 3
    CHARGING = 4
    FULL = 5
    HOLDING = 6
    TESTING = 7


class ChaGriSet(IntEnum):
    PV = 0
    GRID = 1


class StorageBasic(SunSpecComponent):
    """SunSpec model 124: Storage."""

    w_cha_max = uint16(2, scale_register=18, writable=True, unit='W')
    """WChaMax. Setpoint for maximum charge."""

    w_cha_gra = uint16(3, scale_register=19, writable=True, unit='% WChaMax/sec')
    """WChaGra. Setpoint for maximum charging rate. Default is MaxChaRte."""

    w_dis_cha_gra = uint16(4, scale_register=19, writable=True, unit='% WChaMax/sec')
    """WDisChaGra. Setpoint for maximum discharge rate. Default is MaxDisChaRte."""

    stor_ctl_mod = bitfield16(5, StorCtlMod, writable=True)
    """StorCtl_Mod. Activate hold/discharge/charge storage control mode."""

    va_cha_max = uint16(6, scale_register=20, writable=True, unit='VA')
    """VAChaMax. Setpoint for maximum charging VA."""

    min_rsv_pct = uint16(7, scale_register=21, writable=True, unit='% WChaMax')
    """MinRsvPct. Setpoint for minimum reserve for storage as a percentage of the
    nominal maximum storage."""

    cha_state = uint16(8, scale_register=22, unit='% AhrRtg')
    """ChaState. Currently available energy as a percent of the capacity rating."""

    stor_aval = uint16(9, scale_register=23, unit='AH')
    """StorAval. State of charge (ChaState) minus storage reserve (MinRsvPct) times
    capacity rating (AhrRtg)."""

    in_bat_v = uint16(10, scale_register=24, unit='V')
    """InBatV. Internal battery voltage."""

    cha_st = enum16(11, ChaSt)
    """ChaSt. Charge status of storage device."""

    out_w_rte = int16(12, scale_register=25, writable=True, unit='% WDisChaMax')
    """OutWRte. Percent of max discharge rate."""

    in_w_rte = int16(13, scale_register=25, writable=True, unit=' % WChaMax')
    """InWRte. Percent of max charging rate."""

    in_out_w_rte_win_tms = uint16(14, writable=True, unit='Secs')
    """InOutWRte_WinTms. Time window for charge/discharge rate change."""

    in_out_w_rte_rvrt_tms = uint16(15, writable=True, unit='Secs')
    """InOutWRte_RvrtTms. Timeout period for charge/discharge rate."""

    in_out_w_rte_rmp_tms = uint16(16, writable=True, unit='Secs')
    """InOutWRte_RmpTms. Ramp time for moving from current setpoint to new setpoint."""

    cha_gri_set = enum16(17, ChaGriSet, writable=True)
