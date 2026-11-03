"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_126.json)

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
    VArMax = 2
    VArAval = 3


class ReadOnly(IntEnum):
    READWRITE = 0
    READONLY = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class VoltVarCurve(Component):
    """One 'curve' block of SunSpec model 126."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    dept_ref = enum16(13, DeptRef, writable=True)
    """DeptRef. Meaning of dependent variable: 1=%WMax 2=%VArMax 3=%VArAval."""

    v1 = uint16(14, scale_register=9, writable=True, unit='% VRef')
    """V1. Point 1 Volts."""

    v_ar1 = int16(15, scale_register=10, writable=True)
    """VAr1. Point 1 VARs."""

    v2 = uint16(16, scale_register=9, writable=True, unit='% VRef')
    """V2. Point 2 Volts."""

    v_ar2 = int16(17, scale_register=10, writable=True)
    """VAr2. Point 2 VARs."""

    v3 = uint16(18, scale_register=9, writable=True, unit='% VRef')
    """V3. Point 3 Volts."""

    v_ar3 = int16(19, scale_register=10, writable=True)
    """VAr3. Point 3 VARs."""

    v4 = uint16(20, scale_register=9, writable=True, unit='% VRef')
    """V4. Point 4 Volts."""

    v_ar4 = int16(21, scale_register=10, writable=True)
    """VAr4. Point 4 VARs."""

    v5 = uint16(22, scale_register=9, writable=True, unit='% VRef')
    """V5. Point 5 Volts."""

    v_ar5 = int16(23, scale_register=10, writable=True)
    """VAr5. Point 5 VARs."""

    v6 = uint16(24, scale_register=9, writable=True, unit='% VRef')
    """V6. Point 6 Volts."""

    v_ar6 = int16(25, scale_register=10, writable=True)
    """VAr6. Point 6 VARs."""

    v7 = uint16(26, scale_register=9, writable=True, unit='% VRef')
    """V7. Point 7 Volts."""

    v_ar7 = int16(27, scale_register=10, writable=True)
    """VAr7. Point 7 VARs."""

    v8 = uint16(28, scale_register=9, writable=True, unit='% VRef')
    """V8. Point 8 Volts."""

    v_ar8 = int16(29, scale_register=10, writable=True)
    """VAr8. Point 8 VARs."""

    v9 = uint16(30, scale_register=9, writable=True, unit='% VRef')
    """V9. Point 9 Volts."""

    v_ar9 = int16(31, scale_register=10, writable=True)
    """VAr9. Point 9 VARs."""

    v10 = uint16(32, scale_register=9, writable=True, unit='% VRef')
    """V10. Point 10 Volts."""

    v_ar10 = int16(33, scale_register=10, writable=True)
    """VAr10. Point 10 VARs."""

    v11 = uint16(34, scale_register=9, writable=True, unit='% VRef')
    """V11. Point 11 Volts."""

    v_ar11 = int16(35, scale_register=10, writable=True)
    """VAr11. Point 11 VARs."""

    v12 = uint16(36, scale_register=9, writable=True, unit='% VRef')
    """V12. Point 12 Volts."""

    v_ar12 = int16(37, scale_register=10, writable=True)
    """VAr12. Point 12 VARs."""

    v13 = uint16(38, scale_register=9, writable=True, unit='% VRef')
    """V13. Point 13 Volts."""

    v_ar13 = int16(39, scale_register=10, writable=True)
    """VAr13. Point 13 VARs."""

    v14 = uint16(40, scale_register=9, writable=True, unit='% VRef')
    """V14. Point 14 Volts."""

    v_ar14 = int16(41, scale_register=10, writable=True)
    """VAr14. Point 14 VARs."""

    v15 = uint16(42, scale_register=9, writable=True, unit='% VRef')
    """V15. Point 15 Volts."""

    v_ar15 = int16(43, scale_register=10, writable=True)
    """VAr15. Point 15 VARs."""

    v16 = uint16(44, scale_register=9, writable=True, unit='% VRef')
    """V16. Point 16 Volts."""

    v_ar16 = int16(45, scale_register=10, writable=True)
    """VAr16. Point 16 VARs."""

    v17 = uint16(46, scale_register=9, writable=True, unit='% VRef')
    """V17. Point 17 Volts."""

    v_ar17 = int16(47, scale_register=10, writable=True)
    """VAr17. Point 17 VARs."""

    v18 = uint16(48, scale_register=9, writable=True, unit='% VRef')
    """V18. Point 18 Volts."""

    v_ar18 = int16(49, scale_register=10, writable=True)
    """VAr18. Point 18 VARs."""

    v19 = uint16(50, scale_register=9, writable=True, unit='% VRef')
    """V19. Point 19 Volts."""

    v_ar19 = int16(51, scale_register=10, writable=True)
    """VAr19. Point 19 VARs."""

    v20 = uint16(52, scale_register=9, writable=True, unit='% VRef')
    """V20. Point 20 Volts."""

    v_ar20 = int16(53, scale_register=10, writable=True)
    """VAr20. Point 20 VARs."""

    crv_nam = string(54, 8, writable=True)
    """CrvNam. Optional description for curve. (Max 16 chars)."""

    rmp_tms = uint16(62, writable=True, unit='Secs')
    """RmpTms. The time of the PT1 in seconds (time to accomplish a change of 95%)."""

    rmp_dec_tmm = uint16(63, scale_register=11, writable=True, unit='% ref_value/min')
    """RmpDecTmm. The maximum rate at which the VAR value may be reduced in response
    to changes in the voltage value. %refVal is %WMax %VArMax or %VArAval
    depending on value of DeptRef."""

    rmp_inc_tmm = uint16(64, scale_register=11, writable=True, unit='% ref_value/min')
    """RmpIncTmm. The maximum rate at which the VAR value may be increased in
    response to changes in the voltage value. %refVal is %WMax %VArMax or %VArAval
    depending on value of DeptRef."""

    read_only = enum16(65, ReadOnly)
    """ReadOnly. Boolean flag indicates if curve is read-only or can be modified."""


class VoltVar(SunSpecComponent):
    """SunSpec model 126: Static Volt-VAR."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is Volt-VAR control active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for volt-VAR change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for volt-VAR curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. The time of the PT1 in seconds (time to accomplish a change of 95%)."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    curve = model_length_group(VoltVarCurve, start=12, stride=54)
