"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_130.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    model_length_group,
    string,
    uint16,
)


class ReadOnly(IntEnum):
    READWRITE = 0
    READONLY = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class HvrtCurve(Component):
    """One 'curve' block of SunSpec model 130."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 must disconnect duration."""

    v1 = uint16(14, scale_register=10, writable=True, unit='% VRef')
    """V1. Point 1 must disconnect voltage."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 must disconnect duration."""

    v2 = uint16(16, scale_register=10, writable=True, unit='% VRef')
    """V2. Point 2 must disconnect voltage."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 must disconnect duration."""

    v3 = uint16(18, scale_register=10, writable=True, unit='% VRef')
    """V3. Point 3 must disconnect voltage."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 must disconnect duration."""

    v4 = uint16(20, scale_register=10, writable=True, unit='% VRef')
    """V4. Point 4 must disconnect voltage."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 must disconnect duration."""

    v5 = uint16(22, scale_register=10, writable=True, unit='% VRef')
    """V5. Point 5 must disconnect voltage."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 must disconnect duration."""

    v6 = uint16(24, scale_register=10, writable=True, unit='% VRef')
    """V6. Point 6 must disconnect voltage."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 must disconnect duration."""

    v7 = uint16(26, scale_register=10, writable=True, unit='% VRef')
    """V7. Point 7 must disconnect voltage."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 must disconnect duration."""

    v8 = uint16(28, scale_register=10, writable=True, unit='% VRef')
    """V8. Point 8 must disconnect voltage."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 must disconnect duration."""

    v9 = uint16(30, scale_register=10, writable=True, unit='% VRef')
    """V9. Point 9 must disconnect voltage."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 must disconnect duration."""

    v10 = uint16(32, scale_register=10, writable=True, unit='% VRef')
    """V10. Point 10 must disconnect voltage."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 must disconnect duration."""

    v11 = uint16(34, scale_register=10, writable=True, unit='% VRef')
    """V11. Point 11 must disconnect voltage."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 must disconnect duration."""

    v12 = uint16(36, scale_register=10, writable=True, unit='% VRef')
    """V12. Point 12 must disconnect voltage."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 must disconnect duration."""

    v13 = uint16(38, scale_register=10, writable=True, unit='% VRef')
    """V13. Point 13 must disconnect voltage."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 must disconnect duration."""

    v14 = uint16(40, scale_register=10, writable=True, unit='% VRef')
    """V14. Point 14 must disconnect voltage."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 must disconnect duration."""

    v15 = uint16(42, scale_register=10, writable=True, unit='% VRef')
    """V15. Point 15 must disconnect voltage."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 must disconnect duration."""

    v16 = uint16(44, scale_register=10, writable=True, unit='% VRef')
    """V16. Point 16 must disconnect voltage."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 must disconnect duration."""

    v17 = uint16(46, scale_register=10, writable=True, unit='% VRef')
    """V17. Point 17 must disconnect voltage."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 must disconnect duration."""

    v18 = uint16(48, scale_register=10, writable=True, unit='% VRef')
    """V18. Point 18 must disconnect voltage."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 must disconnect duration."""

    v19 = uint16(50, scale_register=10, writable=True, unit='% VRef')
    """V19. Point 19 must disconnect voltage."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 must disconnect duration."""

    v20 = uint16(52, scale_register=10, writable=True, unit='% VRef')
    """V20. Point 20 must disconnect voltage."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Hvrt(SunSpecComponent):
    """SunSpec model 130: HVRTD."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. HVRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for HVRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for HVRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    curve = model_length_group(HvrtCurve, start=12, stride=50)
