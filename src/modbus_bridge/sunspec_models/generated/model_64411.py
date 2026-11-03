"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64411.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
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


class OutputState(IntEnum):
    OFF = 0
    ON = 1


class RelayState(IntEnum):
    OPEN = 0
    CLOSED = 1


class RegenerationState(IntEnum):
    OFF = 0
    ON = 1


class EnableProfile(IntEnum):
    STOP = 0
    START = 1
    TRIGGER = 2


class ProfileResult(IntEnum):
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2


class ACSimInterfaceProfPt(Component):
    """One 'Pt' block of SunSpec model 64411."""

    tms = uint16(1431, scale_register=1393, writable=True, unit='Sec')
    """Profile Time."""

    va = uint16(1432, scale_register=1391, writable=True, unit='V')
    """Voltage Point. Profile voltage phase A point in Volts."""

    vb = uint16(1433, scale_register=1391, writable=True, unit='V')
    """Voltage Point Phase B. Profile voltage phase B point in Volts."""

    vc = uint16(1434, scale_register=1391, writable=True, unit='V')
    """Voltage Point Phase C. Profile voltage phase C point in Volts."""

    hz = uint16(1435, scale_register=1394, writable=True, unit='Hz')
    """Frequency Point. Profile frequency point in Hz."""

    phase_angle_a = uint16(1436, writable=True, unit='Degrees')
    """Phase Angle A. Profile phase A angle in degrees."""

    phase_angle_b = uint16(1437, writable=True, unit='Degrees')
    """Phase Angle B. Profile phase B angle in degrees."""

    phase_angle_c = uint16(1438, writable=True, unit='Degrees')
    """Phase Angle C. Profile phase C angle in degrees."""


