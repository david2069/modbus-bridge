"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_805.json)

from __future__ import annotations

from enum import IntFlag

from modbus_connection.model import Component
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    bitfield32,
    int16,
    model_length_group,
    string,
    uint16,
    uint32,
)


class CellStatus(IntFlag):
    CELL_IS_BALANCING = 1 << 0


class LithiumIonModuleLithiumIonModuleCell(Component):
    """One 'lithium-ion-module-cell' block of SunSpec model 805."""

    cell_v = uint16(44, scale_register=42, unit='V')
    """Cell Voltage. Cell terminal voltage."""

    cell_tmp = int16(45, scale_register=43, unit='C')
    """Cell Temperature."""

    cell_st = bitfield32(46, CellStatus)
    """Cell Status. Status of the cell."""


class LithiumIonModule(SunSpecComponent):
    """SunSpec model 805: Lithium-Ion Module Model."""

    str_idx = uint16(2)
    """String Index. Index of the string containing the module."""

    mod_idx = uint16(3)
    """Module Index. Index of the module within the string."""

    n_cell = uint16(4)
    """Module Cell Count. Count of all cells in the module."""

    so_c = uint16(5, scale_register=38, unit='%')
    """Module SoC. Module state of charge, expressed as a percentage."""

    do_d = uint16(6, scale_register=40, unit='%')
    """Depth of Discharge. Depth of discharge for the module."""

    so_h = uint16(7, scale_register=39, unit='%')
    """Module SoH. Module state of health, expressed as a percentage."""

    n_cyc = uint32(8)
    """Cycle Count. Count of cycles executed."""

    v = uint16(10, scale_register=41, unit='V')
    """Module Voltage. Voltage of the module."""

    cell_v_max = uint16(11, scale_register=42, unit='V')
    """Max Cell Voltage. Maximum voltage for all cells in the module."""

    cell_v_max_cell = uint16(12)
    """Max Cell Voltage Cell. Cell with the maximum voltage."""

    cell_v_min = uint16(13, scale_register=42, unit='V')
    """Min Cell Voltage. Minimum voltage for all cells in the module."""

    cell_v_min_cell = uint16(14)
    """Min Cell Voltage Cell. Cell with the minimum voltage."""

    cell_v_avg = uint16(15, scale_register=42, unit='V')
    """Average Cell Voltage. Average voltage for all cells in the module."""

    cell_tmp_max = int16(16, scale_register=43, unit='C')
    """Max Cell Temperature. Maximum temperature for all cells in the module."""

    cell_tmp_max_cell = uint16(17)
    """Max Cell Temperature Cell. Cell with the maximum cell temperature."""

    cell_tmp_min = int16(18, scale_register=43, unit='C')
    """Min Cell Temperature. Minimum temperature for all cells in the module."""

    cell_tmp_min_cell = uint16(19)
    """Min Cell Temperature Cell. Cell with the minimum cell temperature."""

    cell_tmp_avg = int16(20, scale_register=43, unit='C')
    """Average Cell Temperature. Average temperature for all cells in the module."""

    n_cell_bal = uint16(21)
    """Balanced Cell Count. Number of cells currently being balanced in the module."""

    sn = string(22, 16)
    """Serial Number. Serial number for the module."""

    lithium_ion_module_cell = model_length_group(LithiumIonModuleLithiumIonModuleCell, start=44, stride=4)
