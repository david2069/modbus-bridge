"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_120.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
    uint16,
)


class DERTyp(IntEnum):
    PV = 4
    PV_STOR = 82


class Nameplate(SunSpecComponent):
    """SunSpec model 120: Nameplate."""

    der_typ = enum16(2, DERTyp)
    """DERTyp. Type of DER device. Default value is 4 to indicate PV device."""

    w_rtg = uint16(3, scale_register=4, unit='W')
    """WRtg. Continuous power output capability of the inverter."""

    va_rtg = uint16(5, scale_register=6, unit='VA')
    """VARtg. Continuous Volt-Ampere capability of the inverter."""

    v_ar_rtg_q1 = int16(7, scale_register=11, unit='var')
    """VArRtgQ1. Continuous VAR capability of the inverter in quadrant 1."""

    v_ar_rtg_q2 = int16(8, scale_register=11, unit='var')
    """VArRtgQ2. Continuous VAR capability of the inverter in quadrant 2."""

    v_ar_rtg_q3 = int16(9, scale_register=11, unit='var')
    """VArRtgQ3. Continuous VAR capability of the inverter in quadrant 3."""

    v_ar_rtg_q4 = int16(10, scale_register=11, unit='var')
    """VArRtgQ4. Continuous VAR capability of the inverter in quadrant 4."""

    a_rtg = uint16(12, scale_register=13, unit='A')
    """ARtg. Maximum RMS AC current level capability of the inverter."""

    pf_rtg_q1 = int16(14, scale_register=18, unit='cos()')
    """PFRtgQ1. Minimum power factor capability of the inverter in quadrant 1."""

    pf_rtg_q2 = int16(15, scale_register=18, unit='cos()')
    """PFRtgQ2. Minimum power factor capability of the inverter in quadrant 2."""

    pf_rtg_q3 = int16(16, scale_register=18, unit='cos()')
    """PFRtgQ3. Minimum power factor capability of the inverter in quadrant 3."""

    pf_rtg_q4 = int16(17, scale_register=18, unit='cos()')
    """PFRtgQ4. Minimum power factor capability of the inverter in quadrant 4."""

    wh_rtg = uint16(19, scale_register=20, unit='Wh')
    """WHRtg. Nominal energy rating of storage device."""

    ahr_rtg = uint16(21, scale_register=22, unit='AH')
    """AhrRtg. The usable capacity of the battery. Maximum charge minus minimum
    charge from a technology capability perspective (Amp-hour capacity rating)."""

    max_cha_rte = uint16(23, scale_register=24, unit='W')
    """MaxChaRte. Maximum rate of energy transfer into the storage device."""

    max_dis_cha_rte = uint16(25, scale_register=26, unit='W')
    """MaxDisChaRte. Maximum rate of energy transfer out of the storage device."""