class ACSimInterfaceProf(Component):
    """One 'Prof' block of SunSpec model 64411."""

    name = string(1398, 32, writable=True)
    """Profile Name."""

    act_pt = uint16(1430, writable=True)
    """Active Points. Number of active points."""

    pt = repeating_group(uint16(1390), ACSimInterfaceProfPt, stride=8, count_in_block=False)

    async def write_pt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'Pt' instances in one request.

        Each mapping sets one instance and must set every field:
        tms, va, vb, vc, hz, phase_angle_a, phase_angle_b, phase_angle_c. Instances past ``values`` are untouched.
        """
        await write_block(self, "pt", values)


class ACSimInterface(SunSpecComponent):
    """SunSpec model 64411: AC Simulator Control Interface."""

    phases = uint16(2, writable=True)
    """Active Phases. Set the number of active phases for the power supply."""

    phase_angle = uint16(3, writable=True)
    """Phase Angle. Phase angle (deg) between phases. 0 for signle phase, 120 for two
    phase, 120 for three phase."""

    v_nom = uint16(4, scale_register=1391, writable=True, unit='V')
    """Nominal Voltage. Nominal L-N Voltage."""

    v_max = uint16(5, scale_register=1391, writable=True, unit='V')
    """Maximum Voltage. Maximum Voltage Protection Level."""

    i_max = uint16(6, scale_register=1392, writable=True, unit='A')
    """Maximum Current. Maximum Current Protection Level."""

    freq = uint16(7, scale_register=1394, writable=True, unit='Hz')
    """Frequency. Frequency Setpoint."""

    output = enum16(8, OutputState, writable=True)
    """Output State. AC Output State."""

    relay = enum16(9, RelayState, writable=True)
    """Relay State. AC Relay State."""

    regen = enum16(10, RegenerationState, writable=True)
    """Regeneration State."""

    v_set = uint16(11, scale_register=1391, writable=True, unit='V')
    """Voltage Setpoint. Voltage Setpoint (all phases)."""

    v_set_a = uint16(12, scale_register=1391, writable=True, unit='V')
    """Voltage Setpoint Phase A."""

    v_set_b = uint16(13, scale_register=1391, writable=True, unit='V')
    """Voltage Setpoint Phase B."""

    v_set_c = uint16(14, scale_register=1391, writable=True, unit='V')
    """Voltage Setpoint Phase C."""

    freq_slew = uint16(15, scale_register=1395, writable=True, unit='Hz/s')
    """Frequency Slew Rate."""

    v_slew = uint16(16, scale_register=1396, writable=True, unit='V/s')
    """Voltage Slew Rate."""

    va = int32(17, scale_register=1391, unit='V')
    """Measured Voltage Phase A."""

    vb = int32(19, scale_register=1391, unit='V')
    """Measured Voltage Phase B."""

    vc = int32(21, scale_register=1391, unit='V')
    """Measured Voltage Phase C."""

    hz = int32(23, scale_register=1394, unit='Hz')
    """Measured Frequency."""

    ia = int32(25, scale_register=1392, unit='A')
    """Measured Current Phase A."""

    ib = int32(27, scale_register=1392, unit='A')
    """Measured Current Phase B."""

    ic = int32(29, scale_register=1392, unit='A')
    """Measured Current Phase C."""

    v_har_a = string(31, 150)
    """Voltage Harmonics Phase A. Voltage Harmonics Pct, Phase A (comma seperated
    string for harmonics 1-50)."""

    v_har_b = string(181, 150)
    """Voltage Harmonics Phase B. Voltage Harmonics Pct, Phase B (comma seperated
    string for harmonics 1-50)."""

    v_har_c = string(331, 150)
    """Voltage Harmonics Phase C. Voltage Harmonics Pct, Phase C (comma seperated
    string for harmonics 1-50)."""

    i_har_a = string(481, 150)
    """Current Harmonics Phase A. Current Harmonics Pct, Phase A (comma seperated
    string for harmonics 1-50)."""

    i_har_b = string(631, 150)
    """Current Harmonics Phase B. Current Harmonics Pct, Phase B (comma seperated
    string for harmonics 1-50)."""

    i_har_c = string(781, 150)
    """Current Harmonics Phase C. Current Harmonics Pct, Phase C (comma seperated
    string for harmonics 1-50)."""

    i_int_har_a = string(931, 150)
    """Current Interharmonics Phase A. Current Interharmonics Pct, Phase A (comma
    seperated string for interharmonics 1-50)."""

    i_int_har_b = string(1081, 150)
    """Current Interharmonics Phase B. Current Interharmonics Pct, Phase B (comma
    seperated string for interharmonics 1-50)."""

    i_int_har_c = string(1231, 150)
    """Current Interharmonics Phase C. Current Interharmonics Pct, Phase C (comma
    seperated string for interharmonics 1-50)."""

    v_thd_a = uint16(1381, scale_register=1397, unit='%')
    """Voltage THD Phase A."""

    v_thd_b = uint16(1382, scale_register=1397, unit='%')
    """Voltage THD Phase B."""

    v_thd_c = uint16(1383, scale_register=1397, unit='%')
    """Voltage THD Phase C."""

    i_thd_a = uint16(1384, scale_register=1397, unit='%')
    """Current THD Phase A."""

    i_thd_b = uint16(1385, scale_register=1397, unit='%')
    """Current THD Phase B."""

    i_thd_c = uint16(1386, scale_register=1397, unit='%')
    """Current THD Phase C."""

    ena_prof = enum16(1387, EnableProfile, writable=True)
    """Enable Profile. Start/Stop the AC Profile."""

    prof_rslt = enum16(1388, ProfileResult)
    """Profile Result. Result of last profile operation."""

    n_prof = uint16(1389)
    """Stored Profile Count. Number of stored profiles supported."""

    n_pt = uint16(1390)
    """Max Profile Point Count. Max profile points in the profiles."""

    prof = repeating_group(uint16(1389), ACSimInterfaceProf, stride=lambda m: 33 + 8 * m.n_pt)
