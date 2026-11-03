"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_711.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model import Component, repeating_group
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    int16,
    uint16,
    uint32,
)


class ControlAccess(IntEnum):
    RW = 0
    R = 1


class DERFrequencyDroopModuleEnable(IntEnum):
    DISABLED = 0
    ENABLED = 1


class SetActiveControlResult(IntEnum):
    IN_PROGRESS = 0
    COMPLETED = 1
    FAILED = 2


class DERFreqDroopCtl(Component):
    """One 'Ctl' block of SunSpec model 711."""

    db_of = uint32(14, scale_register=11, writable=True, unit='Hz')
    """Over-Frequency Deadband. The deadband value for over-frequency conditions in
    Hz."""

    db_uf = uint32(16, scale_register=11, writable=True, unit='Hz')
    """Under-Frequency Deadband. The deadband value for under-frequency conditions in
    Hz."""

    k_of = uint16(18, scale_register=12, writable=True)
    """Over-Frequency Change Ratio. Frequency droop per-unit frequency change for
    over-frequency conditions corresponding to 1 per-unit power output change."""

    k_uf = uint16(19, scale_register=12, writable=True)
    """Under-Frequency Change Ratio. Frequency droop per-unit frequency change for
    under-frequency conditions corresponding to 1 per-unit power output change."""

    rsp_tms = uint32(20, scale_register=13, writable=True, unit='Secs')
    """Open-Loop Response Time. The open-loop response time in seconds."""

    p_min = int16(22, writable=True, unit='Pct')
    """Minimum Active Power. The minimum active power output due to DER prime mover
    constraints, in percent of the DER active power rating. The valid range is
    -100 to 100. This setting applies only to the frequency droop control."""

    read_only = enum16(23, ControlAccess)
    """Control Access. Control read-write access."""


class DERFreqDroop(SunSpecComponent):
    """SunSpec model 711: DER Frequency Droop."""

    ena = enum16(2, DERFrequencyDroopModuleEnable, writable=True)
    """DER Frequency Droop Module Enable. DER Frequency-Watt (Frequency-Droop)
    control enable."""

    adpt_ctl_req = uint16(3, writable=True)
    """Set Active Control Request. Set active control. 0 = No active control."""

    adpt_ctl_rslt = enum16(4, SetActiveControlResult)
    """Set Active Control Result. Result of last set active control operation."""

    n_ctl = uint16(5)
    """Stored Control Count. Number of stored controls supported."""

    rvrt_tms = uint32(6, writable=True, unit='Secs')
    """Reversion Timeout. Reversion time in seconds. 0 = No reversion time."""

    rvrt_rem = uint32(8, unit='Secs')
    """Reversion Time Left. Reversion time remaining in seconds."""

    rvrt_ctl = uint16(10, writable=True)
    """Reversion Control. Default control after reversion timeout."""

    ctl = repeating_group(uint16(5), DERFreqDroopCtl, stride=10)
