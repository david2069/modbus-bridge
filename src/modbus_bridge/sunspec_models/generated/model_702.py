"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_702.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield16,
    bitfield32,
    enum16,
    uint16,
)


class NormalOperatingCategory(IntEnum):
    CAT_A = 0
    CAT_B = 1


class AbnormalOperatingCategory(IntEnum):
    CAT_1 = 0
    CAT_2 = 1
    CAT_3 = 2


class SupportedControlModes(IntFlag):
    MAX_W = 1 << 0
    FIXED_W = 1 << 1
    FIXED_VAR = 1 << 2
    FIXED_PF = 1 << 3
    VOLT_VAR = 1 << 4
    FREQ_WATT = 1 << 5
    DYN_REACT_CURR = 1 << 6
    LV_TRIP = 1 << 7
    HV_TRIP = 1 << 8
    WATT_VAR = 1 << 9
    VOLT_WATT = 1 << 10
    SCHEDULED = 1 << 11
    LF_TRIP = 1 << 12
    HF_TRIP = 1 << 13


class IntentionalIslandCategories(IntFlag):
    UNCATEGORIZED = 1 << 0
    INT_ISL_CAPABLE = 1 << 1
    BLACK_START_CAPABLE = 1 << 2
    ISOCH_CAPABLE = 1 << 3


