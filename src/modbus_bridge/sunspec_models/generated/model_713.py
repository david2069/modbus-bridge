"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_713.json)

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
    uint16,
)


class Status(IntEnum):
    OK = 0
    WARNING = 1
    ERROR = 2


class DERStorageCapacity(SunSpecComponent):
    """SunSpec model 713: DER Storage Capacity."""

    wh_rtg = uint16(2, scale_register=7, unit='WH')
    """Energy Rating. Energy rating of the DER storage."""

    wh_avail = uint16(3, scale_register=7, unit='WH')
    """Energy Available. Energy available of the DER storage (WHAvail = WHRtg * SoC *
    SoH)."""

    so_c = uint16(4, scale_register=8, unit='Pct')
    """State of Charge. State of charge of the DER storage."""

    so_h = uint16(5, scale_register=8, unit='Pct')
    """State of Health. State of health of the DER storage."""

    sta = enum16(6, Status)
    """Status. Storage status."""
