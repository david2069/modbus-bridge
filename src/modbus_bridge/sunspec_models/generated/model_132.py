"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_132.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    int16,
    model_length_group,
    string,
    uint16,
)


class DeptRef(IntEnum):
    WMax = 1
    WAval = 2


class ReadOnly(IntEnum):
    READWRITE = 0
    READONLY = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class VoltWattCurve(Component):
    """One 'curve' block of SunSpec model 132."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    dept_ref = enum16(13, DeptRef, writable=True)
    """DeptRef. Defines the meaning of the Watts DeptRef. 1=% WMax 2=% WAvail."""

    v1 = uint16(14, scale_register=9, writable=True, unit='% VRef')
    """V1. Point 1 Volts."""

    w1 = int16(15, scale_register=10, writable=True, unit='% VRef')
    """W1. Point 1 Watts."""

    v2 = uint16(16, scale_register=9, writable=True, unit='% VRef')
    """V2. Point 2 Volts."""

    w2 = int16(17, scale_register=10, writable=True, unit='% VRef')
    """W2. Point 2 Watts."""

    v3 = uint16(18, scale_register=9, writable=True, unit='% VRef')
    """V3. Point 3 Volts."""

    w3 = int16(19, scale_register=10, writable=True, unit='% VRef')
    """W3. Point 3 Watts."""

    v4 = uint16(20, scale_register=9, writable=True, unit='% VRef')
    """V4. Point 4 Volts."""

    w4 = int16(21, scale_register=10, writable=True, unit='% VRef')
    """W4. Point 4 Watts."""

    v5 = uint16(22, scale_register=9, writable=True, unit='% VRef')
    """V5. Point 5 Volts."""

    w5 = int16(23, scale_register=10, writable=True, unit='% VRef')
    """W5. Point 5 Watts."""

    v6 = uint16(24, scale_register=9, writable=True, unit='% VRef')
    """V6. Point 6 Volts."""

    w6 = int16(25, scale_register=10, writable=True, unit='% VRef')
    """W6. Point 6 Watts."""

    v7 = uint16(26, scale_register=9, writable=True, unit='% VRef')
    """V7. Point 7 Volts."""

    w7 = int16(27, scale_register=10, writable=True, unit='% VRef')
    """W7. Point 7 Watts."""

    v8 = uint16(28, scale_register=9, writable=True, unit='% VRef')
    """V8. Point 8 Volts."""

    w8 = int16(29, scale_register=10, writable=True, unit='% VRef')
    """W8. Point 8 Watts."""

    v9 = uint16(30, scale_register=9, writable=True, unit='% VRef')
    """V9. Point 9 Volts."""

    w9 = int16(31, scale_register=10, writable=True, unit='% VRef')
    """W9. Point 9 Watts."""

    v10 = uint16(32, scale_register=9, writable=True, unit='% VRef')
    """V10. Point 10 Volts."""

    w10 = int16(33, scale_register=10, writable=True, unit='% VRef')
    """W10. Point 10 Watts."""

    v11 = uint16(34, scale_register=9, writable=True, unit='% VRef')
    """V11. Point 11 Volts."""

    w11 = int16(35, scale_register=10, writable=True, unit='% VRef')
    """W11. Point 11 Watts."""

    v12 = uint16(36, scale_register=9, writable=True, unit='% VRef')
    """V12. Point 12 Volts."""

    w12 = int16(37, scale_register=10, writable=True, unit='% VRef')
    """W12. Point 12 Watts."""

    v13 = uint16(38, scale_register=9, writable=True, unit='% VRef')
    """V13. Point 13 Volts."""

    w13 = int16(39, scale_register=10, writable=True, unit='% VRef')
    """W13. Point 13 Watts."""

    v14 = uint16(40, scale_register=9, writable=True, unit='% VRef')
    """V14. Point 14 Volts."""

    w14 = int16(41, scale_register=10, writable=True, unit='% VRef')
    """W14. Point 14 Watts."""

    v15 = uint16(42, scale_register=9, writable=True, unit='% VRef')
    """V15. Point 15 Volts."""

    w15 = int16(43, scale_register=10, writable=True, unit='% VRef')
    """W15. Point 15 Watts."""

    v16 = uint16(44, scale_register=9, writable=True, unit='% VRef')
    """V16. Point 16 Volts."""

    w16 = int16(45, scale_register=10, writable=True, unit='% VRef')
    """W16. Point 16 Watts."""

    v17 = uint16(46, scale_register=9, writable=True, unit='% VRef')
    """V17. Point 17 Volts."""

    w17 = int16(47, scale_register=10, writable=True, unit='% VRef')
    """W17. Point 17 Watts."""

    v18 = uint16(48, scale_register=9, writable=True, unit='% VRef')
    """V18. Point 18 Volts."""

    w18 = int16(49, scale_register=10, writable=True, unit='% VRef')
    """W18. Point 18 Watts."""

    v19 = uint16(50, scale_register=9, writable=True, unit='% VRef')
    """V19. Point 19 Volts."""

    w19 = int16(51, scale_register=10, writable=True, unit='% VRef')
    """W19. Point 19 Watts."""

    v20 = uint16(52, scale_register=9, writable=True, unit='% VRef')
    """V20. Point 20 Volts."""

    w20 = int16(53, scale_register=10, writable=True, unit='% VRef')
    """W20. Point 20 Watts."""

    crv_nam = string(54, 8, writable=True)
    """CrvNam. Optional description for curve."""

    rmp_pt1_tms = uint16(62, writable=True, unit='Secs')
    """RmpPt1Tms. The time of the PT1 in seconds (time to accomplish a change of
    95%)."""

    rmp_dec_tmm = uint16(63, scale_register=11, writable=True, unit='% WMax/min')
    """RmpDecTmm. The maximum rate at which the watt value may be reduced in response
    to changes in the voltage value."""

    rmp_inc_tmm = uint16(64, scale_register=11, writable=True, unit='% WMax/min')
    """RmpIncTmm. The maximum rate at which the watt value may be increased in
    response to changes in the voltage value."""

    read_only = enum16(65, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class VoltWatt(SunSpecComponent):
    """SunSpec model 132: Volt-Watt."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is Volt-Watt control active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for volt-watt change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for volt-watt curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend min. 4)."""

    n_pt = uint16(8)
    """NPt. Number of points in array (maximum 20)."""

    curve = model_length_group(VoltWattCurve, start=12, stride=54)
