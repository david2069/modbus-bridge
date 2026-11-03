"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_6.json)

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


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class Model6Repeating(Component):
    """One 'repeating' block of SunSpec model 6."""

    ds = uint16(92, writable=True)
    """DS. Digital Signature."""


class Model6(SunSpecComponent):
    """SunSpec model 6: Secure Write Sequential Request."""

    x = uint16(2, writable=True)
    """X. Number of (offset, value) pairs being written."""

    off = uint16(3, writable=True)
    """Offset. Starting offset for write operation."""

    val1 = uint16(4, writable=True)
    """Value1. Value to write to control register at offset."""

    val2 = uint16(5, writable=True)

    val3 = uint16(6, writable=True)

    val4 = uint16(7, writable=True)

    val5 = uint16(8, writable=True)

    val6 = uint16(9, writable=True)

    val7 = uint16(10, writable=True)

    val8 = uint16(11, writable=True)

    val9 = uint16(12, writable=True)

    val10 = uint16(13, writable=True)

    val11 = uint16(14, writable=True)

    val12 = uint16(15, writable=True)

    val13 = uint16(16, writable=True)

    val14 = uint16(17, writable=True)

    val15 = uint16(18, writable=True)

    val16 = uint16(19, writable=True)

    val17 = uint16(20, writable=True)

    val18 = uint16(21, writable=True)

    val19 = uint16(22, writable=True)

    val20 = uint16(23, writable=True)

    val21 = uint16(24, writable=True)

    val22 = uint16(25, writable=True)

    val23 = uint16(26, writable=True)

    val24 = uint16(27, writable=True)

    val25 = uint16(28, writable=True)

    val26 = uint16(29, writable=True)

    val27 = uint16(30, writable=True)

    val28 = uint16(31, writable=True)

    val29 = uint16(32, writable=True)

    val30 = uint16(33, writable=True)

    val31 = uint16(34, writable=True)

    val32 = uint16(35, writable=True)

    val33 = uint16(36, writable=True)

    val34 = uint16(37, writable=True)

    val35 = uint16(38, writable=True)

    val36 = uint16(39, writable=True)

    val37 = uint16(40, writable=True)

    val38 = uint16(41, writable=True)

    val39 = uint16(42, writable=True)

    val40 = uint16(43, writable=True)

    val41 = uint16(44, writable=True)

    val42 = uint16(45, writable=True)

    val43 = uint16(46, writable=True)

    val44 = uint16(47, writable=True)

    val45 = uint16(48, writable=True)

    val46 = uint16(49, writable=True)

    val47 = uint16(50, writable=True)

    val48 = uint16(51, writable=True)

    val49 = uint16(52, writable=True)

    val50 = uint16(53, writable=True)

    val51 = uint16(54, writable=True)

    val52 = uint16(55, writable=True)

    val53 = uint16(56, writable=True)

    val54 = uint16(57, writable=True)

    val55 = uint16(58, writable=True)

    val56 = uint16(59, writable=True)

    val57 = uint16(60, writable=True)

    val58 = uint16(61, writable=True)

    val59 = uint16(62, writable=True)

    val60 = uint16(63, writable=True)

    val61 = uint16(64, writable=True)

    val62 = uint16(65, writable=True)

    val63 = uint16(66, writable=True)

    val64 = uint16(67, writable=True)

    val65 = uint16(68, writable=True)

    val66 = uint16(69, writable=True)

    val67 = uint16(70, writable=True)

    val68 = uint16(71, writable=True)

    val69 = uint16(72, writable=True)

    val70 = uint16(73, writable=True)

    val71 = uint16(74, writable=True)

    val72 = uint16(75, writable=True)

    val73 = uint16(76, writable=True)

    val74 = uint16(77, writable=True)

    val75 = uint16(78, writable=True)

    val76 = uint16(79, writable=True)

    val77 = uint16(80, writable=True)

    val78 = uint16(81, writable=True)

    val79 = uint16(82, writable=True)

    val80 = uint16(83, writable=True)

    ts = uint32(84, writable=True)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(86, writable=True)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(87, writable=True)
    """Sequence. Sequence number of request."""

    role = uint16(88, writable=True)
    """Role. Signing key used 0-5."""

    alg = enum16(90, Algorithm, writable=True)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(91, writable=True)
    """N. Number of registers comprising the digital signature."""

    repeating = model_length_group(Model6Repeating, start=92, stride=1)

    async def write_repeating(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'repeating' instances in one request.

        Each mapping sets one instance and must set every field:
        ds. Instances past ``values`` are untouched.
        """
        await write_block(self, "repeating", values)
