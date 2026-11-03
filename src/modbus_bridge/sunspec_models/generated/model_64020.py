"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64020.json)

from __future__ import annotations

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
    model_length_group,
    string,
    uint16,
)


class Model64020Repeating(Component):
    """One 'repeating' block of SunSpec model 64020."""

    serial_number = string(32, 9)
    """Serial number. strings of 16 characters."""

    firmware = string(41, 6)
    """Firmware version. string of 11 characters."""

    hardware = uint16(47)
    """Hardware version."""


class Model64020(SunSpecComponent):
    """SunSpec model 64020: Mersen GreenString."""

    aux0_tmp = int16(2, unit='C')
    """Aux 0 temperature."""

    aux1_tmp = int16(3, unit='C')
    """Aux 1 temperature."""

    aux2_tmp = int16(4, unit='C')
    """Aux 2 temperature."""

    aux3_tmp = int16(5, unit='C')
    """Aux 3 temperature."""

    aux4_tmp = int16(6, unit='C')
    """Aux 4 temperature."""

    probe_tmp = int16(7, unit='C')
    """Probe Temperature."""

    main_tmp = int16(8, unit='C')
    """Main Temperature."""

    sensor1_voltage = int16(12, scale_register=9, unit='V')
    """Sensor1 Voltage. scale of 0-10V."""

    sensor2_voltage = int16(13, scale_register=9, unit='V')
    """Sensor2 Voltage. scale of 0-10V."""

    sensor3_voltage = int16(14, scale_register=9, unit='V')
    """Sensor3 Voltage. scale of 0-10V."""

    sensor4_voltage = int16(15, scale_register=9, unit='V')
    """Sensor4 Voltage. scale of 0-10V."""

    sensor5_voltage = int16(16, scale_register=9, unit='V')
    """Sensor5 Voltage. scale of 0-10V."""

    sensor6_voltage = int16(17, scale_register=9, unit='V')
    """Sensor6 Voltage. scale of 0-10V."""

    sensor7_voltage = int16(18, scale_register=9, unit='V')
    """Sensor7 Voltage. scale of 0-10V."""

    sensor1_current = int16(19, scale_register=10, unit='A')
    """Sensor1 Current. scale of 4-20mA."""

    sensor2_current = int16(20, scale_register=10, unit='A')
    """Sensor2 Current. in 4-20mA or 4-20mA."""

    sensor3_current = int16(21, scale_register=10, unit='A')
    """Sensor3 Current. in 4-20mA or 4-20mA."""

    sensor4_current = int16(22, scale_register=10, unit='A')
    """Sensor4 Current. in 4-20mA or 4-20mA."""

    sensor5_current = int16(23, scale_register=10, unit='A')
    """Sensor5 Current. in 4-20mA or 4-20mA."""

    sensor6_current = int16(24, scale_register=10, unit='A')
    """Sensor6 Current. in 4-20mA or 4-20mA."""

    sensor7_current = int16(25, scale_register=10, unit='A')
    """Sensor7 Current. in 4-20mA or 4-20mA."""

    sensor8 = uint16(26, scale_register=11, unit='Hz')
    """Sensor8 frequency. frequency in Hz."""

    relay1 = uint16(27)
    """Relay 1 state."""

    relay2 = uint16(28)
    """Relay 2 state."""

    relay3 = uint16(29)
    """Relay 3 state."""

    reset_accumulators = uint16(30)
    """Reset the accumulators. always 0 in reading, used the code 0xC0DA during the
    writing for resetting them."""

    reset = uint16(31)
    """Reset the system. always 0 in reading, used the code 0xC0DA during the writing
    for resetting the system."""

    repeating = model_length_group(Model64020Repeating, start=32, stride=16)
