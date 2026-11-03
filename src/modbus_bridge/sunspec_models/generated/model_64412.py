"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64412.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
)


class DAManipulation(IntEnum):
    OFF = 0
    ON = 1


class FalsifyDeviceIdentity(IntEnum):
    OFF = 0
    ON = 1


class MeasPAlwaysNameplate(IntEnum):
    OFF = 0
    ON = 1


class MeasQAlwaysMinimum(IntEnum):
    OFF = 0
    ON = 1


class MeasQAlwaysMaximum(IntEnum):
    OFF = 0
    ON = 1


class MeasQAlwaysZero(IntEnum):
    OFF = 0
    ON = 1


class MeasZeroP(IntEnum):
    OFF = 0
    ON = 1


class MeasInvertQ(IntEnum):
    OFF = 0
    ON = 1


class MeasLowV(IntEnum):
    OFF = 0
    ON = 1


class MeasHighV(IntEnum):
    OFF = 0
    ON = 1


class MeasLowL1V(IntEnum):
    OFF = 0
    ON = 1


class MeasHighL1V(IntEnum):
    OFF = 0
    ON = 1


class MeasLowF(IntEnum):
    OFF = 0
    ON = 1


class MeasHighF(IntEnum):
    OFF = 0
    ON = 1


class MeasLowAmps(IntEnum):
    OFF = 0
    ON = 1


class MeasHighAmps(IntEnum):
    OFF = 0
    ON = 1


class MeasHighS(IntEnum):
    OFF = 0
    ON = 1


class MeasLowS(IntEnum):
    OFF = 0
    ON = 1


class MeasHighQ(IntEnum):
    OFF = 0
    ON = 1


class MeasLowQ(IntEnum):
    OFF = 0
    ON = 1


class MeasLowPF(IntEnum):
    OFF = 0
    ON = 1


class MeasLowReversedPF(IntEnum):
    OFF = 0
    ON = 1


