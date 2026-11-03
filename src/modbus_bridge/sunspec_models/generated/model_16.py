"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_16.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    eui48,
    string,
)


class Config(IntEnum):
    STATIC = 0
    DHCP = 1


class Control(IntFlag):
    ENABLE_DNS = 1 << 0
    ENABLE_NTP = 1 << 1


class LinkControl(IntFlag):
    AUTONEGOTIATE = 1 << 0
    FULL_DUPLEX = 1 << 1
    FORCE_10MB = 1 << 2
    FORCE_100MB = 1 << 3
    FORCE_1GB = 1 << 4


class Model16(SunSpecComponent):
    """SunSpec model 16: Simple IP Network."""

    nam = string(2, 4, writable=True)
    """Name. Interface name. (8 chars)."""

    cfg = enum16(6, Config)
    """Config. Force IPv4 configuration method."""

    ctl = bitfield16(7, Control, writable=True)
    """Control. Configure use of services."""

    addr = string(8, 8, writable=True)
    """Address. IP address."""

    msk = string(16, 8, writable=True)
    """Netmask."""

    gw = string(24, 8, writable=True)
    """Gateway. Gateway IP address."""

    dns1 = string(32, 8, writable=True)
    """DNS1. 32 bit IP address of DNS server."""

    dns2 = string(40, 8, writable=True)
    """DNS2. 32 bit IP address of DNS server."""

    mac = eui48(48)
    """MAC. IEEE MAC address of this interface."""

    lnk_ctl = bitfield16(52, LinkControl, writable=True)
    """Link Control. Link control flags."""
