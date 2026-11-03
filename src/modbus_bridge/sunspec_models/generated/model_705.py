"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_705.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
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


class DependentReference(IntEnum):
    W_MAX_PCT = 0
    VAR_MAX_PCT = 1
    VAR_AVAL_PCT = 2
    VA_MAX_PCT = 3


class PowerPriority(IntEnum):
    ACTIVE = 0
    REACTIVE = 1
    VENDOR = 2


class AutonomousVrefEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class CurveAccess(IntEnum):
    RW = 0
    R = 1


class DERVoltVarModuleEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class AdoptCurveResult(IntEnum):
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2


class DERVoltVarCrvPt(Component):
    """One 'Pt' block of SunSpec model 705."""

    v = uint16(25, scale_register=12, writable=True, unit='VNomPct')
    """Voltage Point. Curve voltage point as percentage."""

    var = int16(26, scale_register=13, writable=True, unit='DeptRef')
    """Reactive Power Point. Curve reactive power point as set in DeptRef point."""


class DERVoltVarCrv(Component):
    """One 'Crv' block of SunSpec model 705."""

    act_pt = uint16(15, writable=True)
    """Active Points. Number of active points."""

    dept_ref = enum16(16, DependentReference, writable=True)
    """Dependent Reference. Curve dependent reference."""

    pri = enum16(17, PowerPriority, writable=True)
    """Power Priority."""

    v_ref = uint16(18, scale_register=12, writable=True, unit='VNomPct')
    """Vref Adjustment. Vref adjustment as percentage of nominal voltage."""

    v_ref_auto = uint16(19, scale_register=12, unit='VNomPct')
    """Current Autonomous Vref. Autonomous vref value as a percentage of nominal
    voltage."""

    v_ref_auto_ena = enum16(20, AutonomousVrefEnable, writable=True)
    """Autonomous Vref Enable. Enable autonomous vref."""

    v_ref_auto_tms = uint16(21, writable=True, unit='Secs')
    """Auto Vref Time Constant. Autonomous vref time constant."""

    rsp_tms = uint32(22, scale_register=14, writable=True, unit='Secs')
    """Open Loop Response Time."""

    read_only = enum16(24, CurveAccess)
    """Curve Access. Curve read-write access."""

    pt = repeating_group(uint16(5), DERVoltVarCrvPt, stride=2, count_in_block=False)

    async def write_pt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'Pt' instances in one request.

        Each mapping sets one instance and must set every field:
        v, var. Instances past ``values`` are untouched.
        """
        await write_block(self, "pt", values)


class DERVoltVar(SunSpecComponent):
    """SunSpec model 705: DER Volt-Var."""

    ena = enum16(2, DERVoltVarModuleEnable, writable=True)
    """DER Volt-Var Module Enable. Volt-Var control enable."""

    adpt_crv_req = uint16(3, writable=True)
    """Adopt Curve Request. Index of curve points to adopt. First curve index is 1."""

    adpt_crv_rslt = enum16(4, AdoptCurveResult)
    """Adopt Curve Result. Result of last adopt curve operation."""

    n_pt = uint16(5)
    """Number Of Points. Number of curve points supported."""

    n_crv = uint16(6)
    """Stored Curve Count. Number of stored curves supported."""

    rvrt_tms = uint32(7, writable=True, unit='Secs')
    """Reversion Timeout. Reversion time in seconds. 0 = No reversion time."""

    rvrt_rem = uint32(9, unit='Secs')
    """Reversion Time Remaining. Reversion time remaining in seconds."""

    rvrt_crv = uint16(11, writable=True)
    """Reversion Curve. Default curve after reversion timeout."""

    crv = repeating_group(uint16(6), DERVoltVarCrv, stride=lambda m: 10 + 2 * m.n_pt)
