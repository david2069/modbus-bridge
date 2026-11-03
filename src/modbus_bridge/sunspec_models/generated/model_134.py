"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_134.json)

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


class FreqWattCurve(Component):
    """One 'curve' block of SunSpec model 134."""

    act_pt = uint16(12, writable=True)
    """ActPt. Number of active points in array."""

    hz1 = uint16(13, scale_register=9, writable=True, unit='Hz')
    """Hz1. Point 1 Hertz."""

    w1 = int16(14, scale_register=10, writable=True, unit='% WRef')
    """W1. Point 1 Watts."""

    hz2 = uint16(15, scale_register=9, writable=True, unit='Hz')
    """Hz2. Point 2 Hertz."""

    w2 = int16(16, scale_register=10, writable=True, unit='% WRef')
    """W2. Point 2 Watts."""

    hz3 = uint16(17, scale_register=9, writable=True, unit='Hz')
    """Hz3. Point 3 Hertz."""

    w3 = int16(18, scale_register=10, writable=True, unit='% WRef')
    """W3. Point 3 Watts."""

    hz4 = uint16(19, scale_register=9, writable=True, unit='Hz')
    """Hz4. Point 4 Hertz."""

    w4 = int16(20, scale_register=10, writable=True, unit='% WRef')
    """W4. Point 4 Watts."""

    hz5 = uint16(21, scale_register=9, writable=True, unit='Hz')
    """Hz5. Point 5 Hertz."""

    w5 = int16(22, scale_register=10, writable=True, unit='% WRef')
    """W5. Point 5 Watts."""

    hz6 = uint16(23, scale_register=9, writable=True, unit='Hz')
    """Hz6. Point 6 Hertz."""

    w6 = int16(24, scale_register=10, writable=True, unit='% WRef')
    """W6. Point 6 Watts."""

    hz7 = uint16(25, scale_register=9, writable=True, unit='Hz')
    """Hz7. Point 7 Hertz."""

    w7 = int16(26, scale_register=10, writable=True, unit='% WRef')
    """W7. Point 7 Watts."""

    hz8 = uint16(27, scale_register=9, writable=True, unit='Hz')
    """Hz8. Point 8 Hertz."""

    w8 = int16(28, scale_register=10, writable=True, unit='% WRef')
    """W8. Point 8 Watts."""

    hz9 = uint16(29, scale_register=9, writable=True, unit='Hz')
    """Hz9. Point 9 Hertz."""

    w9 = int16(30, scale_register=10, writable=True, unit='% WRef')
    """W9. Point 9 Watts."""

    hz10 = uint16(31, scale_register=9, writable=True, unit='Hz')
    """Hz10. Point 10 Hertz."""

    w10 = int16(32, scale_register=10, writable=True, unit='% WRef')
    """W10. Point 10 Watts."""

    hz11 = uint16(33, scale_register=9, writable=True, unit='Hz')
    """Hz11. Point 11 Hertz."""

    w11 = int16(34, scale_register=10, writable=True, unit='% WRef')
    """W11. Point 11 Watts."""

    hz12 = uint16(35, scale_register=9, writable=True, unit='Hz')
    """Hz12. Point 12 Hertz."""

    w12 = int16(36, scale_register=10, writable=True, unit='% WRef')
    """W12. Point 12 Watts."""

    hz13 = uint16(37, scale_register=9, writable=True, unit='Hz')
    """Hz13. Point 13 Hertz."""

    w13 = int16(38, scale_register=10, writable=True, unit='% WRef')
    """W13. Point 13 Watts."""

    hz14 = uint16(39, scale_register=9, writable=True, unit='Hz')
    """Hz14. Point 14 Hertz."""

    w14 = int16(40, scale_register=10, writable=True, unit='% WRef')
    """W14. Point 14 Watts."""

    hz15 = uint16(41, scale_register=9, writable=True, unit='Hz')
    """Hz15. Point 15 Hertz."""

    w15 = int16(42, scale_register=10, writable=True, unit='% WRef')
    """W15. Point 15 Watts."""

    hz16 = uint16(43, scale_register=9, writable=True, unit='Hz')
    """Hz16. Point 16 Hertz."""

    w16 = int16(44, scale_register=10, writable=True, unit='% WRef')
    """W16. Point 16 Watts."""

    hz17 = uint16(45, scale_register=9, writable=True, unit='Hz')
    """Hz17. Point 17 Hertz."""

    w17 = int16(46, scale_register=10, writable=True, unit='% WRef')
    """W17. Point 17 Watts."""

    hz18 = uint16(47, scale_register=9, writable=True, unit='Hz')
    """Hz18. Point 18 Hertz."""

    w18 = int16(48, scale_register=10, writable=True, unit='% WRef')
    """W18. Point 18 Watts."""

    hz19 = uint16(49, scale_register=9, writable=True, unit='Hz')
    """Hz19. Point 19 Hertz."""

    w19 = int16(50, scale_register=10, writable=True, unit='% WRef')
    """W19. Point 19 Watts."""

    hz20 = uint16(51, scale_register=9, writable=True, unit='Hz')
    """Hz20. Point 20 Hertz."""

    w20 = int16(52, scale_register=10, writable=True, unit='% WRef')
    """W20. Point 20 Watts."""

    crv_nam = string(53, 8, writable=True)
    """CrvNam. Optional description for curve. (Max 16 chars)."""

    rmp_pt1_tms = uint16(61, writable=True, unit='Secs')
    """RmpPT1Tms. The time of the PT1 in seconds (time to accomplish a change of
    95%)."""

    rmp_dec_tmm = uint16(62, scale_register=11, writable=True, unit='% WMax/min')
    """RmpDecTmm. The maximum rate at which the power value may be reduced in
    response to changes in the frequency value."""

    rmp_inc_tmm = uint16(63, scale_register=11, writable=True, unit='% WMax/min')
    """RmpIncTmm. The maximum rate at which the power value may be increased in
    response to changes in the frequency value."""

    rmp_rs_up = uint16(64, scale_register=11, writable=True, unit='% WMax/min')
    """RmpRsUp. The maximum rate at which the power may be increased after releasing
    the frozen value of snap shot function."""

    snpt_w = bitfield16(65, writable=True)
    """SnptW. 1=enable snapshot/capture mode."""

    w_ref = uint16(66, scale_register=10, writable=True, unit='W')
    """WRef. Reference active power (default = WMax)."""

    w_ref_str_hz = uint16(67, scale_register=9, writable=True, unit='Hz')
    """WRefStrHz. Frequency deviation from nominal frequency at the time of the
    snapshot to start constraining power output."""

    w_ref_stop_hz = uint16(68, scale_register=9, writable=True, unit='Hz')
    """WRefStopHz. Frequency deviation from nominal frequency at which to release the
    power output."""

    read_only = enum16(69, ReadOnly)
    """ReadOnly. Curve is read-only or can be modified."""


class FreqWatt(SunSpecComponent):
    """SunSpec model 134: Freq-Watt Crv."""

    act_crv = uint16(2, writable=True)
    """ActCrv. Index of active curve. 0=no active curve."""

    mod_ena = bitfield16(3, ModEna, writable=True)
    """ModEna. Is curve-based Frequency-Watt control active."""

    win_tms = uint16(4, writable=True, unit='Secs')
    """WinTms. Time window for freq-watt change."""

    rvrt_tms = uint16(5, writable=True, unit='Secs')
    """RvrtTms. Timeout period for freq-watt curve selection."""

    rmp_tms = uint16(6, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current mode to new mode."""

    n_crv = uint16(7)
    """NCrv. Number of curves supported (recommend min. 4)."""

    n_pt = uint16(8)
    """NPt. Number of curve points supported (maximum of 20)."""

    curve = model_length_group(FreqWattCurve, start=12, stride=58)
