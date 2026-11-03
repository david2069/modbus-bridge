"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_305.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int32,
    string,
)


class Location(SunSpecComponent):
    """SunSpec model 305: GPS."""

    tm = string(2, 6)
    """Tm. UTC 24 hour time stamp to millisecond hhmmss.sssZ format."""

    date = string(8, 4)
    """Date. UTC Date string YYYYMMDD format."""

    loc = string(12, 20)
    """Location. Location string (40 chars max)."""

    lat = int32(32, scale=1e-07, unit='Degrees')
    """Lat. Latitude with seven degrees of precision."""

    long = int32(34, scale=1e-07, unit='Degrees')
    """Long. Longitude with seven degrees of precision."""

    alt = int32(36, unit='meters')
    """Altitude. Altitude measurement in meters."""
