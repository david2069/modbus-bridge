"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_803.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    uint16,
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


class DisabledReason(IntEnum):
    NONE = 0
    FAULT = 1
    MAINTENANCE = 2
    EXTERNAL = 3
    OTHER = 4


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


class EnableDisableString(IntEnum):
    ENABLE_STRING = 1
    DISABLE_STRING = 2


class ConnectDisconnectString(IntEnum):
    CONNECT_STRING = 1
    DISCONNECT_STRING = 2


class LithiumIonBankString(Component):
    """One 'string' block of SunSpec model 803."""

    str_n_mod = uint16(28)
    """Module Count. Count of modules in the string."""

    str_st = bitfield32(29, StringStatus)
    """String Status. Current status of the string."""

    str_con_fail = enum16(31, ConnectionFailureReason)
    """Connection Failure Reason."""

    str_so_c = uint16(32, scale_register=26, unit='%')
    """String State of Charge. Battery string state of charge, expressed as a
    percentage."""

    str_so_h = uint16(33, scale_register=25, unit='%')
    """String State of Health. Battery string state of health, expressed as a
    percentage."""

    str_a = int16(34, scale_register=24, unit='A')
    """String Current. String current measurement."""

    str_cell_v_max = uint16(35, scale_register=22, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the string."""

    str_cell_v_max_mod = uint16(36)
    """Max Cell Voltage Module. Module containing the maximum cell voltage."""

    str_cell_v_min = uint16(37, scale_register=22, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the string."""

    str_cell_v_min_mod = uint16(38)
    """Min Cell Voltage Module. Module containing the minimum cell voltage."""

    str_cell_v_avg = uint16(39, scale_register=22, unit='V')
    """Average Cell Voltage. Average voltage for all cells in the string."""

    str_mod_tmp_max = int16(40, scale_register=23, unit='C')
    """Max Module Temperature. Maximum temperature for all modules in the bank."""

    str_mod_tmp_max_mod = uint16(41)
    """Max Module Temperature Module. Module with the maximum temperature."""

    str_mod_tmp_min = int16(42, scale_register=23, unit='C')
    """Min Module Temperature. Minimum temperature for all modules in the bank."""

    str_mod_tmp_min_mod = uint16(43)
    """Min Module Temperature Module. Module with the minimum temperature."""

    str_mod_tmp_avg = int16(44, scale_register=23, unit='C')
    """Average Module Temperature. Average temperature for all modules in the bank."""

    str_dis_rsn = enum16(45, DisabledReason)
    """Disabled Reason. Reason why the string is currently disabled."""

    str_con_st = bitfield32(46, ContactorStatus)
    """Contactor Status. Status of the contactor(s) for the string."""

    str_evt1 = bitfield32(48, StringEvent1)
    """String Event 1. Alarms, warnings and status values."""

    str_evt2 = bitfield32(50)
    """String Event 2. Alarms, warnings and status values."""

    str_evt_vnd1 = bitfield32(52)
    """Vendor String Event Bitfield 1. Vendor defined events."""

    str_evt_vnd2 = bitfield32(54)
    """Vendor String Event Bitfield 2. Vendor defined events."""

    str_set_ena = enum16(56, EnableDisableString, writable=True)
    """Enable/Disable String. Enables and disables the string."""

    str_set_con = enum16(57, ConnectDisconnectString, writable=True)
    """Connect/Disconnect String. Connects and disconnects the string."""


class LithiumIonBank(SunSpecComponent):
    """SunSpec model 803: Lithium-Ion Battery Bank Model."""

    n_str = uint16(2)
    """String Count. Number of strings in the bank."""

    n_str_con = uint16(3)
    """Connected String Count. Number of strings with contactor closed."""

    mod_tmp_max = int16(4, scale_register=23, unit='C')
    """Max Module Temperature. Maximum temperature for all modules in the bank."""

    mod_tmp_max_str = uint16(5)
    """Max Module Temperature String. String containing the module with maximum
    temperature."""

    mod_tmp_max_mod = uint16(6)
    """Max Module Temperature Module. Module with maximum temperature."""

    mod_tmp_min = int16(7, scale_register=23, unit='C')
    """Min Module Temperature. Minimum temperature for all modules in the bank."""

    mod_tmp_min_str = uint16(8)
    """Min Module Temperature String. String containing the module with minimum
    temperature."""

    mod_tmp_min_mod = uint16(9)
    """Min Module Temperature Module. Module with minimum temperature."""

    mod_tmp_avg = int16(10, scale_register=23, unit='C')
    """Average Module Temperature. Average temperature for all modules in the bank."""

    str_v_max = uint16(11, scale_register=27, unit='V')
    """Max String Voltage. Maximum string voltage for all strings in the bank."""

    str_v_max_str = uint16(12)
    """Max String Voltage String. String with maximum voltage."""

    str_v_min = uint16(13, scale_register=27, unit='V')
    """Min String Voltage. Minimum string voltage for all strings in the bank."""

    str_v_min_str = uint16(14)
    """Min String Voltage String. String with minimum voltage."""

    str_v_avg = uint16(15, scale_register=27, unit='V')
    """Average String Voltage. Average string voltage for all strings in the bank."""

    str_a_max = int16(16, scale_register=24, unit='A')
    """Max String Current. Maximum current of any string in the bank."""

    str_a_max_str = uint16(17)
    """Max String Current String. String with the maximum current."""

    str_a_min = int16(18, scale_register=24, unit='A')
    """Min String Current. Minimum current of any string in the bank."""

    str_a_min_str = uint16(19)
    """Min String Current String. String with the minimum current."""

    str_a_avg = int16(20, scale_register=24, unit='A')
    """Average String Current. Average string current for all strings in the bank."""

    n_cell_bal = uint16(21)
    """Battery Cell Balancing Count. Total number of cells that are currently being
    balanced."""

    string = repeating_group(uint16(2), LithiumIonBankString, stride=32)
