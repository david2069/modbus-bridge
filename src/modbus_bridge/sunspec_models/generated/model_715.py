"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_715.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    uint16,
    uint32,
)


class ControlMode(IntEnum):
    REMOTE = 0
    LOCAL = 1


class SetOperation(IntEnum):
    STOP = 0
    START = 1
    ENTER_STANDBY = 2
    EXIT_STANDBY = 3


class DERCtl(SunSpecComponent):
    """SunSpec model 715: DERCtl."""

    loc_rem_ctl = enum16(2, ControlMode)
    """Control Mode. DER control mode. Enumeration."""

    der_hb = uint32(3)
    """DER Heartbeat. Value is incremented every second by the DER with periodic
    resets to zero."""

    controller_hb = uint32(5, writable=True)
    """Controller Heartbeat. Value is incremented every second by the controller with
    periodic resets to zero."""

    alarm_reset = uint16(7, writable=True)
    """Alarm Reset. Used to reset any latched alarms. 1 = Reset."""

    op_ctl = enum16(8, SetOperation, writable=True)
    """Set Operation. Commands to PCS."""
