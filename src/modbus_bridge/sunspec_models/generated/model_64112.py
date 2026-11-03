"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64112.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    enum16,
    sunssf,
    uint16,
)


class MPPTMode(IntEnum):
    Auto = 0
    U_Pick = 1
    Wind = 2


class SweepWidth(IntEnum):
    Half = 0
    Full = 1


class SweepMaximum(IntEnum):
    Eighty_Percent = 0
    Eighty_Five_Percent = 1
    Ninty_Percent = 2
    Ninty_Nine_Percent = 3


class GridTieMode(IntEnum):
    Disabled = 0
    Enabled = 1


class TempCompMode(IntEnum):
    Wide = 0
    Limited = 1


class AutoRestartMode(IntEnum):
    Off = 0
    Every_90_Minutes = 1
    Every_90_Minutes_if_Absorb_or_Float = 2


class AUXOutputMode(IntEnum):
    Float = 0
    Diversion_Relay = 1
    Diversion_Solid_St = 2
    Low_Batt_Disconnect = 3
    Remote = 4
    Vent_Fan = 5
    PV_Trigger = 6
    Error_Output = 7
    Night_Light = 8


class AUXOutputControl(IntEnum):
    Off = 0
    Auto = 1
    On = 2


class AUXOutputState(IntEnum):
    Disabled = 0
    Enabled = 1


class AUXOutputPolarity(IntEnum):
    Low = 0
    High = 1


