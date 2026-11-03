"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64001.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    string,
    uint16,
)


class Model64001(SunSpecComponent):
    """SunSpec model 64001: Veris Status and Configuration."""

    cmd = enum16(2, writable=True)
    """Command Code."""

    hw_rev = uint16(3)
    """Hardware Revision."""

    rsfw_rev = uint16(4)
    """RS FW Revision."""

    osfw_rev = uint16(5)
    """OS FW Revision."""

    prod_rev = string(6, 2)
    """Product Revision."""

    boots = uint16(8)
    """Boot Count."""

    switch = bitfield16(9)
    """DIP Switches."""

    sensors = uint16(10)
    """Num Detected Sensors."""

    talking = uint16(11)
    """Num Communicating Sensors."""

    status = bitfield16(12)
    """System Status."""

    config = bitfield16(13)
    """System Configuration."""

    le_dblink = uint16(14, unit='Pct')
    """LED Blink Threshold."""

    le_don = uint16(15, unit='Pct')
    """LED On Threshold."""

    reserved = uint16(16)

    loc = string(17, 16)
    """Location String."""

    s1_id = enum16(33)
    """Sensor 1 Unit ID."""

    s1_addr = uint16(34)
    """Sensor 1 Address."""

    s1_os_ver = uint16(35)
    """Sensor 1 OS Version."""

    s1_ver = string(36, 2)
    """Sensor 1 Product Version."""

    s1_serial = string(38, 5)
    """Sensor 1 Serial Num."""

    s2_id = enum16(43)
    """Sensor 2 Unit ID."""

    s2_addr = uint16(44)
    """Sensor 2 Address."""

    s2_os_ver = uint16(45)
    """Sensor 2 OS Version."""

    s2_ver = string(46, 2)
    """Sensor 2 Product Version."""

    s2_serial = string(48, 5)
    """Sensor 2 Serial Num."""

    s3_id = enum16(53)
    """Sensor 3 Unit ID."""

    s3_addr = uint16(54)
    """Sensor 3 Address."""

    s3_os_ver = uint16(55)
    """Sensor 3 OS Version."""

    s3_ver = string(56, 2)
    """Sensor 3 Product Version."""

    s3_serial = string(58, 5)
    """Sensor 3 Serial Num."""

    s4_id = enum16(63)
    """Sensor 4 Unit ID."""

    s4_addr = uint16(64)
    """Sensor 4 Address."""

    s4_os_ver = uint16(65)
    """Sensor 4 OS Version."""

    s4_ver = string(66, 2)
    """Sensor 4 Product Version."""

    s4_serial = string(68, 5)
    """Sensor 4 Serial Num."""
