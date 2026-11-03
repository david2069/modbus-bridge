"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_122.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc64,
    bitfield16,
    bitfield32,
    int16,
    string,
    uint16,
    uint32,
)


class PVConn(IntFlag):
    CONNECTED = 1 << 0
    AVAILABLE = 1 << 1
    OPERATING = 1 << 2
    TEST = 1 << 3


class StorConn(IntFlag):
    CONNECTED = 1 << 0
    AVAILABLE = 1 << 1
    OPERATING = 1 << 2
    TEST = 1 << 3


class ECPConn(IntFlag):
    DISCONNECTED = 1 << 0
    CONNECTED = 1 << 1


class StSetLimMsk(IntFlag):
    WMax = 1 << 0
    VAMax = 1 << 1
    VArAval = 1 << 2
    VArMaxQ1 = 1 << 3
    VArMaxQ2 = 1 << 4
    VArMaxQ3 = 1 << 5
    VArMaxQ4 = 1 << 6
    PFMinQ1 = 1 << 7
    PFMinQ2 = 1 << 8
    PFMinQ3 = 1 << 9
    PFMinQ4 = 1 << 10


class StActCtl(IntFlag):
    FixedW = 1 << 0
    FixedVAR = 1 << 1
    FixedPF = 1 << 2
    Volt_VAr = 1 << 3
    Freq_Watt_Param = 1 << 4
    Freq_Watt_Curve = 1 << 5
    Dyn_Reactive_Current = 1 << 6
    LVRT = 1 << 7
    HVRT = 1 << 8
    Watt_PF = 1 << 9
    Volt_Watt = 1 << 10
    Scheduled = 1 << 12
    LFRT = 1 << 13
    HFRT = 1 << 14


class RtSt(IntFlag):
    LVRT_ACTIVE = 1 << 0
    HVRT_ACTIVE = 1 << 1
    LFRT_ACTIVE = 1 << 2
    HFRT_ACTIVE = 1 << 3


class Status(SunSpecComponent):
    """SunSpec model 122: Measurements_Status."""

    pv_conn = bitfield16(2, PVConn)
    """PVConn. PV inverter present/available status."""

    stor_conn = bitfield16(3, StorConn)
    """StorConn. Storage inverter present/available status."""

    ecp_conn = bitfield16(4, ECPConn)
    """ECPConn. ECP connection status: disconnected=0 connected=1."""

    act_wh = acc64(5, unit='Wh')
    """ActWh. AC lifetime active (real) energy output."""

    act_v_ah = acc64(9, unit='VAh')
    """ActVAh. AC lifetime apparent energy output."""

    act_v_arh_q1 = acc64(13, unit='varh')
    """ActVArhQ1. AC lifetime reactive energy output in quadrant 1."""

    act_v_arh_q2 = acc64(17, unit='varh')
    """ActVArhQ2. AC lifetime reactive energy output in quadrant 2."""

    act_v_arh_q3 = acc64(21, unit='varh')
    """ActVArhQ3. AC lifetime negative energy output in quadrant 3."""

    act_v_arh_q4 = acc64(25, unit='varh')
    """ActVArhQ4. AC lifetime reactive energy output in quadrant 4."""

    v_ar_aval = int16(29, scale_register=30, unit='var')
    """VArAval. Amount of VARs available without impacting watts output."""

    w_aval = uint16(31, scale_register=32, unit='W')
    """WAval. Amount of Watts available."""

    st_set_lim_msk = bitfield32(33, StSetLimMsk)
    """StSetLimMsk. Setpoint limit(s) reached."""

    st_act_ctl = bitfield32(35, StActCtl)
    """StActCtl. Which inverter controls are currently active."""

    tm_src = string(37, 4)
    """TmSrc. Source of time synchronization."""

    tms = uint32(41, unit='Secs')
    """Tms. Seconds since 01-01-2000 00:00 UTC."""

    rt_st = bitfield16(43, RtSt)
    """RtSt. Active ride-through status."""

    ris = uint16(44, scale_register=45, unit='ohms')
    """Ris. Isolation resistance."""
