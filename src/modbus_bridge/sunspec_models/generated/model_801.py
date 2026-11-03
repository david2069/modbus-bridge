"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_801.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    enum16,
)


class Storage(SunSpecComponent):
    """SunSpec model 801: Energy Storage Base Model (DEPRECATED)."""

    deprecated = enum16(2)
    """Deprecated Model. This model has been deprecated."""
