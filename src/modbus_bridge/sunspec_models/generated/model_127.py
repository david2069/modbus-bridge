"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_127.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    int16,
    uint16,
)


class HysEna(IntFlag):
    ENABLED = 1 << 0


class ModEna(IntFlag):
    ENABLED = 1 << 0


class FreqWattParam(SunSpecComponent):
    """SunSpec model 127: Freq-Watt Param."""

    w_gra = uint16(2, scale_register=8, writable=True, unit='% PM/Hz')
    """WGra. The slope of the reduction in the maximum allowed watts output as a
    function of frequency."""

    hz_str = int16(3, scale_register=9, writable=True, unit='Hz')
    """HzStr. The frequency deviation from nominal frequency (ECPNomHz) at which a
    snapshot of the instantaneous power output is taken to act as the CAPPED power
    level (PM) and above which reduction in power output occurs."""

    hz_stop = int16(4, scale_register=9, writable=True, unit='Hz')
    """HzStop. The frequency deviation from nominal frequency (ECPNomHz) at which
    curtailed power output may return to normal and the cap on the power level
    value is removed."""

    hys_ena = bitfield16(5, HysEna, writable=True)
    """HysEna. Enable hysteresis."""

    mod_ena = bitfield16(6, ModEna, writable=True)
    """ModEna. Is Parameterized Frequency-Watt control active."""

    hz_stop_w_gra = uint16(7, scale_register=10, writable=True, unit='% WMax/min')
    """HzStopWGra. The maximum time-based rate of change at which power output
    returns to normal after having been capped by an over frequency event."""
