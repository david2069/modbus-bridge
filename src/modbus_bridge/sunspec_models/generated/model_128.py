"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_128.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    uint16,
)


class ArGraMod(IntEnum):
    EDGE = 0
    CENTER = 1


class ModEna(IntFlag):
    ENABLED = 1 << 0


class ReactiveCurrent(SunSpecComponent):
    """SunSpec model 128: Dynamic Reactive Current."""

    ar_gra_mod = enum16(2, ArGraMod, writable=True)
    """ArGraMod. Indicates if gradients trend toward zero at the edges of the
    deadband or trend toward zero at the center of the deadband."""

    ar_gra_sag = uint16(3, scale_register=13, writable=True, unit='%ARtg/%dV')
    """ArGraSag. The gradient used to increase capacitive dynamic current. A value of
    0 indicates no additional reactive current support."""

    ar_gra_swell = uint16(4, scale_register=13, writable=True, unit='%ARtg/%dV')
    """ArGraSwell. The gradient used to increase inductive dynamic current. A value
    of 0 indicates no additional reactive current support."""

    mod_ena = bitfield16(5, ModEna, writable=True)
    """ModEna. Activate dynamic reactive current model."""

    fil_tms = uint16(6, writable=True, unit='Secs')
    """FilTms. The time window used to calculate the moving average voltage."""

    db_v_min = uint16(7, scale_register=14, writable=True, unit='% VRef')
    """DbVMin. The lower delta voltage limit for which negative voltage deviations
    less than this value no dynamic vars are produced."""

    db_v_max = uint16(8, scale_register=14, writable=True, unit='% VRef')
    """DbVMax. The upper delta voltage limit for which positive voltage deviations
    less than this value no dynamic current produced."""

    blk_zn_v = uint16(9, scale_register=14, writable=True, unit='% VRef')
    """BlkZnV. Block zone voltage which defines a lower voltage boundary below which
    no dynamic current is produced."""

    hys_blk_zn_v = uint16(10, scale_register=14, writable=True, unit='% VRef')
    """HysBlkZnV. Hysteresis voltage used with BlkZnV."""

    blk_zn_tmms = uint16(11, writable=True, unit='mSecs')
    """BlkZnTmms. Block zone time the time before which reactive current support
    remains active regardless of how low the voltage drops."""

    hold_tmms = uint16(12, writable=True, unit='mSecs')
    """HoldTmms. Hold time during which reactive current support continues after the
    average voltage has entered the dead zone."""
