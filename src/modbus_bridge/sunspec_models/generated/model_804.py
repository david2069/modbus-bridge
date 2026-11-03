"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_804.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    uint16,
    uint32,
)


class StringStatus(IntFlag):
    STRING_ENABLED = 1 << 0
    CONTACTOR_STATUS = 1 << 1


class ConnectionFailureReason(IntEnum):
    NO_FAILURE = 0
    BUTTON_PUSHED = 1
    STR_GROUND_FAULT = 2
    OUTSIDE_VOLTAGE_RANGE = 3
    STRING_NOT_ENABLED = 4
    FUSE_OPEN = 5
    CONTACTOR_FAILURE = 6
    PRECHARGE_FAILURE = 7
    STRING_FAULT = 8


class ContactorStatus(IntFlag):
    CONTACTOR_0 = 1 << 0
    CONTACTOR_1 = 1 << 1
    CONTACTOR_2 = 1 << 2
    CONTACTOR_3 = 1 << 3
    CONTACTOR_4 = 1 << 4
    CONTACTOR_5 = 1 << 5
    CONTACTOR_6 = 1 << 6
    CONTACTOR_7 = 1 << 7
    CONTACTOR_8 = 1 << 8
    CONTACTOR_9 = 1 << 9
    CONTACTOR_10 = 1 << 10
    CONTACTOR_11 = 1 << 11
    CONTACTOR_12 = 1 << 12
    CONTACTOR_13 = 1 << 13
    CONTACTOR_14 = 1 << 14
    CONTACTOR_15 = 1 << 15
    CONTACTOR_16 = 1 << 16
    CONTACTOR_17 = 1 << 17
    CONTACTOR_18 = 1 << 18
    CONTACTOR_19 = 1 << 19
    CONTACTOR_20 = 1 << 20
    CONTACTOR_21 = 1 << 21
    CONTACTOR_22 = 1 << 22
    CONTACTOR_23 = 1 << 23
    CONTACTOR_24 = 1 << 24
    CONTACTOR_25 = 1 << 25
    CONTACTOR_26 = 1 << 26
    CONTACTOR_27 = 1 << 27
    CONTACTOR_28 = 1 << 28
    CONTACTOR_29 = 1 << 29
    CONTACTOR_30 = 1 << 30


class StringEvent1(IntFlag):
    COMMUNICATION_ERROR = 1 << 0
    OVER_TEMP_ALARM = 1 << 1
    OVER_TEMP_WARNING = 1 << 2
    UNDER_TEMP_ALARM = 1 << 3
    UNDER_TEMP_WARNING = 1 << 4
    OVER_CHARGE_CURRENT_ALARM = 1 << 5
    OVER_CHARGE_CURRENT_WARNING = 1 << 6
    OVER_DISCHARGE_CURRENT_ALARM = 1 << 7
    OVER_DISCHARGE_CURRENT_WARNING = 1 << 8
    OVER_VOLT_ALARM = 1 << 9
    OVER_VOLT_WARNING = 1 << 10
    UNDER_VOLT_ALARM = 1 << 11
    UNDER_VOLT_WARNING = 1 << 12
    UNDER_SOC_MIN_ALARM = 1 << 13
    UNDER_SOC_MIN_WARNING = 1 << 14
    OVER_SOC_MAX_ALARM = 1 << 15
    OVER_SOC_MAX_WARNING = 1 << 16
    VOLTAGE_IMBALANCE_WARNING = 1 << 17
    TEMPERATURE_IMBALANCE_ALARM = 1 << 18
    TEMPERATURE_IMBALANCE_WARNING = 1 << 19
    CONTACTOR_ERROR = 1 << 20
    FAN_ERROR = 1 << 21
    GROUND_FAULT = 1 << 22
    OPEN_DOOR_ERROR = 1 << 23
    RESERVED_1 = 1 << 24
    OTHER_ALARM = 1 << 25
    OTHER_WARNING = 1 << 26
    RESERVED_2 = 1 << 27
    CONFIGURATION_ALARM = 1 << 28
    CONFIGURATION_WARNING = 1 << 29


class ConnectDisconnectString(IntEnum):
    CONNECT_STRING = 1
    DISCONNECT_STRING = 2


