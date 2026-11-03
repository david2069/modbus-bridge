"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_64414.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    float32,
    string,
)


class DERSimControls(SunSpecComponent):
    """SunSpec model 64414: DER Simulation Controls."""

    time = string(2, 10)
    """Time offset. Time offset for simulation formatted 'HH:MM:SS'."""

    temperature = float32(12, writable=True)
    """Ambient temperature (degrees Celsius)."""

    grid_model_source = string(14, 32, writable=True)
    """The data source for the grid model. 'csv' or 'const'."""

    irradiance_model_source = string(46, 32, writable=True)
    """The data source for the irradiance model. 'csv' or 'const'."""

    irradiance = float32(78, writable=True)
    """The irradiance on the DER device (W/m^2) for the 'const' irradiance model."""

    grid_voltage_a = float32(80, writable=True)
    """Phase A RMS Voltage (pu) for the 'const' grid model."""

    grid_voltage_b = float32(82, writable=True)
    """Phase B RMS Voltage (pu) for the 'const' grid model."""

    grid_voltage_c = float32(84, writable=True)
    """Phase C RMS Voltage (pu) for the 'const' grid model."""

    grid_frequency = float32(86, writable=True)
    """Grid frequency (Hz) for the 'const' grid model."""
