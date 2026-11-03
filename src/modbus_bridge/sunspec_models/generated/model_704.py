"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_704.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
    int32,
    uint16,
    uint32,
)


async def write_block(
    component: Component, group: str, values: Sequence[Mapping[str, Any]]
) -> None:
    """Write the leading instances of a repeated block in one request.

    ``values`` holds one mapping per instance, keyed by that instance's field
    names, and has to set every field of each instance it covers: the write
    puts a whole run of registers on the wire, so a field left out would be
    written with a value nobody chose. Instances past ``values`` are untouched.

    Each scale register is read once for the whole block rather than once per
    field, so a four-point curve costs one write and two reads instead of
    eight of each.
    """
    instances = getattr(component, group)
    if len(values) > len(instances):
        raise IndexError(
            f"{group!r} has {len(instances)} instance(s),"
            f" got {len(values)} set(s) of values"
        )
    targets = [
        (resolved, mapping[name])
        for instance, mapping in zip(instances, values, strict=False)
        for name, resolved in instance.resolved_fields.items()
    ]
    targets.sort(key=lambda target: target[0].address)

    unit = component.modbus_unit
    exponents: dict[int, int] = {}
    for resolved, _value in targets:
        address = resolved.scale_address
        if address is not None and address not in exponents:
            (word,) = await unit.read_holding_registers(address, 1)
            exponents[address] = word - 0x10000 if word & 0x8000 else word

    words: list[int] = []
    for resolved, value in targets:
        address = resolved.scale_address
        words += resolved.field.encode(
            value, None if address is None else exponents[address]
        )
    await unit.write_registers(targets[0][0].address, words)


class PowerFactorExcitationWInj(IntEnum):
    OVER_EXCITED = 0
    UNDER_EXCITED = 1


class ReversionPFExcitationWInj(IntEnum):
    OVER_EXCITED = 0
    UNDER_EXCITED = 1


class PowerFactorExcitationWAbs(IntEnum):
    OVER_EXCITED = 0
    UNDER_EXCITED = 1


class ReversionPFExcitationWAbs(IntEnum):
    OVER_EXCITED = 0
    UNDER_EXCITED = 1


class PowerFactorEnableWInjEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class PowerFactorReversionEnableWInj(IntEnum):
    DISABLED = 0
    ENABLED = 1


class PowerFactorEnableWAbsEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class PowerFactorReversionEnableWAbs(IntEnum):
    DISABLED = 0
    ENABLED = 1


class LimitMaxPowerPctEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class ReversionLimitMaxPowerPctEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SetActivePowerEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SetActivePowerMode(IntEnum):
    W_MAX_PCT = 0
    WATTS = 1


class ReversionActivePowerEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SetReactivePowerEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SetReactivePowerMode(IntEnum):
    W_MAX_PCT = 0
    VAR_MAX_PCT = 1
    VAR_AVAIL_PCT = 2
    VA_MAX_PCT = 3
    VARS = 4


class ReactivePowerPriority(IntEnum):
    ACTIVE = 0
    REACTIVE = 1
    VENDOR = 2


class ReversionReactivePowerEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class NormalRampRateReference(IntEnum):
    A_MAX = 0
    W_MAX = 1


class AntiIslandingEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class DERCtlACPFWInj(Component):
    """One 'PFWInj' block of SunSpec model 704."""

    pf = uint16(59, scale_register=53, writable=True)
    """Power Factor (W Inj). Power factor setpoint when injecting active power."""

    ext = enum16(60, PowerFactorExcitationWInj, writable=True)
    """Power Factor Excitation (W Inj). Power factor excitation setpoint when
    injecting active power."""


class DERCtlACPFWInjRvrt(Component):
    """One 'PFWInjRvrt' block of SunSpec model 704."""

    pf = uint16(61, scale_register=53, writable=True)
    """Reversion Power Factor (W Inj). Reversion power factor setpoint when injecting
    active power."""

    ext = enum16(62, ReversionPFExcitationWInj, writable=True)
    """Reversion PF Excitation (W Inj). Reversion power factor excitation setpoint
    when injecting active power."""


