"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_133.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    bitfield32,
    enum16,
    int32,
    model_length_group,
    string,
    uint16,
    uint32,
)


class SchdTyp(IntEnum):
    ONETIME = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    WEEKDAY = 4
    HOLIDAY = 5
    WEEKEND = 6
    YEARLY = 7


class XTyp(IntEnum):
    UNSET = 0
    TIME = 1
    TEMP = 2
    PRICE = 3
    OTHER = 99


class YTyp(IntEnum):
    UNSET = 0
    WMax = 1
    RSRVD2 = 2
    PF = 3
    RSRVD4 = 4
    WATT_PRICE = 5
    VAR_PRICE = 6
    RSRVD7 = 7
    VOLT_VAR_ARRAY = 8
    WChaGra = 9
    WDisChaGra = 10
    VArAval = 11
    Schedule = 12
    OTHER = 99


class ActSchd(IntFlag):
    SCHED1 = 1 << 0
    SCHED2 = 1 << 1
    SCHED3 = 1 << 2
    SCHED4 = 1 << 3
    SCHED5 = 1 << 4
    SCHED6 = 1 << 5
    SCHED7 = 1 << 6
    SCHED8 = 1 << 7
    SCHED9 = 1 << 8
    SCHED10 = 1 << 9
    SCHED12 = 1 << 10
    SCHED13 = 1 << 11
    SCHED14 = 1 << 12
    SCHED15 = 1 << 13
    SCHED16 = 1 << 14
    SCHED17 = 1 << 15
    SCHED18 = 1 << 16
    SCHED19 = 1 << 17
    SCHED20 = 1 << 18
    SCHED21 = 1 << 19
    SCHED22 = 1 << 21
    SCHED23 = 1 << 22
    SCHED24 = 1 << 23
    SCHED25 = 1 << 24
    SCHED26 = 1 << 25
    SCHED27 = 1 << 26
    SCHED28 = 1 << 27
    SCHED29 = 1 << 28
    SCHED30 = 1 << 29
    SCHED31 = 1 << 30
    SCHED32 = 1 << 31


class ModEna(IntFlag):
    ENABLED = 1 << 0


class ScheduleRepeating(Component):
    """One 'repeating' block of SunSpec model 133."""

    scale_in_block = True  # each instance carries its own scale factors

    act_pts = uint16(8, writable=True)
    """ActPts. Number of active entries in schedule."""

    str_tms = uint32(9, writable=True, unit='Secs')
    """StrTms. Schedule start in seconds since 2000 JAN 01 00:00:00 UTC."""

    rep_per = uint16(11, writable=True)
    """RepPer. The repetition count for time-based schedules (0=repeat forever)."""

    intv_typ = enum16(12, SchdTyp, writable=True)
    """SchdTyp. The repetition frequency for time-based schedules: no repeat=0."""

    x_typ = enum16(13, XTyp, writable=True)
    """XTyp. The meaning of the X-values in the array."""

    y_typ = enum16(15, YTyp, writable=True)
    """YTyp. The meaning of the Y-values in the array."""

    x1 = int32(17, scale_register=14, writable=True)
    """X1. Entry 1 range."""

    y1 = int32(19, scale_register=16, writable=True)
    """Y1. Entry 1 target."""

    x2 = int32(21, scale_register=14, writable=True)
    """X2. Entry 2 range."""

    y2 = int32(23, scale_register=16, writable=True)
    """Y2. Entry 2 target."""

    x3 = int32(25, scale_register=14, writable=True)
    """X3. Entry 3 range."""

    y3 = int32(27, scale_register=16, writable=True)
    """Y3. Entry 3 target."""

    x4 = int32(29, scale_register=14, writable=True)
    """X4. Entry 4 range."""

    y4 = int32(31, scale_register=16, writable=True)
    """Y4. Entry 4 target."""

    x5 = int32(33, scale_register=14, writable=True)
    """X5. Entry 15range."""

    y5 = int32(35, scale_register=16, writable=True)
    """Y5. Entry 5 target."""

    x6 = int32(37, scale_register=14, writable=True)
    """X6. Entry 6 range."""

    y6 = int32(39, scale_register=16, writable=True)
    """Y6. Entry 6 target."""

    x7 = int32(41, scale_register=14, writable=True)
    """X7. Entry 7 range."""

    y7 = int32(43, scale_register=16, writable=True)
    """Y7. Entry 7 target."""

    x8 = int32(45, scale_register=14, writable=True)
    """X8. Entry 8 range."""

    y8 = int32(47, scale_register=16, writable=True)
    """Y8. Entry 8 target."""

    x9 = int32(49, scale_register=14, writable=True)
    """X9. Entry 9 range."""

    y9 = int32(51, scale_register=16, writable=True)
    """Y9. Entry 9 target."""

    x10 = int32(53, scale_register=14, writable=True)
    """X10. Entry 10 range."""

    y10 = int32(55, scale_register=16, writable=True)
    """Y10. Entry 10 target."""

    nam = string(57, 8, writable=True)
    """Nam. Optional description for schedule."""

    win_tms = uint16(65, writable=True, unit='Secs')
    """WinTms. Time window for schedule entry change."""

    rmp_tms = uint16(66, writable=True, unit='Secs')
    """RmpTms. Ramp time for moving from current target to new target."""

    act_indx = uint16(67)
    """ActIndx. Index of active entry in the active schedule."""


class Schedule(SunSpecComponent):
    """SunSpec model 133: Basic Scheduling."""

    act_schd = bitfield32(2, ActSchd, writable=True)
    """ActSchd. Bitfield of active schedules."""

    mod_ena = bitfield16(4, ModEna, writable=True)
    """ModEna. Is basic scheduling active."""

    n_schd = uint16(5)
    """NSchd. Number of schedules supported (recommend min. 4, max 32)."""

    n_pts = uint16(6)
    """NPts. Number of schedule entries supported (maximum of 10)."""

    repeating = model_length_group(ScheduleRepeating, start=8, stride=60)
