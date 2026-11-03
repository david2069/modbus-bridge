"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64415.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    string,
)


class LogEventModeEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class HTTPMessageModeEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class COMM004Certificate(IntEnum):
    Default_Certificate = 0
    COMM_004A = 1
    COMM_004B = 2
    COMM_004C = 3
    COMM_004D = 4
    COMM_004E = 5
    COMM_004F = 6
    COMM_004G = 7


class SubscribtionEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class CSIPControl(SunSpecComponent):
    """SunSpec model 64415: CSIP Client Control."""

    log_event_ena = enum16(2, LogEventModeEnable, writable=True)
    """LogEvent Mode Enable. Enable or disable the LogEvent mode."""

    http_msg = enum16(3, HTTPMessageModeEnable, writable=True)
    """HTTP Message Mode Enable. Enable or disable the HTTP Message mode."""

    comm004_cert = enum16(4, COMM004Certificate, writable=True)
    """COMM-004 Certificate. Select COMM-004 certificate type."""

    subscribed_resource = string(5, 64, writable=True)
    """Subscribed Resource URL. The URL of the resource to subscribe to."""

    subscription_ena = enum16(69, SubscribtionEnable, writable=True)
    """Subscribtion Enable. Enable or disable the Subscription mode."""
