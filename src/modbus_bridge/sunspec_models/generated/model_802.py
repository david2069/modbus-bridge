"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_802.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int16,
    uint16,
    uint32,
)


class ChargeStatus(IntEnum):
    OFF = 1
    EMPTY = 2
    DISCHARGING = 3
    CHARGING = 4
    FULL = 5
    HOLDING = 6
    TESTING = 7


class ControlMode(IntEnum):
    REMOTE = 0
    LOCAL = 1


class BatteryType(IntEnum):
    NOT_APPLICABLE_UNKNOWN = 0
    LEAD_ACID = 1
    NICKEL_METAL_HYDRATE = 2
    NICKEL_CADMIUM = 3
    LITHIUM_ION = 4
    CARBON_ZINC = 5
    ZINC_CHLORIDE = 6
    ALKALINE = 7
    RECHARGEABLE_ALKALINE = 8
    SODIUM_SULFUR = 9
    FLOW = 10
    OTHER = 99


class StateOfTheBatteryBank(IntEnum):
    DISCONNECTED = 1
    INITIALIZING = 2
    CONNECTED = 3
    STANDBY = 4
    SOC_PROTECTION = 5
    SUSPENDING = 6
    FAULT = 99


class BatteryEvent1Bitfield(IntFlag):
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
    CURRENT_IMBALANCE_WARNING = 1 << 24
    OTHER_ALARM = 1 << 25
    OTHER_WARNING = 1 << 26
    RESERVED_1 = 1 << 27
    CONFIGURATION_ALARM = 1 << 28
    CONFIGURATION_WARNING = 1 << 29


class InverterStateRequest(IntEnum):
    NO_REQUEST = 0
    START = 1
    STOP = 2


class SetOperation(IntEnum):
    CONNECT = 1
    DISCONNECT = 2


class SetInverterState(IntEnum):
    INVERTER_STOPPED = 1
    INVERTER_STANDBY = 2
    INVERTER_STARTED = 3


