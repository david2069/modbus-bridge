"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_3.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    model_length_group,
    uint16,
    uint32,
)


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class Model3Repeating(Component):
    """One 'repeating' block of SunSpec model 3."""

    ds = uint16(60)
    """DS. Digital Signature."""


class Model3(SunSpecComponent):
    """SunSpec model 3: Secure Dataset Read Request."""

    x = uint16(2, writable=True)
    """X. Number of registers being requested."""

    off1 = uint16(3, writable=True)
    """Offset1. Offset of value to read."""

    off2 = uint16(4, writable=True)

    off3 = uint16(5, writable=True)

    off4 = uint16(6, writable=True)

    off5 = uint16(7, writable=True)

    off6 = uint16(8, writable=True)

    off7 = uint16(9, writable=True)

    off8 = uint16(10, writable=True)

    off9 = uint16(11, writable=True)

    off10 = uint16(12, writable=True)

    off11 = uint16(13, writable=True)

    off12 = uint16(14, writable=True)

    off13 = uint16(15, writable=True)

    off14 = uint16(16, writable=True)

    off15 = uint16(17, writable=True)

    off16 = uint16(18, writable=True)

    off17 = uint16(19, writable=True)

    off18 = uint16(20, writable=True)

    off19 = uint16(21, writable=True)

    off20 = uint16(22, writable=True)

    off21 = uint16(23, writable=True)

    off22 = uint16(24, writable=True)

    off23 = uint16(25, writable=True)

    off24 = uint16(26, writable=True)

    off25 = uint16(27, writable=True)

    off26 = uint16(28, writable=True)

    off27 = uint16(29, writable=True)

    off28 = uint16(30, writable=True)

    off29 = uint16(31, writable=True)

    off30 = uint16(32, writable=True)

    off31 = uint16(33, writable=True)

    off32 = uint16(34, writable=True)

    off33 = uint16(35, writable=True)

    off34 = uint16(36, writable=True)

    off35 = uint16(37, writable=True)

    off36 = uint16(38, writable=True)

    off37 = uint16(39, writable=True)

    off38 = uint16(40, writable=True)

    off39 = uint16(41, writable=True)

    off40 = uint16(42, writable=True)

    off41 = uint16(43, writable=True)

    off42 = uint16(44, writable=True)

    off43 = uint16(45, writable=True)

    off44 = uint16(46, writable=True)

    off45 = uint16(47, writable=True)

    off46 = uint16(48, writable=True)

    off47 = uint16(49, writable=True)

    off48 = uint16(50, writable=True)

    off49 = uint16(51, writable=True)

    off50 = uint16(52, writable=True)

    ts = uint32(53, writable=True)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(55, writable=True)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(56, writable=True)
    """Sequence. Sequence number of request."""

    role = uint16(57, writable=True)
    """Role. Digital Signature ID."""

    alg = enum16(58, Algorithm)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(59)
    """N. Number of registers comprising the digital signature."""

    repeating = model_length_group(Model3Repeating, start=60, stride=1)
