"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_703.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    uint16,
    uint32,
)


class PermitEnterService(IntEnum):
    DISABLED = 0
    ENABLED = 1


class DEREnterService(SunSpecComponent):
    """SunSpec model 703: Enter Service."""

    es = enum16(2, PermitEnterService, writable=True)
    """Permit Enter Service."""

    esv_hi = uint16(3, scale_register=17, writable=True, unit='Pct')
    """Enter Service Voltage High. Enter service voltage high threshold as percent of
    normal voltage."""

    esv_lo = uint16(4, scale_register=17, writable=True, unit='Pct')
    """Enter Service Voltage Low. Enter service voltage low threshold as percent of
    normal voltage."""

    es_hz_hi = uint32(5, scale_register=18, writable=True, unit='Hz')
    """Enter Service Frequency High. Enter service frequency high threshold."""

    es_hz_lo = uint32(7, scale_register=18, writable=True, unit='Hz')
    """Enter Service Frequency Low. Enter service frequency low threshold."""

    es_dly_tms = uint32(9, writable=True, unit='Secs')
    """Enter Service Delay Time. Enter service delay time in seconds."""

    es_rnd_tms = uint32(11, writable=True, unit='Secs')
    """Enter Service Random Delay. Enter service random delay in seconds."""

    es_rmp_tms = uint32(13, writable=True, unit='Secs')
    """Enter Service Ramp Time. Enter service ramp time in seconds."""

    es_dly_rem_tms = uint32(15, unit='Secs')
    """Enter Service Delay Remaining. Enter service delay time remaining in seconds."""