class Battery(SunSpecComponent):
    """SunSpec model 802: Battery Base Model."""

    ah_rtg = uint16(2, scale_register=52, unit='Ah')
    """Nameplate Charge Capacity. Nameplate charge capacity in amp-hours."""

    wh_rtg = uint16(3, scale_register=53, unit='Wh')
    """Nameplate Energy Capacity. Nameplate energy capacity in DC watt-hours."""

    w_cha_rte_max = uint16(4, scale_register=54, unit='W')
    """Nameplate Max Charge Rate. Maximum rate of energy transfer into the storage
    device in DC watts."""

    w_dis_cha_rte_max = uint16(5, scale_register=54, unit='W')
    """Nameplate Max Discharge Rate. Maximum rate of energy transfer out of the
    storage device in DC watts."""

    dis_cha_rte = uint16(6, scale_register=55, unit='%WHRtg')
    """Self Discharge Rate. Self discharge rate. Percentage of capacity (WHRtg)
    discharged per day."""

    so_c_max = uint16(7, scale_register=56, unit='%WHRtg')
    """Nameplate Max SoC. Manufacturer maximum state of charge, expressed as a
    percentage."""

    so_c_min = uint16(8, scale_register=56, unit='%WHRtg')
    """Nameplate Min SoC. Manufacturer minimum state of charge, expressed as a
    percentage."""

    soc_rsv_max = uint16(9, scale_register=56, writable=True, unit='%WHRtg')
    """Max Reserve Percent. Setpoint for maximum reserve for storage as a percentage
    of the nominal maximum storage."""

    so_c_rsv_min = uint16(10, scale_register=56, writable=True, unit='%WHRtg')
    """Min Reserve Percent. Setpoint for minimum reserve for storage as a percentage
    of the nominal maximum storage."""

    so_c = uint16(11, scale_register=56, unit='%WHRtg')
    """State of Charge. State of charge, expressed as a percentage."""

    do_d = uint16(12, scale_register=57, unit='%')
    """Depth of Discharge. Depth of discharge, expressed as a percentage."""

    so_h = uint16(13, scale_register=58, unit='%')
    """State of Health. Percentage of battery life remaining."""

    n_cyc = uint32(14)
    """Cycle Count. Number of cycles executed in the battery."""

    cha_st = enum16(16, ChargeStatus)
    """Charge Status. Charge status of storage device. Enumeration."""

    loc_rem_ctl = enum16(17, ControlMode)
    """Control Mode. Battery control mode. Enumeration."""

    hb = uint16(18)
    """Battery Heartbeat. Value is incremented every second with periodic resets to
    zero."""

    ctrl_hb = uint16(19, writable=True)
    """Controller Heartbeat. Value is incremented every second with periodic resets
    to zero."""

    alm_rst = uint16(20, writable=True)
    """Alarm Reset. Used to reset any latched alarms. 1 = Reset."""

    typ = enum16(21, BatteryType)
    """Battery Type. Type of battery. Enumeration."""

    state = enum16(22, StateOfTheBatteryBank)
    """State of the Battery Bank. State of the battery bank. Enumeration."""

    state_vnd = enum16(23)
    """Vendor Battery Bank State. Vendor specific battery bank state. Enumeration."""

    warr_dt = uint32(24)
    """Warranty Date. Date the device warranty expires."""

    evt1 = bitfield32(26, BatteryEvent1Bitfield)
    """Battery Event 1 Bitfield. Alarms and warnings."""

    evt2 = bitfield32(28)
    """Battery Event 2 Bitfield. Alarms and warnings."""

    evt_vnd1 = bitfield32(30)
    """Vendor Event Bitfield 1. Vendor defined events."""

    evt_vnd2 = bitfield32(32)
    """Vendor Event Bitfield 2. Vendor defined events."""

    v = uint16(34, scale_register=59, unit='V')
    """External Battery Voltage. DC Bus Voltage."""

    v_max = uint16(35, scale_register=59, unit='V')
    """Max Battery Voltage. Instantaneous maximum battery voltage."""

    v_min = uint16(36, scale_register=59, unit='V')
    """Min Battery Voltage. Instantaneous minimum battery voltage."""

    cell_v_max = uint16(37, scale_register=60, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the bank."""

    cell_v_max_str = uint16(38)
    """Max Cell Voltage String. String containing the cell with maximum voltage."""

    cell_v_max_mod = uint16(39)
    """Max Cell Voltage Module. Module containing the cell with maximum voltage."""

    cell_v_min = uint16(40, scale_register=60, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the bank."""

    cell_v_min_str = uint16(41)
    """Min Cell Voltage String. String containing the cell with minimum voltage."""

    cell_v_min_mod = uint16(42)
    """Min Cell Voltage Module. Module containing the cell with minimum voltage."""

    cell_v_avg = uint16(43, scale_register=60, unit='V')
    """Average Cell Voltage. Average cell voltage for all cells in the bank."""

    a = int16(44, scale_register=61, unit='A')
    """Total DC Current. Total DC current flowing to/from the battery bank."""

    a_cha_max = uint16(45, scale_register=62, unit='A')
    """Max Charge Current. Instantaneous maximum DC charge current."""

    a_dis_cha_max = uint16(46, scale_register=62, unit='A')
    """Max Discharge Current. Instantaneous maximum DC discharge current."""

    w = int16(47, scale_register=63, unit='W')
    """Total Power. Total power flowing to/from the battery bank."""

    req_inv_state = enum16(48, InverterStateRequest)
    """Inverter State Request. Request from battery to start or stop the inverter.
    Enumeration."""

    req_w = int16(49, scale_register=63, unit='W')
    """Battery Power Request. AC Power requested by battery."""

    set_op = enum16(50, SetOperation, writable=True)
    """Set Operation. Instruct the battery bank to perform an operation such as
    connecting. Enumeration."""

    set_inv_state = enum16(51, SetInverterState, writable=True)
    """Set Inverter State. Set the current state of the inverter."""
