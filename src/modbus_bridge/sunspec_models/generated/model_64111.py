"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64111.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    uint16,
)


class OperatingState(IntEnum):
    Off = 0
    Float = 1
    Bulk = 2
    Absorb = 3
    EQ = 4


class Model64111(SunSpecComponent):
    """SunSpec model 64111: Basic Charge Controller."""

    port = uint16(2)
    """Port Number."""

    batt_v = uint16(8, scale_register=3, unit='V')
    """Battery Voltage."""

    array_v = uint16(9, scale_register=3, unit='V')
    """Array Voltage."""

    output_a = uint16(10, scale_register=4, unit='A')
    """Output Current."""

    input_a = uint16(11, scale_register=5, unit='A')
    """Array Current."""

    charger_st = enum16(12, OperatingState)
    """Operating State."""

    output_w = uint16(13, scale_register=5, unit='W')
    """Output Wattage."""

    today_min_bat_v = uint16(14, scale_register=3, unit='V')
    """Today's Minimum Battery Voltage."""

    today_max_bat_v = uint16(15, scale_register=3, unit='V')
    """Today's Maximum Battery Voltage."""

    vocv = uint16(16, scale_register=3, unit='V')
    """VOC."""

    today_max_voc = uint16(17, scale_register=3, unit='V')
    """Today's Maximum VOC."""

    todayk_wh_output = uint16(18, scale_register=7, unit='kWh')
    """Today's kWh."""

    today_ah_output = uint16(19, scale_register=6, unit='AH')
    """Today's AH."""

    life_time_kwh_out = uint16(20, scale_register=5, unit='kWh')
    """Lifetime kWh."""

    life_time_ah_out = uint16(21, scale_register=7, unit='kAH')
    """Lifetime kAH."""

    life_time_max_out = uint16(22, scale_register=5, unit='W')
    """Lifetime Maximum Output Wattage."""

    life_time_max_batt = uint16(23, scale_register=3, unit='V')
    """Lifetime Maximum Battery Voltage."""

    life_time_max_voc = uint16(24, scale_register=3, unit='V')
    """Lifetime Maximum VOC Voltage."""
