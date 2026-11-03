"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_14.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    string,
    uint16,
)


class Capabilities(IntFlag):
    NO_PROXY = 1 << 0
    IPV4_PROXY = 1 << 1
    IPV6_PROXY = 1 << 2


class Model14(SunSpecComponent):
    """SunSpec model 14: Proxy Server."""

    nam = string(2, 4, writable=True)
    """name. Interface name (8 chars)."""

    cap = bitfield16(6, Capabilities, writable=True)
    """Capabilities. Proxy configuration capabilities."""

    cfg = enum16(7, writable=True)
    """Config. Set proxy address type."""

    typ = bitfield16(8, writable=True)
    """Type. Enumerate value. Proxy server type."""

    addr = string(9, 20, writable=True)
    """Address. IPv4 or IPv6 proxy hostname or dotted address (40 chars)."""

    port = uint16(29, writable=True)
    """Port. Proxy port number."""

    user = string(30, 12, writable=True)
    """Username. Proxy user name."""

    pw = string(42, 12, writable=True)
    """Password. Proxy password."""
