"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_807.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    model_length_group,
    uint16,
)


class ModuleStatus(IntFlag):
    MODULE_ENABLED = 1 << 0
    CONTACTOR_STATUS = 1 << 1


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


class ModuleEvent1(IntFlag):
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
    RESERVED_1 = 1 << 18
    RESERVED_2 = 1 << 19
    CONTACTOR_ERROR = 1 << 20
    FAN_ERROR = 1 << 21
    GROUND_FAULT = 1 << 22
    OPEN_DOOR_ERROR = 1 << 23
    RESERVED_3 = 1 << 24
    RESERVED_4 = 1 << 25
    RESERVED_5 = 1 << 26
    FIRE_ALARM = 1 << 27
    MODULE_CONFIGURATION_ALARM = 1 << 28
    MODULE_CONFIGURATION_WARNING = 1 << 29


class ModuleEvent2(IntFlag):
    LEAK_ALARM = 1 << 0
    PUMP_ALARM = 1 << 1
    HIGH_PRESSURE_ALARM = 1 << 2
    HIGH_PRESSURE_WARNING = 1 << 3
    LOW_FLOW_ALARM = 1 << 4
    LOW_FLOW_WARNING = 1 << 5


class ConnectionFailureReason(IntEnum):
    NO_FAILURE = 0
    BUTTON_PUSHED = 1
    MODULE_GROUND_FAULT = 2
    OUTSIDE_VOLTAGE_RANGE = 3
    MODULE_NOT_ENABLED = 4
    FUSE_OPEN = 5
    CONTACTOR_FAILURE = 6
    PRECHARGE_FAILURE = 7
    MODULE_FAULT = 8


class EnableDisableModule(IntEnum):
    ENABLE_MODULE = 1
    DISABLE_MODULE = 2


class ConnectDisconnectModule(IntEnum):
    CONNECT_MODULE = 1
    DISCONNECT_MODULE = 2


class DisabledReason(IntEnum):
    NONE = 0
    FAULT = 1
    MAINTENANCE = 2
    EXTERNAL = 3
    OTHER = 4


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
    RESERVED_1 = 1 << 18
    RESERVED_2 = 1 << 19
    CONTACTOR_ERROR = 1 << 20
    FAN_ERROR = 1 << 21
    GROUND_FAULT = 1 << 22
    OPEN_DOOR_ERROR = 1 << 23
    RESERVED_3 = 1 << 24
    OTHER_ALARM = 1 << 25
    OTHER_WARNING = 1 << 26
    FIRE_ALARM = 1 << 27
    CONFIGURATION_ALARM = 1 << 28
    CONFIGURATION_WARNING = 1 << 29


class StringEvent2(IntFlag):
    LEAK_ALARM = 1 << 0
    PUMP_ALARM = 1 << 1
    HIGH_PRESSURE_ALARM = 1 << 2
    HIGH_PRESSURE_WARNING = 1 << 3
    LOW_FLOW_ALARM = 1 << 4
    LOW_FLOW_WARNING = 1 << 5