class DERCtlACPFWAbs(Component):
    """One 'PFWAbs' block of SunSpec model 704."""

    pf = uint16(63, scale_register=53, writable=True)
    """Power Factor (W Abs). Power factor setpoint when absorbing active power."""

    ext = enum16(64, PowerFactorExcitationWAbs, writable=True)
    """Power Factor Excitation (W Abs). Power factor excitation setpoint when
    absorbing active power."""


class DERCtlACPFWAbsRvrt(Component):
    """One 'PFWAbsRvrt' block of SunSpec model 704."""

    pf = uint16(65, scale_register=53, writable=True)
    """Reversion Power Factor (W Abs). Reversion power factor setpoint when absorbing
    active power."""

    ext = enum16(66, ReversionPFExcitationWAbs, writable=True)
    """Reversion PF Excitation (W Abs). Reversion power factor excitation setpoint
    when absorbing active power."""


class DERCtlAC(SunSpecComponent):
    """SunSpec model 704: DER AC Controls."""

    pfw_inj_ena = enum16(2, PowerFactorEnableWInjEnable, writable=True)
    """Power Factor Enable (W Inj) Enable. Power factor enable when injecting active
    power."""

    pfw_inj_ena_rvrt = enum16(3, PowerFactorReversionEnableWInj, writable=True)
    """Power Factor Reversion Enable (W Inj). Power factor reversion timer when
    injecting active power enable."""

    pfw_inj_rvrt_tms = uint32(4, writable=True, unit='Secs')
    """PF Reversion Time (W Inj). Power factor reversion timer when injecting active
    power."""

    pfw_inj_rvrt_rem = uint32(6, unit='Secs')
    """PF Reversion Time Rem (W Inj). Power factor reversion time remaining when
    injecting active power."""

    pfw_abs_ena = enum16(8, PowerFactorEnableWAbsEnable, writable=True)
    """Power Factor Enable (W Abs) Enable. Power factor enable when absorbing active
    power."""

    pfw_abs_ena_rvrt = enum16(9, PowerFactorReversionEnableWAbs, writable=True)
    """Power Factor Reversion Enable (W Abs). Power factor reversion timer when
    absorbing active power enable."""

    pfw_abs_rvrt_tms = uint32(10, writable=True, unit='Secs')
    """PF Reversion Time (W Abs). Power factor reversion timer when absorbing active
    power."""

    pfw_abs_rvrt_rem = uint32(12, unit='Secs')
    """PF Reversion Time Rem (W Abs). Power factor reversion time remaining when
    absorbing active power."""

    w_max_lim_pct_ena = enum16(14, LimitMaxPowerPctEnable, writable=True)
    """Limit Max Power Pct Enable. Limit maximum active power percent enable."""

    w_max_lim_pct = uint16(15, scale_register=54, writable=True, unit='Pct')
    """Limit Max Power Pct Setpoint. Limit maximum active power percent value."""

    w_max_lim_pct_rvrt = uint16(16, scale_register=54, writable=True, unit='Pct')
    """Reversion Limit Max Power Pct. Reversion limit maximum active power percent
    value."""

    w_max_lim_pct_ena_rvrt = enum16(17, ReversionLimitMaxPowerPctEnable, writable=True)
    """Reversion Limit Max Power Pct Enable. Reversion limit maximum active power
    percent value enable."""

    w_max_lim_pct_rvrt_tms = uint32(18, writable=True, unit='Secs')
    """Limit Max Power Pct Reversion Time. Limit maximum active power percent
    reversion time."""

    w_max_lim_pct_rvrt_rem = uint32(20, unit='Secs')
    """Limit Max Power Pct Rev Time Rem. Limit maximum active power percent reversion
    time remaining."""

    w_set_ena = enum16(22, SetActivePowerEnable, writable=True)
    """Set Active Power Enable."""

    w_set_mod = enum16(23, SetActivePowerMode, writable=True)
    """Set Active Power Mode."""

    w_set = int32(24, scale_register=55, writable=True, unit='W')
    """Active Power Setpoint (W). Active power setting value in watts."""

    w_set_rvrt = int32(26, scale_register=55, writable=True, unit='W')
    """Reversion Active Power (W). Reversion active power setting value in watts."""

    w_set_pct = int16(28, scale_register=56, writable=True, unit='Pct')
    """Active Power Setpoint (Pct). Active power setting value as percent."""

    w_set_pct_rvrt = int16(29, scale_register=56, writable=True, unit='Pct')
    """Reversion Active Power (Pct). Reversion active power setting value as percent."""

    w_set_ena_rvrt = enum16(30, ReversionActivePowerEnable, writable=True)
    """Reversion Active Power Enable. Reversion active power function enable."""

    w_set_rvrt_tms = uint32(31, writable=True, unit='Secs')
    """Active Power Reversion Time. Set active power reversion time."""

    w_set_rvrt_rem = uint32(33, unit='Secs')
    """Active Power Rev Time Rem. Set active power reversion time remaining."""

    var_set_ena = enum16(35, SetReactivePowerEnable, writable=True)
    """Set Reactive Power Enable."""

    var_set_mod = enum16(36, SetReactivePowerMode, writable=True)
    """Set Reactive Power Mode."""

    var_set_pri = enum16(37, ReactivePowerPriority, writable=True)
    """Reactive Power Priority."""

    var_set = int32(38, scale_register=57, writable=True, unit='Var')
    """Reactive Power Setpoint (Vars). Reactive power setting value in vars."""

    var_set_rvrt = int32(40, scale_register=57, writable=True, unit='Var')
    """Reversion Reactive Power (Vars). Reversion reactive power setting value in
    vars."""

    var_set_pct = int16(42, scale_register=58, writable=True, unit='Pct')
    """Reactive Power Setpoint (Pct). Reactive power setting value as percent."""

    var_set_pct_rvrt = int16(43, scale_register=58, writable=True, unit='Pct')
    """Reversion Reactive Power (Pct). Reversion reactive power setting value as
    percent."""

    var_set_ena_rvrt = enum16(44, ReversionReactivePowerEnable, writable=True)
    """Reversion Reactive Power Enable. Reversion reactive power function enable."""

    var_set_rvrt_tms = uint32(45, writable=True, unit='Secs')
    """Reactive Power Reversion Time. Set reactive power reversion time."""

    var_set_rvrt_rem = uint32(47, unit='Secs')
    """Reactive Power Rev Time Rem. Set reactive power reversion time remaining."""

    w_rmp = uint16(49, writable=True, unit='%Max/Sec')
    """Normal Ramp Rate. Ramp rate for increases in active power during normal
    generation."""

    w_rmp_ref = enum16(50, NormalRampRateReference, writable=True)
    """Normal Ramp Rate Reference. Ramp rate reference unit for increases in active
    power or current during normal generation."""

    var_rmp = uint16(51, writable=True, unit='%Max/Sec')
    """Reactive Power Ramp Rate. Ramp rate based on max reactive power per second."""

    anti_isl_ena = enum16(52, AntiIslandingEnable, writable=True)
    """Anti-Islanding Enable."""

    pfw_inj = repeating_group(1, DERCtlACPFWInj, stride=2)

    async def write_pfw_inj(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'PFWInj' instances in one request.

        Each mapping sets one instance and must set every field:
        pf, ext. Instances past ``values`` are untouched.
        """
        await write_block(self, "pfw_inj", values)

    pfw_inj_rvrt = repeating_group(1, DERCtlACPFWInjRvrt, stride=2)

    async def write_pfw_inj_rvrt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'PFWInjRvrt' instances in one request.

        Each mapping sets one instance and must set every field:
        pf, ext. Instances past ``values`` are untouched.
        """
        await write_block(self, "pfw_inj_rvrt", values)

    pfw_abs = repeating_group(1, DERCtlACPFWAbs, stride=2)

    async def write_pfw_abs(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'PFWAbs' instances in one request.

        Each mapping sets one instance and must set every field:
        pf, ext. Instances past ``values`` are untouched.
        """
        await write_block(self, "pfw_abs", values)

    pfw_abs_rvrt = repeating_group(1, DERCtlACPFWAbsRvrt, stride=2)

    async def write_pfw_abs_rvrt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'PFWAbsRvrt' instances in one request.

        Each mapping sets one instance and must set every field:
        pf, ext. Instances past ``values`` are untouched.
        """
        await write_block(self, "pfw_abs_rvrt", values)
