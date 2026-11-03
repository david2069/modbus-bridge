"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_125.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    int16,
    uint16,
)


class ModEna(IntFlag):
    ENABLE = 1 << 0


class SigType(IntEnum):
    UNKNOWN = 0
    ABSOLUTE = 1
    RELATIVE = 2
    MULTIPLIER = 3
    LEVEL = 4


class Pricing(SunSpecComponent):
    """SunSpec model 125: Pricing."""

    mod_ena = bitfield16(2, ModEna, writable=True)
    """ModEna. Is price-based charge/discharge mode active?."""

    sig_type = enum16(3, SigType, writable=True)
    """SigType. Meaning of the pricing signal. When a Price schedule is used, type
    must match the schedule range variable description."""

    sig = int16(4, scale_register=8, writable=True)
    """Sig. Utility/ESP specific pricing signal. Content depends on pricing signal
    type. When H/M/L type is specified. Low=0; Med=1; High=2."""

    win_tms = uint16(5, writable=True, unit='Secs')
    """WinTms. Time window for charge/discharge pricing change."""

    rvt_tms = uint16(6, writable=True, unit='Secs')
    """RvtTms. Timeout period for charge/discharge pricing change."""

    rmp_tms = uint16(7, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current charge or discharge level to new
    level."""
