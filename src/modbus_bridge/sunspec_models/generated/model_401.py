"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_401.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    int16,
    uint16,
    uint32,
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


class StringCombinerCurrentString(Component):
    """One 'string' block of SunSpec model 401."""

    in_id = uint16(16)
    """ID. Uniquely identifies this input set."""

    in_evt = bitfield32(17, InputEvent)
    """Input Event. String Input Event Flags."""

    in_evt_vnd = bitfield32(19)
    """Input Event Vendor. String Input Vendor Event Flags."""

    in_dca = int16(21, scale_register=2, unit='A')
    """Amps. String Input Current."""

    in_dc_ahr = uint32(22, scale_register=3, unit='Ah')
    """Amp-hours. String Input Amp-Hours."""


class StringCombinerCurrent(SunSpecComponent):
    """SunSpec model 401: String Combiner (Current)."""

    dca_max = uint16(5, scale_register=2, unit='A')
    """Rating. Maximum DC Current Rating."""

    n = uint16(6)
    """N. Number of Inputs."""

    evt = bitfield32(7, Event)
    """Event. Events."""

    evt_vnd = bitfield32(9)
    """Vendor Event. Vendor defined events."""

    dca = int16(11, scale_register=2, unit='A')
    """Amps. Total measured current."""

    dc_ahr = uint32(12, scale_register=3, unit='Ah')
    """Amp-hours. Total metered Amp-hours."""

    dcv = uint16(14, scale_register=4, unit='V')
    """Voltage. Output Voltage."""

    tmp = int16(15, unit='C')
    """Temp. Internal operating temperature."""

    string = repeating_group(uint16(6), StringCombinerCurrentString, stride=8)
