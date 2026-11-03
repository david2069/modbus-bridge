"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_13.json)

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


class IPv6Config(IntEnum):
    STATIC = 0
    DHCP = 1
    BOOTP = 2
    ZEROCONF = 3


class Control(IntEnum):
    ENABLE_DNS = 0
    ENABLE_NTP = 1


class Model13(SunSpecComponent):
    """SunSpec model 13: IPv6."""

    nam = string(2, 4, writable=True)
    """Name. Interface name."""

    cfg_st = enum16(6, ConfigStatus)
    """Config Status. Configuration status."""

    chg_st = bitfield16(7, ChangeStatus)
    """Change Status. A configuration change is pending."""

    cap = bitfield16(8, ConfigCapability)
    """Config Capability. Identify capable sources of configuration."""

    cfg = enum16(9, IPv6Config, writable=True)
    """IPv6 Config. Configuration method used."""

    ctl = enum16(10, Control, writable=True)
    """Control. Configure use of services."""

    addr = string(11, 20, writable=True)
    """IP. IPv6 numeric address as a dotted string xxxx.xxxx.xxxx.xxxx."""

    cidr = string(31, 20, writable=True)
    """CIDR. Classless Inter-Domain Routing Number."""

    gw = string(51, 20, writable=True)
    """Gateway. IPv6 numeric address as a dotted string xxxx.xxxx.xxxx.xxxx."""

    dns1 = string(71, 20, writable=True)
    """DNS1. IPv6 numeric DNS address as a dotted string xxxx.xxxx.xxxx.xxxx."""

    dns2 = string(91, 20, writable=True)
    """DNS2. IPv6 numeric DNS address as a dotted string xxxx.xxxx.xxxx.xxxx."""

    ntp1 = string(111, 20, writable=True)
    """NTP1. IPv6 numeric NTP address as a name or dotted string xxxx.xxxx.xxxx.xxxx."""

    ntp2 = string(131, 20, writable=True)
    """NTP2. IPv6 numeric NTP address as a name or dotted string xxxx.xxxx.xxxx.xxxx."""

    dom_nam = string(151, 12, writable=True)
    """Domain. Domain name (24 chars max)."""

    host_nam = string(163, 12, writable=True)
    """Host Name. Host name (24 chars max)."""
