"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_708.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
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


class CurveAccess(IntEnum):
    RW = 0
    R = 1


class DERTripHVModuleEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class AdoptCurveResult(IntEnum):
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2


class DERTripHVCrvRegionPt(Component):
    """One 'Pt' block of SunSpec model 708."""

    v = uint16(11, scale_register=7, writable=True, unit='VNomPct')
    """Voltage Point. Curve voltage point as percentage."""

    tms = uint32(12, scale_register=8, writable=True, unit='Secs')
    """Time Point. Curve time point in seconds."""


class DERTripHVCrvRegion(Component):
    """One 'region' block of SunSpec model 708."""

    act_pt = uint16(10, writable=True)
    """Number Of Active Points. Number of active points in must trip curve."""

    pt = repeating_group(uint16(5), DERTripHVCrvRegionPt, stride=3, count_in_block=False)

    async def write_pt(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'Pt' instances in one request.

        Each mapping sets one instance and must set every field:
        v, tms. Instances past ``values`` are untouched.
        """
        await write_block(self, "pt", values)


class DERTripHVCrv(Component):
    """One 'Crv' block of SunSpec model 708."""

    read_only = enum16(9, CurveAccess)
    """Curve Access. Curve read-write access."""

    region = repeating_group(3, DERTripHVCrvRegion, stride=lambda m: 1 + 3 * m.n_pt)

    @property
    def must_trip(self) -> DERTripHVCrvRegion:
        """The 'MustTrip' block."""
        return self.region[0]

    @property
    def may_trip(self) -> DERTripHVCrvRegion:
        """The 'MayTrip' block."""
        return self.region[1]

    @property
    def mom_cess(self) -> DERTripHVCrvRegion:
        """The 'MomCess' block."""
        return self.region[2]


class DERTripHV(SunSpecComponent):
    """SunSpec model 708: DER Trip HV."""

    ena = enum16(2, DERTripHVModuleEnable, writable=True)
    """DER Trip HV Module Enable. DER high voltage trip control enable."""

    adpt_crv_req = uint16(3, writable=True)
    """Adopt Curve Request. Index of curve points to adopt. First curve index is 1."""

    adpt_crv_rslt = enum16(4, AdoptCurveResult)
    """Adopt Curve Result. Result of last adopt curve operation."""

    n_pt = uint16(5)
    """Number Of Points. Number of curve points supported."""

    n_crv_set = uint16(6)
    """Stored Curve Count. Number of stored curves supported."""

    crv = repeating_group(uint16(6), DERTripHVCrv, stride=lambda m: 4 + 9 * m.n_pt)
