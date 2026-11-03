"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_131.json)

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


class ReadOnly(IntEnum):
    READWRITE = 0
    READONLY = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class WattPfCurve(Component):
    """One 'curve' block of SunSpec model 131."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    w1 = int16(13, scale_register=9, writable=True, unit='% WMax')
    """W1. Point 1 Watts."""

    pf1 = int16(14, scale_register=10, writable=True, unit='cos()')
    """PF1. Point 1 PF in EEI notation."""

    w2 = int16(15, scale_register=9, writable=True, unit='% WMax')
    """W2. Point 2 Watts."""

    pf2 = int16(16, scale_register=10, writable=True, unit='cos()')
    """PF2. Point 2 PF in EEI notation."""

    w3 = int16(17, scale_register=9, writable=True, unit='% WMax')
    """W3. Point 3 Watts."""

    pf3 = int16(18, scale_register=10, writable=True, unit='cos()')
    """PF3. Point 3 PF in EEI notation."""

    w4 = int16(19, scale_register=9, writable=True, unit='% WMax')
    """W4. Point 4 Watts."""

    pf4 = int16(20, scale_register=10, writable=True, unit='cos()')
    """PF4. Point 4 PF in EEI notation."""

    w5 = int16(21, scale_register=9, writable=True, unit='% WMax')
    """W5. Point 5 Watts."""

    pf5 = int16(22, scale_register=10, writable=True, unit='cos()')
    """PF5. Point 5 PF in EEI notation."""

    w6 = int16(23, scale_register=9, writable=True, unit='% WMax')
    """W6. Point 6 Watts."""

    pf6 = int16(24, scale_register=10, writable=True, unit='cos()')
    """PF6. Point 6 PF in EEI notation."""

    w7 = int16(25, scale_register=9, writable=True, unit='% WMax')
    """W7. Point 7 Watts."""

    pf7 = int16(26, scale_register=10, writable=True, unit='cos()')
    """PF7. Point 7 PF in EEI notation."""

    w8 = int16(27, scale_register=9, writable=True, unit='% WMax')
    """W8. Point 8 Watts."""

    pf8 = int16(28, scale_register=10, writable=True, unit='cos()')
    """PF8. Point 8 PF in EEI notation."""

    w9 = int16(29, scale_register=9, writable=True, unit='% WMax')
    """W9. Point 9 Watts."""

    pf9 = int16(30, scale_register=10, writable=True, unit='cos()')
    """PF9. Point 9 PF in EEI notation."""

    w10 = int16(31, scale_register=9, writable=True, unit='% WMax')
    """W10. Point 10 Watts."""

    pf10 = int16(32, scale_register=10, writable=True, unit='cos()')
    """PF10. Point 10 PF in EEI notation."""

    w11 = int16(33, scale_register=9, writable=True, unit='% WMax')
    """W11. Point 11 Watts."""

    pf11 = int16(34, scale_register=10, writable=True, unit='cos()')
    """PF11. Point 11 PF in EEI notation."""

    w12 = int16(35, scale_register=9, writable=True, unit='% WMax')
    """W12. Point 12 Watts."""

    pf12 = int16(36, scale_register=10, writable=True, unit='cos()')
    """PF12. Point 12 PF in EEI notation."""

    w13 = int16(37, scale_register=9, writable=True, unit='% WMax')
    """W13. Point 13 Watts."""

    pf13 = int16(38, scale_register=10, writable=True, unit='cos()')
    """PF13. Point 13 PF in EEI notation."""

    w14 = int16(39, scale_register=9, writable=True, unit='% WMax')
    """W14. Point 14 Watts."""

    pf14 = int16(40, scale_register=10, writable=True, unit='cos()')
    """PF14. Point 14 PF in EEI notation."""

    w15 = int16(41, scale_register=9, writable=True, unit='% WMax')
    """W15. Point 15 Watts."""

    pf15 = int16(42, scale_register=10, writable=True, unit='cos()')
    """PF15. Point 15 PF in EEI notation."""

    w16 = int16(43, scale_register=9, writable=True, unit='% WMax')
    """W16. Point 16 Watts."""

    pf16 = int16(44, scale_register=10, writable=True, unit='cos()')
    """PF16. Point 16 PF in EEI notation."""

    w17 = int16(45, scale_register=9, writable=True, unit='% WMax')
    """W17. Point 17 Watts."""

    pf17 = int16(46, scale_register=10, writable=True, unit='cos()')
    """PF17. Point 17 PF in EEI notation."""

    w18 = int16(47, scale_register=9, writable=True, unit='% WMax')
    """W18. Point 18 Watts."""

    pf18 = int16(48, scale_register=10, writable=True, unit='cos()')
    """PF18. Point 18 PF in EEI notation."""

    w19 = int16(49, scale_register=9, writable=True, unit='% WMax')
    """W19. Point 19 Watts."""

    pf19 = int16(50, scale_register=10, writable=True, unit='cos()')
    """PF19. Point 19 PF in EEI notation."""

    w20 = int16(51, scale_register=9, writable=True, unit='% WMax')
    """W20. Point 20 Watts."""

    pf20 = int16(52, scale_register=10, writable=True, unit='cos()')
    """PF20. Point 20 PF in EEI notation."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve."""

    rmp_pt1_tms = uint16(61, writable=True, unit='Secs')
    """RmpPT1Tms. The time of the PT1 in seconds (time to accomplish a change of
    95%)."""

    rmp_dec_tmm = uint16(62, scale_register=11, writable=True, unit='% PF/min')
    """RmpDecTmm. The maximum rate at which the power factor may be reduced in
    response to changes in the power value."""

    rmp_inc_tmm = uint16(63, scale_register=11, writable=True, unit='% PF/min')
    """RmpIncTmm. The maximum rate at which the power factor may be increased in
    response to changes in the power value."""

    read_only = enum16(64, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class WattPf(SunSpecComponent):
    """SunSpec model 131: Watt-PF."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is watt-PF mode active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for watt-PF change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for watt-PF curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend 4)."""

    n_pt = uint16(8)
    """NPt. Max number of points in array."""

    curve = model_length_group(WattPfCurve, start=12, stride=54)