class Model64112(SunSpecComponent):
    """SunSpec model 64112: OutBack FM Charge Controller."""

    port = uint16(2)
    """Port Number."""

    c_sf = sunssf(4)

    p_sf = sunssf(6)

    ah_sf = sunssf(7)

    cc_config_fault = bitfield16(9)
    """Faults."""

    cc_config_absorb_v = uint16(10, scale_register=3, unit='V')
    """Absorb."""

    cc_config_absorb_hr = uint16(11, scale_register=5, unit='Tmh')
    """Absorb Time."""

    cc_config_absorb_end_a = uint16(12, scale_register=3, unit='A')
    """Absorb End."""

    cc_config_rebulk_v = uint16(13, scale_register=3, unit='V')
    """Rebulk."""

    cc_config_float_v = uint16(14, scale_register=3, unit='V')
    """Float."""

    cc_config_max_chg_a = uint16(15, scale_register=3, unit='A')
    """Maximum Charge."""

    cc_config_equalize_v = uint16(16, scale_register=3, unit='V')
    """Equalize."""

    cc_config_equalize_hr = uint16(17, unit='Tmh')
    """Equalize Time."""

    cc_config_auto_equalize = uint16(18, unit='Tmd')
    """Auto Equalize Interval."""

    cc_config_mppt_mode = enum16(19, MPPTMode)
    """MPPT mode."""

    cc_config_sweep_width = enum16(20, SweepWidth)
    """Sweep Width."""

    cc_config_sweep_max = enum16(21, SweepMaximum)
    """Sweep Maximum."""

    cc_config_u_pick_duty_cyc = uint16(22, scale_register=3, unit='Pct')
    """U-Pick PWM Duty Cycle."""

    cc_config_grid_tie = enum16(23, GridTieMode)
    """Grid Tie Mode."""

    cc_config_temp_comp = enum16(24, TempCompMode)
    """Temp Comp Mode."""

    cc_config_temp_comp_llimt = uint16(25, scale_register=3, unit='V')
    """Temp Comp Lower Limit."""

    cc_config_temp_comp_hlimt = uint16(26, scale_register=3, unit='V')
    """Temp Comp Upper Limit."""

    cc_config_auto_restart = enum16(27, AutoRestartMode)
    """Auto Restart Mode."""

    cc_config_wakeup_voc = uint16(28, scale_register=3, unit='V')
    """Wakeup VOC Change."""

    cc_config_snooze_mode_a = uint16(29, scale_register=3, unit='A')
    """Snooze Mode."""

    cc_config_wakeup_interval = uint16(30, unit='Tms')
    """Wakeup Interval."""

    cc_config_aux_mode = enum16(31, AUXOutputMode)
    """AUX Output Mode."""

    cc_config_aux_control = enum16(32, AUXOutputControl)
    """AUX Output Control."""

    cc_config_aux_state = enum16(33, AUXOutputState)
    """AUX Output State."""

    cc_config_aux_polarity = enum16(34, AUXOutputPolarity)
    """AUX Output Polarity."""

    cc_config_aux_l_batt_disc = uint16(35, scale_register=3, unit='V')
    """AUX Low Battery Disconnect."""

    cc_config_aux_l_batt_rcon = uint16(36, scale_register=3, unit='V')
    """AUX Low Battery Reconnect."""

    cc_config_aux_l_batt_dly = uint16(37, unit='Tms')
    """AUX Low Battery Disconnect Delay."""

    cc_config_aux_vent_fan_v = uint16(38, scale_register=3, unit='V')
    """AUX Vent Fan."""

    cc_config_aux_pv_trigger_v = uint16(39, scale_register=3, unit='V')
    """AUX PV Trigger."""

    cc_config_aux_pv_trg_h_tm = uint16(40, unit='Tms')
    """AUX PV Trigger Hold Time."""

    cc_config_aux_nlite_thrs_v = uint16(41, scale_register=3, unit='V')
    """AUX Night Light Threshold."""

    cc_config_aux_nlite_on_tm = uint16(42, scale_register=5, unit='Tmh')
    """AUX Night Light On Time."""

    cc_config_aux_nlite_on_hist = uint16(43, unit='Tms')
    """AUX Night Light On Hysteresis."""

    cc_config_aux_nlite_off_hist = uint16(44, unit='Tms')
    """AUX Night Light Off Hysteresis."""

    cc_config_aux_error_batt_v = uint16(45, scale_register=3, unit='V')
    """AUX Error Output Low Battery."""

    cc_config_aux_divert_h_time = uint16(46, scale_register=3, unit='Tms')
    """AUX Divert Hold Time."""

    cc_config_aux_divert_dly_time = uint16(47, unit='Tms')
    """AUX Divert Delay Time."""

    cc_config_aux_divert_rel_v = uint16(48, scale_register=3, unit='V')
    """AUX Divert Relative."""

    cc_config_aux_divert_hyst_v = uint16(49, scale_register=3, unit='V')
    """AUX Divert Hysteresis."""

    cc_config_major_fw_rev = uint16(50)
    """FM CC Major Firmware Number."""

    cc_config_mid_fw_rev = uint16(51)
    """FM CC Mid Firmware Number."""

    cc_config_minor_fw_rev = uint16(52)
    """FM CC Minor Firmware Number."""

    cc_config_data_log_day_offset = uint16(53, unit='Tmd')
    """Set Data Log Day Offset."""

    cc_config_data_log_cur_day_off = uint16(54, unit='Tmd')
    """Current Data Log Day Offset."""

    cc_config_data_log_daily_ah = uint16(55, unit='Ah')
    """Data Log Daily (Ah)."""

    cc_config_data_log_daily_kwh = uint16(56, scale_register=8, unit='kWh')
    """Data Log Daily (kWh)."""

    cc_config_data_log_max_out_a = uint16(57, scale_register=3, unit='A')
    """Data Log Daily Maximum Output (A)."""

    cc_config_data_log_max_out_w = uint16(58, scale_register=3, unit='W')
    """Data Log Daily Maximum Output (W)."""

    cc_config_data_log_absorb_t = uint16(59, unit='Tms')
    """Data Log Daily Absorb Time."""

    cc_config_data_log_float_t = uint16(60, unit='Tms')
    """Data Log Daily Float Time."""

    cc_config_data_log_min_batt_v = uint16(61, scale_register=3, unit='V')
    """Data Log Daily Minimum Battery."""

    cc_config_data_log_max_batt_v = uint16(62, scale_register=3, unit='V')
    """Data Log Daily Maximum Battery."""

    cc_config_data_log_max_input_v = uint16(63, scale_register=3, unit='V')
    """Data Log Daily Maximum Input."""

    cc_config_data_log_clear = uint16(64)
    """Data Log Clear."""

    cc_config_data_log_clr_comp = uint16(65)
    """Data Log Clear Complement."""
