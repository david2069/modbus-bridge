"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64410.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum, IntFlag
from typing import Any

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    enum16,
    int32,
    string,
    uint16,
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


class DependentReferences(IntFlag):
    VOLTAGE = 1 << 0
    POWER = 1 << 1
    CURRENT = 1 << 2
    IRRADIANCE = 1 << 3


class CVOrCCMode(IntEnum):
    CV = 0
    CC = 1


class PowerOnOff(IntEnum):
    ON = 1
    OFF = 0


class ResetDevice(IntEnum):
    RESET = 1
    DO_NOT_RESET = 0


class EN50530Mode(IntEnum):
    EN50530 = 1
    DO_NOT_EN50530 = 0


class EnableProfile(IntEnum):
    START = 1
    STOP = 0


class AdoptProfileResult(IntEnum):
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2


class DCSimInterfaceProfPt(Component):
    """One 'Pt' block of SunSpec model 64410."""

    tms = uint16(73, scale_register=65, writable=True, unit='Sec')
    """Profile Time."""

    v = uint16(74, scale_register=62, writable=True, unit='V')
    """Voltage Point. Profile voltage point in Volts."""

    p = uint16(75, scale_register=61, writable=True, unit='W')
    """Power Point. Profile power point in Watts."""

    i = uint16(76, scale_register=63, writable=True, unit='A')
    """Current Point. Profile current point in Amps."""

    g = uint16(77, scale_register=69, writable=True, unit='Pct')
    """Irradiance Point. Profile irradiance point as percentage."""


class DCSimInterfaceProf(Component):
    """One 'Prof' block of SunSpec model 64410."""

    act_pt = uint16(70, writable=True)
    """Active Points. Number of active points."""

    dept_ref = bitfield32(71, DependentReferences, writable=True)
    """Dependent References. Profile references."""

    pt = repeating_group(uint16(59), DCSimInterfaceProfPt, stride=5, count_in_block=False)

    async def write_pt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'Pt' instances in one request.

        Each mapping sets one instance and must set every field:
        tms, v, p, i, g. Instances past ``values`` are untouched.
        """
        await write_block(self, "pt", values)


class DCSimInterface(SunSpecComponent):
    """SunSpec model 64410: DC Simulator Control Interface."""

    v_max_lim = uint16(2, scale_register=62, writable=True, unit='V')
    """Maximum Voltage. Upper Voltage Protection Limit."""

    p_max_lim = uint16(3, scale_register=61, writable=True, unit='W')
    """Maximum Power. Upper Power Protection Limit."""

    i_max_lim = uint16(4, scale_register=63, writable=True, unit='A')
    """Maximum Current. Upper Current Protection Limit."""

    mode = enum16(5, CVOrCCMode, writable=True)
    """CV or CC Mode. Constant Voltage (CV) or Constant Current (CC) Mode."""

    ena = enum16(6, PowerOnOff, writable=True)
    """Power On/Off."""

    reset = enum16(7, ResetDevice, writable=True)
    """Reset Device."""

    v_set = uint16(8, scale_register=62, writable=True, unit='V')
    """Voltage Setpoint."""

    p_set = uint16(9, scale_register=61, writable=True, unit='W')
    """Power Setpoint."""

    i_set = uint16(10, scale_register=63, writable=True, unit='A')
    """Current Setpoint."""

    en50530 = enum16(11, EN50530Mode, writable=True)
    """EN50530 Mode. EN50530 Mode - Enable or disable EN50530 profile mode."""

    vmpp = uint16(12, scale_register=62, writable=True, unit='V')
    """EN50530 MPP Voltage."""

    pmpp = uint16(13, scale_register=61, writable=True, unit='W')
    """EN50530 MPP Power."""

    g_set = uint16(14, scale_register=64, writable=True, unit='W/m^2')
    """Irradiance Setpoint."""

    v_slew_rate = uint16(15, scale_register=66, writable=True, unit='V/s')
    """Voltage Slew Rate."""

    p_slew_rate = uint16(16, scale_register=67, writable=True, unit='W/s')
    """Power Slew Rate."""

    i_slew_rate = uint16(17, scale_register=68, writable=True, unit='A/s')
    """Current Slew Rate."""

    ena_prof = enum16(18, EnableProfile, writable=True)
    """Enable Profile. Start/Stop the Profile."""

    adpt_prof_req = uint16(19, writable=True)
    """Profile Adoption Request. Index of profile points to adopt. First curve index
    is 1."""

    adpt_prof_rslt = enum16(20, AdoptProfileResult)
    """Adopt Profile Result. Result of last adopt profile operation."""

    v = int32(21)
    """Measured Voltage."""

    p = int32(23)
    """Measured Power."""

    i = int32(25)
    """Measured Current."""

    errors = string(27, 32)
    """Errors. Error States."""

    n_pt = uint16(59)
    """Number Of Points. Number of profile points supported."""

    n_prof = uint16(60)
    """Stored Profile Count. Number of stored profiles supported."""

    prof = repeating_group(uint16(60), DCSimInterfaceProf, stride=lambda m: 3 + 5 * m.n_pt)