class NameplateHighP(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowP(IntEnum):
    OFF = 0
    ON = 1


class NameplateHighS(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowS(IntEnum):
    OFF = 0
    ON = 1


class NameplateHighQ(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowQ(IntEnum):
    OFF = 0
    ON = 1


class NameplateHighNomV(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowNomV(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowAmps(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowVarmaxinj(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowVarmaxabs(IntEnum):
    OFF = 0
    ON = 1


class NameplateLowPF(IntEnum):
    OFF = 0
    ON = 1


class SettingsHighNomV(IntEnum):
    OFF = 0
    ON = 1


class SettingsLowAmps(IntEnum):
    OFF = 0
    ON = 1


class SettingsHighP(IntEnum):
    OFF = 0
    ON = 1


class SettingsLowP(IntEnum):
    OFF = 0
    ON = 1


class SettingsHighVAMax(IntEnum):
    OFF = 0
    ON = 1


class SettingsHighVarmaxinj(IntEnum):
    OFF = 0
    ON = 1


class SettingsHighVarmaxabs(IntEnum):
    OFF = 0
    ON = 1


class ChangeCommonModelID(IntEnum):
    OFF = 0
    ON = 1


class ChangeCommonModelLength(IntEnum):
    OFF = 0
    ON = 1


class DERExploitation(SunSpecComponent):
    """SunSpec model 64412: DER Cyber Exploitation."""

    da_manipulation = enum16(2, DAManipulation, writable=True)
    """DA Manipulation. Modify the device ID of the DER."""

    falsify_device_identity = enum16(3, FalsifyDeviceIdentity, writable=True)
    """Falsify Device Identity. Change the DER manufacturer and model."""

    meas_p_always_nameplate = enum16(4, MeasPAlwaysNameplate, writable=True)
    """Meas P Always Nameplate. Set the DER meas to always be at nameplate power."""

    meas_q_always_minimum = enum16(5, MeasQAlwaysMinimum, writable=True)
    """Meas Q Always Minimum. Set the DER to always be at minimum reactive power."""

    meas_q_always_maximum = enum16(6, MeasQAlwaysMaximum, writable=True)
    """Meas Q Always Maximum. Set the DER to always be at maximum reactive power."""

    meas_q_always_zero = enum16(7, MeasQAlwaysZero, writable=True)
    """Meas Q Always Zero. Set the DER to always be at zero reactive power."""

    meas_zero_p = enum16(8, MeasZeroP, writable=True)
    """Meas Zero P. Set the DER to always be at zero P, Q, and S."""

    meas_invert_q = enum16(9, MeasInvertQ, writable=True)
    """Meas Invert Q. Set the DER to reverse the Q measurement data."""

    meas_low_v = enum16(10, MeasLowV, writable=True)
    """Meas Low V. Set the DER to always measure low voltage."""

    meas_high_v = enum16(11, MeasHighV, writable=True)
    """Meas High V. Set the DER to always measure high voltage."""

    meas_low_l1_v = enum16(12, MeasLowL1V, writable=True)
    """Meas Low L1 V. Set the DER to always measure low line 1 voltage."""

    meas_high_l1_v = enum16(13, MeasHighL1V, writable=True)
    """Meas High L1 V. Set the DER to always measure high line 1 voltage."""

    meas_low_f = enum16(14, MeasLowF, writable=True)
    """Meas Low F. Set the DER to always measure low frequency."""

    meas_high_f = enum16(15, MeasHighF, writable=True)
    """Meas High F. Set the DER to always measure high frequency."""

    meas_low_amps = enum16(16, MeasLowAmps, writable=True)
    """Meas Low Amps. Set the DER to always measure low current."""

    meas_high_amps = enum16(17, MeasHighAmps, writable=True)
    """Meas High Amps. Set the DER to always measure high current."""

    meas_high_s = enum16(18, MeasHighS, writable=True)
    """Meas High S. Set the DER to always measure high apparent power."""

    meas_low_s = enum16(19, MeasLowS, writable=True)
    """Meas Low S. Set the DER to always measure low apparent power."""

    meas_high_q = enum16(20, MeasHighQ, writable=True)
    """Meas High Q. Set the DER to always measure high reactive power."""

    meas_low_q = enum16(21, MeasLowQ, writable=True)
    """Meas Low Q. Set the DER to always measure low reactive power."""

    meas_low_pf = enum16(22, MeasLowPF, writable=True)
    """Meas Low PF. Set the DER to always measure low power factor."""

    meas_low_reversed_pf = enum16(23, MeasLowReversedPF, writable=True)
    """Meas Low Reversed PF. Set the DER to always measure low reversed power factor."""

    nameplate_high_p = enum16(24, NameplateHighP, writable=True)
    """Nameplate High P. Set the DER nameplate power to be high."""

    nameplate_low_p = enum16(25, NameplateLowP, writable=True)
    """Nameplate Low P. Set the DER nameplate power to be low."""

    nameplate_high_s = enum16(26, NameplateHighS, writable=True)
    """Nameplate High S. Set the DER nameplate apparent power to be high."""

    nameplate_low_s = enum16(27, NameplateLowS, writable=True)
    """Nameplate Low S. Set the DER nameplate apparent power to be low."""

    nameplate_high_q = enum16(28, NameplateHighQ, writable=True)
    """Nameplate High Q. Set the DER nameplate reactive power to be high."""

    nameplate_low_q = enum16(29, NameplateLowQ, writable=True)
    """Nameplate Low Q. Set the DER nameplate reactive power to be low."""

    nameplate_high_nom_v = enum16(30, NameplateHighNomV, writable=True)
    """Nameplate High Nom V. Set the DER nameplate voltage to be high."""

    nameplate_low_nom_v = enum16(31, NameplateLowNomV, writable=True)
    """Nameplate Low Nom V. Set the DER nameplate voltage to be low."""

    nameplate_low_amps = enum16(32, NameplateLowAmps, writable=True)
    """Nameplate Low Amps. Set the DER nameplate current to be low."""

    nameplate_low_varmaxinj = enum16(33, NameplateLowVarmaxinj, writable=True)
    """Nameplate Low Varmaxinj. Set the DER nameplate VarMaxInj to be low."""

    nameplate_low_varmaxabs = enum16(34, NameplateLowVarmaxabs, writable=True)
    """Nameplate Low Varmaxabs. Set the DER nameplate VarMaxAbs to be low."""

    nameplate_low_pf = enum16(35, NameplateLowPF, writable=True)
    """Nameplate Low PF. Set the DER nameplate power factor to be low."""

    settings_high_nom_v = enum16(36, SettingsHighNomV, writable=True)
    """Settings High Nom V. Set the DER settings voltage to be high."""

    settings_low_amps = enum16(37, SettingsLowAmps, writable=True)
    """Settings Low Amps. Set the DER settings current to be low."""

    settings_high_p = enum16(38, SettingsHighP, writable=True)
    """Settings High P. Set the DER settings power to be high."""

    settings_low_p = enum16(39, SettingsLowP, writable=True)
    """Settings Low P. Set the DER settings power to be low."""

    settings_high_va_max = enum16(40, SettingsHighVAMax, writable=True)
    """Settings High VAMax. Set the DER settings VAMax to be high."""

    settings_high_varmaxinj = enum16(41, SettingsHighVarmaxinj, writable=True)
    """Settings High Varmaxinj. Set the DER settings VarMaxInj to be high."""

    settings_high_varmaxabs = enum16(42, SettingsHighVarmaxabs, writable=True)
    """Settings High Varmaxabs. Set the DER settings VarMaxAbs to be high."""

    change_common_model_id = enum16(43, ChangeCommonModelID, writable=True)
    """Change Common Model ID. Change the common model ID."""

    change_common_model_length = enum16(44, ChangeCommonModelLength, writable=True)
    """Change Common Model Length. Change the common model length."""