class DERCapacity(SunSpecComponent):
    """SunSpec model 702: DER Capacity."""

    w_max_rtg = uint16(2, scale_register=45, unit='W')
    """Active Power Max Rating. Maximum active power rating at unity power factor in
    watts."""

    w_ovr_ext_rtg = uint16(3, scale_register=45, unit='W')
    """Active Power (Over-Excited) Rating. Active power rating at specified over-
    excited power factor in watts."""

    w_ovr_ext_rtg_pf = uint16(4, scale_register=46)
    """Specified Over-Excited PF. Specified over-excited power factor."""

    w_und_ext_rtg = uint16(5, scale_register=45, unit='W')
    """Active Power (Under-Excited) Rating. Active power rating at specified under-
    excited power factor in watts."""

    w_und_ext_rtg_pf = uint16(6, scale_register=46)
    """Specified Under-Excited PF. Specified under-excited power factor."""

    va_max_rtg = uint16(7, scale_register=47, unit='VA')
    """Apparent Power Max Rating. Maximum apparent power rating in voltamperes."""

    var_max_inj_rtg = uint16(8, scale_register=48, unit='Var')
    """Reactive Power Injected Rating. Maximum injected reactive power rating in
    vars."""

    var_max_abs_rtg = uint16(9, scale_register=48, unit='Var')
    """Reactive Power Absorbed Rating. Maximum absorbed reactive power rating in
    vars."""

    w_cha_rte_max_rtg = uint16(10, scale_register=45, unit='W')
    """Charge Rate Max Rating. Maximum active power charge rate in watts."""

    w_dis_cha_rte_max_rtg = uint16(11, scale_register=45, unit='W')
    """Discharge Rate Max Rating. Maximum active power discharge rate in watts."""

    va_cha_rte_max_rtg = uint16(12, scale_register=47, unit='VA')
    """Charge Rate Max VA Rating. Maximum apparent power charge rate in voltamperes."""

    va_dis_cha_rte_max_rtg = uint16(13, scale_register=47, unit='VA')
    """Discharge Rate Max VA Rating. Maximum apparent power discharge rate in
    voltamperes."""

    v_nom_rtg = uint16(14, scale_register=49, unit='V')
    """AC Voltage Nominal Rating."""

    v_max_rtg = uint16(15, scale_register=49, unit='V')
    """AC Voltage Max Rating. AC voltage maximum rating."""

    v_min_rtg = uint16(16, scale_register=49, unit='V')
    """AC Voltage Min Rating. AC voltage minimum rating."""

    a_max_rtg = uint16(17, scale_register=50, unit='A')
    """AC Current Max Rating. AC current maximum rating in amps."""

    pf_ovr_ext_rtg = uint16(18, scale_register=46)
    """PF Over-Excited Rating (Unused). Unused. Please use WOvrExtRtgPF."""

    pf_und_ext_rtg = uint16(19, scale_register=46)
    """PF Under-Excited Rating (Unused). Unused. Please use WUndExtRtgPF."""

    react_suscept_rtg = uint16(20, scale_register=51, unit='S')
    """Reactive Susceptance. Reactive susceptance that remains connected to the Area
    EPS in the cease to energize and trip state."""

    nor_op_cat_rtg = enum16(21, NormalOperatingCategory)
    """Normal Operating Category. Normal operating performance category as specified
    in IEEE 1547-2018."""

    abn_op_cat_rtg = enum16(22, AbnormalOperatingCategory)
    """Abnormal Operating Category. Abnormal operating performance category as
    specified in IEEE 1547-2018."""

    ctrl_modes = bitfield32(23, SupportedControlModes)
    """Supported Control Modes. Supported control mode functions."""

    int_island_cat_rtg = bitfield16(25, IntentionalIslandCategories)
    """Intentional Island Categories."""

    w_max = uint16(26, scale_register=45, writable=True, unit='W')
    """Active Power Max Setting. Maximum active power setting used to adjust maximum
    active power setting."""

    w_max_ovr_ext = uint16(27, scale_register=45, writable=True, unit='W')
    """Active Power (Over-Excited) Setting. Active power setting at specified over-
    excited power factor in watts."""

    w_ovr_ext_pf = uint16(28, scale_register=46, writable=True)
    """Specified Over-Excited PF. Specified over-excited power factor."""

    w_max_und_ext = uint16(29, scale_register=45, writable=True, unit='W')
    """Active Power (Under-Excited) Setting. Active power setting at specified under-
    excited power factor in watts."""

    w_und_ext_pf = uint16(30, scale_register=46, writable=True)
    """Specified Under-Excited PF. Specified under-excited power factor."""

    va_max = uint16(31, scale_register=47, writable=True, unit='VA')
    """Apparent Power Max Setting. Maximum apparent power setting used to adjust
    maximum apparent power rating."""

    var_max_inj = uint16(32, scale_register=48, writable=True, unit='Var')
    """Reactive Power Injected Setting. Maximum injected reactive power setting used
    to adjust maximum injected reactive power rating."""

    var_max_abs = uint16(33, scale_register=48, writable=True, unit='Var')
    """Reactive Power Absorbed Setting. Maximum absorbed reactive power setting used
    to adjust maximum absorbed reactive power rating."""

    w_cha_rte_max = uint16(34, scale_register=45, writable=True, unit='W')
    """Charge Rate Max Setting. Maximum active power charge rate setting used to
    adjust maximum active power charge rate rating."""

    w_dis_cha_rte_max = uint16(35, scale_register=45, writable=True, unit='W')
    """Discharge Rate Max Setting. Maximum active power discharge rate setting used
    to adjust maximum active power discharge rate rating."""

    va_cha_rte_max = uint16(36, scale_register=47, writable=True, unit='VA')
    """Charge Rate Max VA Setting. Maximum apparent power charge rate setting used to
    adjust maximum apparent power charge rate rating."""

    va_dis_cha_rte_max = uint16(37, scale_register=47, writable=True, unit='VA')
    """Discharge Rate Max VA Setting. Maximum apparent power discharge rate setting
    used to adjust maximum apparent power discharge rate rating."""

    v_nom = uint16(38, scale_register=49, writable=True, unit='V')
    """Nominal AC Voltage Setting."""

    v_max = uint16(39, scale_register=49, writable=True, unit='V')
    """AC Voltage Max Setting. AC voltage maximum setting used to adjust AC voltage
    maximum rating."""

    v_min = uint16(40, scale_register=49, writable=True, unit='V')
    """AC Voltage Min Setting. AC voltage minimum setting used to adjust AC voltage
    minimum rating."""

    a_max = uint16(41, scale_register=50, writable=True, unit='A')
    """AC Current Max Setting. Maximum AC current setting used to adjust maximum AC
    current rating."""

    pf_ovr_ext = uint16(42, scale_register=46, writable=True)
    """PF Over-Excited Setting (Unused). Unused. Please use WOvrExtPF."""

    pf_und_ext = uint16(43, scale_register=46, writable=True)
    """PF Under-Excited Setting (Unused). Unused. Please use WUndExtPF."""

    int_island_cat = bitfield16(44, IntentionalIslandCategories, writable=True)
    """Intentional Island Categories."""