class LithiumIonStringLithiumIonStringModule(Component):
    """One 'lithium_ion_string_module' block of SunSpec model 804."""

    mod_n_cell = uint16(48)
    """Module Cell Count. Count of all cells in the module."""

    mod_so_c = uint16(49, scale_register=38, unit='%')
    """Module SoC. Module state of charge, expressed as a percentage."""

    mod_so_h = uint16(50, scale_register=39, unit='%')
    """Module SoH. Module state of health, expressed as a percentage."""

    mod_cell_v_max = uint16(51, scale_register=43, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the module."""

    mod_cell_v_max_cell = uint16(52)
    """Max Cell Voltage Cell. Cell with maximum voltage."""

    mod_cell_v_min = uint16(53, scale_register=43, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the module."""

    mod_cell_v_min_cell = uint16(54)
    """Min Cell Voltage Cell. Cell with minimum voltage."""

    mod_cell_v_avg = uint16(55, scale_register=43, unit='V')
    """Average Cell Voltage. Average voltage for all cells in the module."""

    mod_cell_tmp_max = int16(56, scale_register=44, unit='C')
    """Max Cell Temperature. Maximum temperature for all cells in the module."""

    mod_cell_tmp_max_cell = uint16(57)
    """Max Cell Temperature Cell. Cell with maximum temperature."""

    mod_cell_tmp_min = int16(58, scale_register=44, unit='C')
    """Min Cell Temperature. Minimum temperature for all cells in the module."""

    mod_cell_tmp_min_cell = uint16(59)
    """Min Cell Temperature Cell. Cell with minimum temperature."""

    mod_cell_tmp_avg = int16(60, scale_register=44, unit='C')
    """Average Cell Temperature. Average temperature for all cells in the module."""


class LithiumIonString(SunSpecComponent):
    """SunSpec model 804: Lithium-Ion String Model."""

    idx = uint16(2)
    """String Index. Index of the string within the bank."""

    n_mod = uint16(3)
    """Module Count. Count of modules in the string."""

    st = bitfield32(4, StringStatus)
    """String Status. Current status of the string."""

    con_fail = enum16(6, ConnectionFailureReason)
    """Connection Failure Reason."""

    n_cell_bal = uint16(7)
    """String Cell Balancing Count. Number of cells currently being balanced in the
    string."""

    so_c = uint16(8, scale_register=38, unit='%')
    """String State of Charge. Battery string state of charge, expressed as a
    percentage."""

    do_d = uint16(9, scale_register=40, unit='%')
    """String Depth of Discharge. Depth of discharge for the string, expressed as a
    percentage."""

    n_cyc = uint32(10)
    """String Cycle Count. Number of discharge cycles executed upon the string."""

    so_h = uint16(12, scale_register=39, unit='%')
    """String State of Health. Battery string state of health, expressed as a
    percentage."""

    a = int16(13, scale_register=41, unit='A')
    """String Current. String current measurement."""

    v = uint16(14, scale_register=42, unit='V')
    """String Voltage. String voltage measurement."""

    cell_v_max = uint16(15, scale_register=43, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the string."""

    cell_v_max_mod = uint16(16)
    """Max Cell Voltage Module. Module containing the cell with maximum cell voltage."""

    cell_v_min = uint16(17, scale_register=43, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the string."""

    cell_v_min_mod = uint16(18)
    """Min Cell Voltage Module. Module containing the cell with minimum cell voltage."""

    cell_v_avg = uint16(19, scale_register=43, unit='V')
    """Average Cell Voltage. Average voltage for all cells in the string."""

    mod_tmp_max = int16(20, scale_register=44, unit='C')
    """Max Module Temperature. Maximum temperature for all modules in the string."""

    mod_tmp_max_mod = uint16(21)
    """Max Module Temperature Module. Module with the maximum temperature."""

    mod_tmp_min = int16(22, scale_register=44, unit='C')
    """Min Module Temperature. Minimum temperature for all modules in the string."""

    mod_tmp_min_mod = uint16(23)
    """Min Module Temperature Module. Module with the minimum temperature."""

    mod_tmp_avg = int16(24, scale_register=44, unit='C')
    """Average Module Temperature. Average temperature for all modules in the string."""

    con_st = bitfield32(26, ContactorStatus)
    """Contactor Status. Status of the contactor(s) for the string."""

    evt1 = bitfield32(28, StringEvent1)
    """String Event 1. Alarms, warnings and status values."""

    evt2 = bitfield32(30)
    """String Event 2. Alarms, warnings and status values."""

    evt_vnd1 = bitfield32(32)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(34)
    """Vendor Event Bitfield 2. Vendor defined events."""

    set_ena = enum16(36, writable=True)
    """Enable/Disable String. Enables and disables the string. Should reset to 0 upon
    completion."""

    set_con = enum16(37, ConnectDisconnectString, writable=True)
    """Connect/Disconnect String. Connects and disconnects the string."""

    lithium_ion_string_module = repeating_group(uint16(3), LithiumIonStringLithiumIonStringModule, stride=16)