class FlowBatteryStringModule(Component):
    """One 'module' block of SunSpec model 807."""

    mod_idx = uint16(36)
    """Module Index. Index of the module within the string."""

    mod_n_stk = uint16(37)
    """Stack Count. Number of stacks in this module."""

    mod_st = bitfield32(38, ModuleStatus)
    """Module Status. Current status of the module."""

    mod_so_c = uint16(40, scale_register=33, unit='%')
    """Module State of Charge. State of charge for this module."""

    mod_ocv = uint16(41, scale_register=34, unit='V')
    """Open Circuit Voltage. Open circuit voltage for this module."""

    mod_v = uint16(42, scale_register=30, unit='V')
    """External Voltage. External voltage fo this module."""

    mod_cell_v_max = uint16(43, scale_register=31, unit='V')
    """Maximum Cell Voltage. Maximum voltage for all cells in this module."""

    mod_cell_v_max_cell = uint16(44)
    """Max Cell Voltage Cell. Cell with the maximum cell voltage."""

    mod_cell_v_min = uint16(45, scale_register=31, unit='V')
    """Minimum Cell Voltage. Minimum voltage for all cells in this module."""

    mod_cell_v_min_cell = uint16(46)
    """Min Cell Voltage Cell. Cell with the minimum cell voltage."""

    mod_cell_v_avg = uint16(47, scale_register=31, unit='V')
    """Average Cell Voltage. Average voltage for all cells in this module."""

    mod_ano_tmp = uint16(48, scale_register=32, unit='C')
    """Anolyte Temperature."""

    mod_cat_tmp = uint16(49, scale_register=32, unit='C')
    """Catholyte Temperature."""

    mod_con_st = bitfield32(50, ContactorStatus)
    """Contactor Status."""

    mod_evt1 = bitfield32(52, ModuleEvent1)
    """Module Event 1. Alarms, warnings and status values."""

    mod_evt2 = bitfield32(54, ModuleEvent2)
    """Module Event 2. Alarms, warnings and status values."""

    mod_con_fail = enum16(56, ConnectionFailureReason)
    """Connection Failure Reason."""

    mod_set_ena = enum16(57, EnableDisableModule, writable=True)
    """Enable/Disable Module. Enables and disables the module."""

    mod_set_con = enum16(58, ConnectDisconnectModule, writable=True)
    """Connect/Disconnect Module. Connects and disconnects the module."""

    mod_dis_rsn = enum16(59, DisabledReason)
    """Disabled Reason. Reason why the module is currently disabled."""


class FlowBatteryString(SunSpecComponent):
    """SunSpec model 807: Flow Battery String Model."""

    idx = uint16(2)
    """String Index. Index of the string within the bank."""

    n_mod = uint16(3)
    """Module Count. Number of modules in this string."""

    n_mod_con = uint16(4)
    """Connected Module Count. Number of electrically connected modules in this
    string."""

    mod_v_max = uint16(5, scale_register=30, unit='V')
    """Max Module Voltage. Maximum voltage for all modules in the string."""

    mod_v_max_mod = uint16(6)
    """Max Module Voltage Module. Module with the maximum voltage."""

    mod_v_min = uint16(7, scale_register=30, unit='V')
    """Min Module Voltage. Minimum voltage for all modules in the string."""

    mod_v_min_mod = uint16(8)
    """Min Module Voltage Module. Module with the minimum voltage."""

    mod_v_avg = uint16(9, scale_register=30, unit='V')
    """Average Module Voltage. Average voltage for all modules in the string."""

    cell_v_max = uint16(10, scale_register=31, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the string."""

    cell_v_max_mod = uint16(11)
    """Max Cell Voltage Module. Module containing the cell with the maximum voltage."""

    cell_v_max_stk = uint16(12)
    """Max Cell Voltage Stack. Stack containing the cell with the maximum voltage."""

    cell_v_min = uint16(13, scale_register=31, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the string."""

    cell_v_min_mod = uint16(14)
    """Min Cell Voltage Module. Module containing the cell with the minimum voltage."""

    cell_v_min_stk = uint16(15)
    """Min Cell Voltage Stack. Stack containing the cell with the minimum voltage."""

    cell_v_avg = uint16(16, scale_register=31, unit='V')
    """Average Cell Voltage. Average voltage for all cells in the string."""

    tmp_max = int16(17, scale_register=32, unit='C')
    """Max Temperature. Maximum electrolyte temperature for all modules in the
    string."""

    tmp_max_mod = uint16(18)
    """Max Temperature Module. Module with the maximum temperature."""

    tmp_min = int16(19, scale_register=32, unit='C')
    """Min Temperature. Minimum electrolyte temperature for all modules in the
    string."""

    tmp_min_mod = uint16(20)
    """Min Temperature Module. Module with the minimum temperature."""

    tmp_avg = int16(21, scale_register=32, unit='C')
    """Average Temperature. Average electrolyte temperature for all modules in the
    string."""

    evt1 = bitfield32(22, StringEvent1)
    """String Event 1. Alarms, warnings and status values."""

    evt2 = bitfield32(24, StringEvent2)
    """String Event 2. Alarms, warnings and status values."""

    evt_vnd1 = bitfield32(26)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(28)
    """Vendor Event Bitfield 2. Vendor defined events."""

    module = model_length_group(FlowBatteryStringModule, start=36, stride=24)
