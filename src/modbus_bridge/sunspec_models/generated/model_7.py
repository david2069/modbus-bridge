"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_7.json)

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import IntEnum
from typing import Any

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    model_length_group,
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


class Status(IntEnum):
    SUCCESS = 0
    DS = 1
    ACL = 2
    OFF = 3
    VAL = 4


class Alarm(IntEnum):
    NONE = 0
    ALM = 1


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class Model7Repeating(Component):
    """One 'repeating' block of SunSpec model 7."""

    ds = uint16(12, writable=True)
    """DS. Digital Signature."""


class Model7(SunSpecComponent):
    """SunSpec model 7: Secure Write Response Model (DRAFT 1)."""

    rq_seq = uint16(2)
    """Request Sequence. Sequence number from the request."""

    sts = enum16(3, Status)
    """Status. Status of last write operation."""

    ts = uint32(4)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(6)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(7)
    """Sequence. Sequence number of response."""

    alm = enum16(8, Alarm)
    """Alarm. Bitmask alarm code."""

    alg = enum16(10, Algorithm)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(11, writable=True)
    """N. Number of registers comprising the digital signature."""

    repeating = model_length_group(Model7Repeating, start=12, stride=1)

    async def write_repeating(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'repeating' instances in one request.

        Each mapping sets one instance and must set every field:
        ds. Instances past ``values`` are untouched.
        """
        await write_block(self, "repeating", values)
