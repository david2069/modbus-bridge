"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_11.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    eui48,
    string,
    uint16,
)


class InterfaceStatusFlags(IntFlag):
    LINK = 1 << 0
    FULL_DUPLEX = 1 << 1
    AUTO_NEG1 = 1 << 2
    AUTO_NEG2 = 1 << 3
    AUTO_NEG3 = 1 << 4
    RESET_REQUIRED = 1 << 5
    HW_FAULT = 1 << 6


class LinkState(IntEnum):
    UNKNOWN = 0
    ENABLED = 1
    DISABLED = 2
    TESTING = 3


class Control(IntFlag):
    AUTO = 1 << 0
    FULL_DUPLEX = 1 << 1


class Model11(SunSpecComponent):
    """SunSpec model 11: Ethernet Link Layer."""

    spd = uint16(2, unit='Mbps')
    """Ethernet Link Speed. Interface speed in Mb/s."""

    cfg_st = bitfield16(3, InterfaceStatusFlags)
    """Interface Status Flags. Interface flags."""

    st = enum16(4, LinkState)
    """Link State. State information for this interface."""

    mac = eui48(5)
    """MAC. IEEE MAC address of this interface."""

    nam = string(9, 4, writable=True)
    """Name. Interface name (8 chars)."""

    ctl = bitfield16(13, Control, writable=True)
    """Control. Control flags."""

    frc_spd = uint16(14, writable=True, unit='Mbps')
    """Forced Speed. Forced interface speed in Mb/s when AUTO is disabled."""
