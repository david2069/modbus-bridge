"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_9.json)

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


class Format(IntEnum):
    NONE = 0
    X509_PEM = 1
    X509_DER = 2


class Type(IntEnum):
    DEV_KEY_PAIR = 0
    DEV_SHARED_KEY = 1
    OPERATOR_PUB = 2
    OPERATOR_SHARED = 3
    CA_PUB = 4


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class Model9Repeating(Component):
    """One 'repeating' block of SunSpec model 9."""

    cert = uint16(94, writable=True)


class Model9(SunSpecComponent):
    """SunSpec model 9: Set Operator Security Certificate."""

    cert_uid = uint16(2, writable=True)
    """Cert_UID. User ID for this certificate."""

    cert_role = uint16(3, writable=True)
    """Cert_Role. Role for this certificate."""

    fmt = enum16(4, Format, writable=True)
    """Format. Format of this certificate."""

    typ = enum16(5, Type, writable=True)
    """Type. Type of this certificate."""

    tot_ln = uint16(6, writable=True)
    """Total Length. Total Length of the Certificate."""

    frg_ln = uint16(7, writable=True)
    """Fragment length. Length of this fragment."""

    frg1 = uint16(8, writable=True)
    """Frag1. First word of this fragment."""

    frg2 = uint16(9, writable=True)

    frg3 = uint16(10, writable=True)

    frg4 = uint16(11, writable=True)

    frg5 = uint16(12, writable=True)

    frg6 = uint16(13, writable=True)

    frg7 = uint16(14, writable=True)

    frg8 = uint16(15, writable=True)

    frg9 = uint16(16, writable=True)

    frg10 = uint16(17, writable=True)

    frg11 = uint16(18, writable=True)

    frg12 = uint16(19, writable=True)

    frg13 = uint16(20, writable=True)

    frg14 = uint16(21, writable=True)

    frg15 = uint16(22, writable=True)

    frg16 = uint16(23, writable=True)

    frg17 = uint16(24, writable=True)

    frg18 = uint16(25, writable=True)

    frg19 = uint16(26, writable=True)

    frg20 = uint16(27, writable=True)

    frg21 = uint16(28, writable=True)

    frg22 = uint16(29, writable=True)

    frg23 = uint16(30, writable=True)

    frg24 = uint16(31, writable=True)

    frg25 = uint16(32, writable=True)

    frg26 = uint16(33, writable=True)

    frg27 = uint16(34, writable=True)

    frg28 = uint16(35, writable=True)

    frg29 = uint16(36, writable=True)

    frg30 = uint16(37, writable=True)

    frg31 = uint16(38, writable=True)

    frg32 = uint16(39, writable=True)

    frg33 = uint16(40, writable=True)

    frg34 = uint16(41, writable=True)

    frg35 = uint16(42, writable=True)

    frg36 = uint16(43, writable=True)

    frg37 = uint16(44, writable=True)

    frg38 = uint16(45, writable=True)

    frg39 = uint16(46, writable=True)

    frg40 = uint16(47, writable=True)

    frg41 = uint16(48, writable=True)

    frg42 = uint16(49, writable=True)

    frg43 = uint16(50, writable=True)

    frg44 = uint16(51, writable=True)

    frg45 = uint16(52, writable=True)

    frg46 = uint16(53, writable=True)

    frg47 = uint16(54, writable=True)

    frg48 = uint16(55, writable=True)

    frg49 = uint16(56, writable=True)

    frg50 = uint16(57, writable=True)

    frg51 = uint16(58, writable=True)

    frg52 = uint16(59, writable=True)

    frg53 = uint16(60, writable=True)

    frg54 = uint16(61, writable=True)

    frg55 = uint16(62, writable=True)

    frg56 = uint16(63, writable=True)

    frg57 = uint16(64, writable=True)

    frg58 = uint16(65, writable=True)

    frg59 = uint16(66, writable=True)

    frg60 = uint16(67, writable=True)

    frg61 = uint16(68, writable=True)

    frg62 = uint16(69, writable=True)

    frg63 = uint16(70, writable=True)

    frg64 = uint16(71, writable=True)

    frg65 = uint16(72, writable=True)

    frg66 = uint16(73, writable=True)

    frg67 = uint16(74, writable=True)

    frg68 = uint16(75, writable=True)

    frg69 = uint16(76, writable=True)

    frg70 = uint16(77, writable=True)

    frg71 = uint16(78, writable=True)

    frg72 = uint16(79, writable=True)

    frg73 = uint16(80, writable=True)

    frg74 = uint16(81, writable=True)

    frg75 = uint16(82, writable=True)

    frg78 = uint16(83, writable=True)

    frg79 = uint16(84, writable=True)

    frg80 = uint16(85, writable=True)
    """Frag80. Last word of this fragment."""

    ts = uint32(86, writable=True)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(88, writable=True)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(89, writable=True)
    """Sequence. Sequence number of request."""

    uid = uint16(90, writable=True)
    """UID. User ID for the request signature."""

    role = uint16(91, writable=True)
    """Role. Signing key used 0-5."""

    alg = enum16(92, Algorithm, writable=True)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(93, writable=True)
    """N. Number of registers to follow for the certificate."""

    repeating = model_length_group(Model9Repeating, start=94, stride=1)

    async def write_repeating(self, values: Sequence[Mapping[str, Any]]) -> None:
        """Write consecutive 'repeating' instances in one request.

        Each mapping sets one instance and must set every field:
        cert. Instances past ``values`` are untouched.
        """
        await write_block(self, "repeating", values)
