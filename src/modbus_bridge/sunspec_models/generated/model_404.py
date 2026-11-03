"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_404.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    int16,
    uint16,
)


class InputEvent(IntFlag):
    LOW_VOLTAGE = 1 << 0
    LOW_POWER = 1 << 1
    LOW_EFFICIENCY = 1 << 2
    CURRENT = 1 << 3
    VOLTAGE = 1 << 4
    POWER = 1 << 5
    PR = 1 << 6
    DISCONNECTED = 1 << 7
    FUSE_FAULT = 1 << 8
    COMBINER_FUSE_FAULT = 1 << 9
    COMBINER_CABINET_OPEN = 1 << 10
    TEMP = 1 << 11
    GROUNDFAULT = 1 << 12
    REVERSED_POLARITY = 1 << 13
    INCOMPATIBLE = 1 << 14
    COMM_ERROR = 1 << 15
    INTERNAL_ERROR = 1 << 16
    THEFT = 1 << 17
    ARC_DETECTED = 1 << 18


class Event(IntFlag):
    LOW_VOLTAGE = 1 << 0
    LOW_POWER = 1 << 1
    LOW_EFFICIENCY = 1 << 2
    CURRENT = 1 << 3
    VOLTAGE = 1 << 4
    POWER = 1 << 5
    PR = 1 << 6
    DISCONNECTED = 1 << 7
    FUSE_FAULT = 1 << 8
    COMBINER_FUSE_FAULT = 1 << 9
    COMBINER_CABINET_OPEN = 1 << 10
    TEMP = 1 << 11
    GROUNDFAULT = 1 << 12
    REVERSED_POLARITY = 1 << 13
    INCOMPATIBLE = 1 << 14
    COMM_ERROR = 1 << 15
    INTERNAL_ERROR = 1 << 16
    THEFT = 1 << 17
    ARC_DETECTED = 1 << 18


class StringCombinerAdvancedInputsString(Component):
    """One 'string' block of SunSpec model 404."""

    in_id = uint16(27)
    """ID. Uniquely identifies this input set."""

    in_evt = bitfield32(28, InputEvent)
    """Input Event. String Input Event Flags."""

    in_evt_vnd = bitfield32(30)
    """Input Event Vendor. String Input Vendor Event Flags."""

    in_dca = int16(32, scale_register=22, unit='A')
    """Amps. String Input Current."""

    in_dc_ahr = acc32(33, scale_register=23, unit='Ah')
    """Amp-hours. String Input Amp-Hours."""

    in_dcv = int16(35, scale_register=24, unit='V')
    """Voltage. String Input Voltage."""

    in_dcw = int16(36, scale_register=25, unit='W')
    """Watts. String Input Power."""

    in_dc_wh = acc32(37, scale_register=26, unit='Wh')
    """Watt-hours. String Input Energy."""

    in_dcpr = uint16(39, unit='Pct')
    """PR. String Performance Ratio."""

    in_n = uint16(40)
    """N. Number of modules in this input string."""


class StringCombinerAdvancedInputs(SunSpecComponent):
    """SunSpec model 404: String Combiner (Advanced)."""

    dca_max = uint16(7, scale_register=2, unit='A')
    """Rating. Maximum DC Current Rating."""

    n = uint16(8)
    """N. Number of Inputs."""

    evt = bitfield32(9, Event)
    """Event. Events."""

    evt_vnd = bitfield32(11)
    """Vendor Event. Vendor defined events."""

    dca = int16(13, scale_register=2, unit='A')
    """Amps. Total measured current."""

    dc_ahr = acc32(14, scale_register=3, unit='Ah')
    """Amp-hours. Total metered Amp-hours."""

    dcv = int16(16, scale_register=4, unit='V')
    """Voltage. Output Voltage."""

    tmp = int16(17, unit='C')
    """Temp. Internal operating temperature."""

    dcw = int16(18, scale_register=5, unit='W')
    """Watts. Output power."""

    dcpr = int16(19, unit='Pct')
    """PR. DC Performance ratio value."""

    dc_wh = acc32(20, scale_register=6, unit='Wh')
    """Watt-hours. Output energy."""

    string = repeating_group(uint16(8), StringCombinerAdvancedInputsString, stride=14)
