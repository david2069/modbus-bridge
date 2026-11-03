"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_145.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    uint16,
)


class ExtSettings(SunSpecComponent):
    """SunSpec model 145: Extended Settings."""

    nom_rmp_up_rte = uint16(2, scale_register=9, writable=True, unit='Pct')
    """Ramp Up Rate. Ramp up rate as a percentage of max current."""

    nom_rmp_dn_rte = uint16(3, scale_register=9, writable=True, unit='Pct')
    """NomRmpDnRte. Ramp down rate as a percentage of max current."""

    emg_rmp_up_rte = uint16(4, scale_register=9, writable=True, unit='Pct')
    """Emergency Ramp Up Rate. Emergency ramp up rate as a percentage of max current."""

    emg_rmp_dn_rte = uint16(5, scale_register=9, writable=True, unit='Pct')
    """Emergency Ramp Down Rate. Emergency ramp down rate as a percentage of max
    current."""

    conn_rmp_up_rte = uint16(6, scale_register=9, writable=True, unit='Pct')
    """Connect Ramp Up Rate. Connect ramp up rate as a percentage of max current."""

    conn_rmp_dn_rte = uint16(7, scale_register=9, writable=True, unit='Pct')
    """Connect Ramp Down Rate. Connect ramp down rate as a percentage of max current."""

    a_gra = uint16(8, scale_register=9, writable=True, unit='Pct')
    """Default Ramp Rate. Ramp rate specified in percent of max current."""
