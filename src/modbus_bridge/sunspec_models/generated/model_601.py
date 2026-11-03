"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_601.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    int32,
    model_length_group,
    string,
    uint16,
)


class Mode(IntEnum):
    Automatic = 0
    Manual = 1
    Calibrate = 2


class Alarm(IntFlag):
    SetPoint = 1 << 0
    ObsEl = 1 << 1
    ObsAz = 1 << 2


class Type(IntEnum):
    Unknown = 0
    Fixed = 1
    Horizontal = 2
    Tilted = 3
    Azimuth = 4
    Dual = 5
    Other = 99


class GlobalMode(IntEnum):
    Automatic = 0
    Manual = 1
    Calibrate = 2


class GlobalAlarm(IntFlag):
    SetPoint = 1 << 0
    ObsEl = 1 << 1
    ObsAz = 1 << 2


class TrackerControllerTracker(Component):
    """One 'tracker' block of SunSpec model 601."""

    id = string(28, 8)
    """Tracker. Descriptive name for this tracker unit."""

    el_trgt = int32(36, scale_register=26, unit='Degrees')
    """Target Elevation. Auto target elevation in degrees from horizontal.
    Unimplemented for single axis azimuth tracker type."""

    az_trgt = int32(38, scale_register=26, unit='Degrees')
    """Target Azimuth. Auto target azimuth in degrees from true north towards east.
    Unimplemented for single axis horizontal tracker type."""

    el_pos = int32(40, scale_register=26, unit='Degrees')
    """Elevation. Actual elevation position in degrees from horizontal. Unimplemented
    for single axis azimuth tracker type."""

    az_pos = int32(42, scale_register=26, unit='Degrees')
    """Azimuth. Actual azimuth position in degrees from true north towards east.
    Unimplemented for single axis horizontal tracker type."""

    el_ctl = int32(44, scale_register=26, writable=True, unit='Degrees')
    """Manual Elevation. Manual override target position of elevation in degrees from
    horizontal. Unimplemented for single axis azimuth tracker type."""

    az_ctl = int32(46, scale_register=26, writable=True, unit='Degrees')
    """Manual Azimuth. Manual override target position of azimuth in degrees from
    true north towards east. Unimplemented for single axis azimuth tracker type."""

    ctl = enum16(48, Mode, writable=True)
    """Mode. Control register. Normal operation is automatic. Operator can override
    the position by setting the ElCtl, AzCtl and enabling Manual operation.
    Entering calibration mode will revert to automatic operation after calibration
    is complete."""

    alm = bitfield16(49, Alarm)
    """Alarm. Tracker alarm conditions."""


class TrackerController(SunSpecComponent):
    """SunSpec model 601: Tracker Controller DRAFT 2."""

    nam = string(2, 8)
    """Controller. Descriptive name for this control unit."""

    typ = enum16(10, Type)
    """Type. Type of tracker."""

    dt_loc = string(11, 5)
    """Date. Local date in YYYYMMDD format."""

    tm_loc = string(16, 3)
    """Time. 24 hour local time stamp to second."""

    day = uint16(19)
    """Day. Number of the day in the year (1-366)."""

    glbl_el_ctl = int32(20, scale_register=26, writable=True, unit='Degrees')
    """Manual Elevation. Global manual override target position of elevation in
    degrees from horizontal. Unimplemented for single axis azimuth tracker type."""

    glbl_az_ctl = int32(22, scale_register=26, writable=True, unit='Degrees')
    """Manual Azimuth. Global manual override target position of azimuth in degrees
    from true north towards east. Unimplemented for single axis azimuth tracker
    type."""

    glbl_ctl = enum16(24, GlobalMode, writable=True)
    """Global Mode. Global Control register operates on all trackers. Normal
    operation is automatic. Operator can override the position by setting the
    ElCtl, AzCtl and enabling Manual operation. Entering calibration mode will
    revert to automatic operation after calibration is complete."""

    glbl_alm = bitfield16(25, GlobalAlarm)
    """Global Alarm. Global tracker alarm conditions."""

    n = uint16(27)
    """Trackers. Number of trackers being controlled. Size of repeating block."""

    tracker = model_length_group(TrackerControllerTracker, start=28, stride=22)
