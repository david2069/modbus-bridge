"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64101.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    int16,
    uint16,
)


class Model64101(SunSpecComponent):
    """SunSpec model 64101: Eltek Inverter Extension."""

    eltek_country_code = uint16(2)

    eltek_feeding_phase = uint16(3)

    eltek_apd_method = uint16(4)

    eltek_apd_power_ref = uint16(5)

    eltek_rps_method = uint16(6)

    eltek_rps_q_ref = uint16(7)

    eltek_rps_cos_phi_ref = int16(8)
