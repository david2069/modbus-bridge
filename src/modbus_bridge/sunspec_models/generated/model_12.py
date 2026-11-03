"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_12.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    string,
)


class ConfigStatus(IntEnum):
    NOT_CONFIGURED = 0
    VALID_SETTING = 1
    VALID_HW = 2


class ChangeStatus(IntFlag):
    PENDING = 1 << 0


class ConfigCapability(IntFlag):
    DHCP = 1 << 0
    BOOTP = 1 << 1
    ZEROCONF = 1 << 2
    DNS = 1 << 3
    CFG_SETTABLE = 1 << 4
    HW_CONFIG = 1 << 5
    NTP_CLIENT = 1 << 6
    RESET_REQUIRED = 1 << 7


class IPv4Config(IntEnum):
    STATIC = 0
    DHCP = 1
    BOOTP = 2
    ZEROCONF = 3


class Control(IntEnum):
    ENABLE_DNS = 0
    ENABLE_NTP = 1


class Model12(SunSpecComponent):
    """SunSpec model 12: IPv4."""

    nam = string(2, 4, writable=True)
    """Name. Interface name."""

    cfg_st = enum16(6, ConfigStatus)
    """Config Status. Configuration status."""

    chg_st = bitfield16(7, ChangeStatus)
    """Change Status. A configuration change is pending."""

    cap = bitfield16(8, ConfigCapability)
    """Config Capability. Identify capable sources of configuration."""

    cfg = enum16(9, IPv4Config, writable=True)
    """IPv4 Config. Configuration method used."""

    ctl = enum16(10, Control, writable=True)
    """Control. Configure use of services."""

    addr = string(11, 8, writable=True)
    """IP. IPv4 numeric address as a dotted string xxx.xxx.xxx.xxx."""

    msk = string(19, 8, writable=True)
    """Netmask. IPv4 numeric netmask as a dotted string xxx.xxx.xxx.xxx."""

    gw = string(27, 8, writable=True)
    """Gateway. IPv4 numeric gateway address as a dotted string xxx.xxx.xxx.xxx."""

    dns1 = string(35, 8, writable=True)
    """DNS1. IPv4 numeric DNS address as a dotted string xxx.xxx.xxx.xxx."""

    dns2 = string(43, 8, writable=True)
    """DNS2. IPv4 numeric DNS address as a dotted string xxx.xxx.xxx.xxx."""

    ntp1 = string(51, 12, writable=True)
    """NTP1. IPv4 numeric NTP address as a dotted string xxx.xxx.xxx.xxx."""

    ntp2 = string(63, 12, writable=True)
    """NTP2. IPv4 numeric NTP address as a dotted string xxx.xxx.xxx.xxx."""

    dom_nam = string(75, 12, writable=True)
    """Domain. Domain name (24 chars max)."""

    host_nam = string(87, 12, writable=True)
    """Host Name. Host name (24 chars max)."""
