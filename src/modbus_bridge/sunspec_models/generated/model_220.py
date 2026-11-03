"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_220.json)

from __future__ import annotations

from enum import IntEnum, IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    bitfield32,
    enum16,
    int16,
    model_length_group,
    uint16,
    uint32,
)


class Events(IntFlag):
    Power_Failure = 1 << 2
    Under_Voltage = 1 << 3
    Low_PF = 1 << 4
    Over_Current = 1 << 5
    Over_Voltage = 1 << 6
    Missing_Sensor = 1 << 7
    OEM01 = 1 << 16
    OEM02 = 1 << 17
    OEM03 = 1 << 18
    OEM04 = 1 << 19
    OEM05 = 1 << 20
    OEM06 = 1 << 21
    OEM07 = 1 << 22
    OEM08 = 1 << 23
    OEM09 = 1 << 24
    OEM10 = 1 << 25
    OEM11 = 1 << 26
    OEM12 = 1 << 27
    OEM13 = 1 << 28
    OEM14 = 1 << 29
    OEM15 = 1 << 30


class Algorithm(IntEnum):
    NONE = 0
    AES_GMAC_64 = 1
    ECC_256 = 2


class AcMeterSecureRepeating(Component):
    """One 'repeating' block of SunSpec model 220."""

    ds = uint16(44)


class AcMeterSecure(SunSpecComponent):
    """SunSpec model 220: Secure AC Meter Selected Readings."""

    a = int16(2, scale_register=3, unit='A')
    """Amps. Total AC Current."""

    ph_v = int16(4, scale_register=5, unit='V')
    """Voltage. Average phase or line voltage."""

    hz = int16(6, scale_register=7, unit='Hz')
    """Hz. Frequency."""

    w = int16(8, scale_register=9, unit='W')
    """Watts. Total Real Power."""

    va = int16(10, scale_register=11, unit='VA')
    """VA. AC Apparent Power."""

    var = int16(12, scale_register=13, unit='var')
    """VAR. Reactive Power."""

    pf = int16(14, scale_register=15, unit='Pct')
    """PF. Power Factor."""

    tot_wh_exp = acc32(16, scale_register=20, unit='Wh')
    """Total Watt-hours Exported. Total Real Energy Exported."""

    tot_wh_imp = acc32(18, scale_register=20, unit='Wh')
    """Total Watt-hours Imported. Total Real Energy Imported."""

    tot_v_ah_exp = acc32(21, scale_register=25, unit='VAh')
    """Total VA-hours Exported. Total Apparent Energy Exported."""

    tot_v_ah_imp = acc32(23, scale_register=25, unit='VAh')
    """Total VA-hours Imported. Total Apparent Energy Imported."""

    tot_v_arh_imp_q1 = acc32(26, scale_register=34, unit='varh')
    """Total VAR-hours Imported Q1. Total Reactive Energy Imported Quadrant 1."""

    tot_v_arh_imp_q2 = acc32(28, scale_register=34, unit='varh')
    """Total VAr-hours Imported Q2. Total Reactive Power Imported Quadrant 2."""

    tot_v_arh_exp_q3 = acc32(30, scale_register=34, unit='varh')
    """Total VAr-hours Exported Q3. Total Reactive Power Exported Quadrant 3."""

    tot_v_arh_exp_q4 = acc32(32, scale_register=34, unit='varh')
    """Total VAr-hours Exported Q4. Total Reactive Power Exported Quadrant 4."""

    evt = bitfield32(35, Events)
    """Events. Meter Event Flags."""

    ts = uint32(38)
    """Timestamp. Timestamp value is the number of seconds since January 1, 2000."""

    ms = uint16(40)
    """Milliseconds. Millisecond counter 0-999."""

    seq = uint16(41)
    """Sequence. Sequence number of request."""

    alg = enum16(42, Algorithm)
    """Algorithm. Algorithm used to compute the digital signature."""

    n = uint16(43)
    """N. Number of registers comprising the digital signature."""

    repeating = model_length_group(AcMeterSecureRepeating, start=44, stride=1)
