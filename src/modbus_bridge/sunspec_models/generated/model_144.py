"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_144.json)

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


class CrvType(IntEnum):
    CEASE_TO_ENERGIZE = 1


class HfrtxCurve(Component):
    """One 'curve' block of SunSpec model 144."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    tms1 = uint16(13, scale_register=9, writable=True, unit='Secs')
    """Tms1. Point 1 duration."""

    hz1 = uint16(14, scale_register=10, writable=True, unit='Hz')
    """Hz1. Point 1 frequency."""

    tms2 = uint16(15, scale_register=9, writable=True, unit='Secs')
    """Tms2. Point 2 duration."""

    hz2 = uint16(16, scale_register=10, writable=True, unit='Hz')
    """Hz2. Point 2 frequency."""

    tms3 = uint16(17, scale_register=9, writable=True, unit='Secs')
    """Tms3. Point 3 duration."""

    hz3 = uint16(18, scale_register=10, writable=True, unit='Hz')
    """Hz3. Point 3 frequency."""

    tms4 = uint16(19, scale_register=9, writable=True, unit='Secs')
    """Tms4. Point 4 duration."""

    hz4 = uint16(20, scale_register=10, writable=True, unit='Hz')
    """Hz4. Point 4 frequency."""

    tms5 = uint16(21, scale_register=9, writable=True, unit='Secs')
    """Tms5. Point 5 duration."""

    hz5 = uint16(22, scale_register=10, writable=True, unit='Hz')
    """Hz5. Point 5 frequency."""

    tms6 = uint16(23, scale_register=9, writable=True, unit='Secs')
    """Tms6. Point 6 duration."""

    hz6 = uint16(24, scale_register=10, writable=True, unit='Hz')
    """Hz6. Point 6 frequency."""

    tms7 = uint16(25, scale_register=9, writable=True, unit='Secs')
    """Tms7. Point 7 duration."""

    hz7 = uint16(26, scale_register=10, writable=True, unit='Hz')
    """Hz7. Point 7 frequency."""

    tms8 = uint16(27, scale_register=9, writable=True, unit='Secs')
    """Tms8. Point 8 duration."""

    hz8 = uint16(28, scale_register=10, writable=True, unit='Hz')
    """Hz8. Point 8 frequency."""

    tms9 = uint16(29, scale_register=9, writable=True, unit='Secs')
    """Tms9. Point 9 duration."""

    hz9 = uint16(30, scale_register=10, writable=True, unit='Hz')
    """Hz9. Point 9 frequency."""

    tms10 = uint16(31, scale_register=9, writable=True, unit='Secs')
    """Tms10. Point 10 duration."""

    hz10 = uint16(32, scale_register=10, writable=True, unit='Hz')
    """Hz10. Point 10 frequency."""

    tms11 = uint16(33, scale_register=9, writable=True, unit='Secs')
    """Tms11. Point 11 duration."""

    hz11 = uint16(34, scale_register=10, writable=True, unit='Hz')
    """Hz11. Point 11 frequency."""

    tms12 = uint16(35, scale_register=9, writable=True, unit='Secs')
    """Tms12. Point 12 duration."""

    hz12 = uint16(36, scale_register=10, writable=True, unit='Hz')
    """Hz12. Point 12 frequency."""

    tms13 = uint16(37, scale_register=9, writable=True, unit='Secs')
    """Tms13. Point 13 duration."""

    hz13 = uint16(38, scale_register=10, writable=True, unit='Hz')
    """Hz13. Point 13 frequency."""

    tms14 = uint16(39, scale_register=9, writable=True, unit='Secs')
    """Tms14. Point 14 duration."""

    hz14 = uint16(40, scale_register=10, writable=True, unit='Hz')
    """Hz14. Point 14 frequency."""

    tms15 = uint16(41, scale_register=9, writable=True, unit='Secs')
    """Tms15. Point 15 duration."""

    hz15 = uint16(42, scale_register=10, writable=True, unit='Hz')
    """Hz15. Point 15 frequency."""

    tms16 = uint16(43, scale_register=9, writable=True, unit='Secs')
    """Tms16. Point 16 duration."""

    hz16 = uint16(44, scale_register=10, writable=True, unit='Hz')
    """Hz16. Point 16 frequency."""

    tms17 = uint16(45, scale_register=9, writable=True, unit='Secs')
    """Tms17. Point 17 duration."""

    hz17 = uint16(46, scale_register=10, writable=True, unit='Hz')
    """Hz17. Point 17 frequency."""

    tms18 = uint16(47, scale_register=9, writable=True, unit='Secs')
    """Tms18. Point 18 duration."""

    hz18 = uint16(48, scale_register=10, writable=True, unit='Hz')
    """Hz18. Point 18 frequency."""

    tms19 = uint16(49, scale_register=9, writable=True, unit='Secs')
    """Tms19. Point 19 duration."""

    hz19 = uint16(50, scale_register=10, writable=True, unit='Hz')
    """Hz19. Point 19 frequency."""

    tms20 = uint16(51, scale_register=9, writable=True, unit='Secs')
    """Tms20. Point 20 duration."""

    hz20 = uint16(52, scale_register=10, writable=True, unit='Hz')
    """Hz20. Point 20 frequency."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    read_only = enum16(61, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class Hfrtx(SunSpecComponent):
    """SunSpec model 144: HFRTX."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. LHzRT control mode. Enable active curve."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for LFRT change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for LFRT curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    crv_type = enum16(11, CrvType)

    curve = model_length_group(HfrtxCurve, start=12, stride=50)
