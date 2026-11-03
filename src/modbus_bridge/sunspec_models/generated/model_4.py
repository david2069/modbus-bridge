"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_4.json)

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


class Status(IntEnum):
    SUCCESS = 0
    DS = 1
    ACL = 2
    OFF = 3


class Alarm(IntEnum):
    NONE = 0
    ALM = 1


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class Model4Repeating(Component):
    """One 'repeating' block of SunSpec model 4."""

    ds = uint16(62)
    """DS. Digital Signature."""


class Model4(SunSpecComponent):
    """SunSpec model 4: Secure Dataset Read Response."""

    rq_seq = uint16(2)
    """Request Sequence. Sequence number from the request."""

    sts = enum16(3, Status)
    """Status. Status of last read operation."""

    x = uint16(4)
    """X. Number of values from the request."""

    val1 = uint16(5)
    """Value1. Copy of value from register Off1."""

    val2 = uint16(6)

    val3 = uint16(7)

    val4 = uint16(8)

    val5 = uint16(9)

    val6 = uint16(10)

    val7 = uint16(11)

    val8 = uint16(12)

    val9 = uint16(13)

    val10 = uint16(14)

    val11 = uint16(15)

    val12 = uint16(16)

    val13 = uint16(17)

    val14 = uint16(18)

    val15 = uint16(19)

    val16 = uint16(20)

    val17 = uint16(21)

    val18 = uint16(22)

    val19 = uint16(23)

    val20 = uint16(24)

    val21 = uint16(25)

    val22 = uint16(26)

    val23 = uint16(27)

    val24 = uint16(28)

    val25 = uint16(29)

    val26 = uint16(30)

    val27 = uint16(31)

    val28 = uint16(32)

    val29 = uint16(33)

    val30 = uint16(34)

    val31 = uint16(35)

    val32 = uint16(36)

    val33 = uint16(37)

    val34 = uint16(38)

    val35 = uint16(39)

    val36 = uint16(40)

    val37 = uint16(41)

    val38 = uint16(42)

    val39 = uint16(43)

    val40 = uint16(44)

    val41 = uint16(45)

    val42 = uint16(46)

    val43 = uint16(47)

    val44 = uint16(48)

    val45 = uint16(49)

    val46 = uint16(50)

    val47 = uint16(51)

    val48 = uint16(52)

    val49 = uint16(53)

    val50 = uint16(54)

    ts = uint32(55)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(57)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(58)
    """Sequence. Sequence number of response."""

    alm = enum16(59, Alarm)
    """Alarm. Bitmask alarm code."""

    alg = enum16(60, Algorithm)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(61)
    """N. Number of registers comprising the digital signature."""

    repeating = model_length_group(Model4Repeating, start=62, stride=1)
