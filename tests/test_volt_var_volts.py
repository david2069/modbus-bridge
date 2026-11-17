"""Tests for the aGate V10R01B04D00 volt-var voltages in volts (P2 step 23). Values are made up."""

from pathlib import Path

import pytest
from test_quirks import state

import modbus_bridge
from modbus_bridge.mqtt_publisher import sensor_classes
from modbus_bridge.quirks import ActiveQuirks, QuirkSet, load_sets
from modbus_bridge.service import point_json
from modbus_bridge.sunspec import DeviceIdentity

FILE = Path(modbus_bridge.__file__).parent / "quirk_sets" / "franklinwh-v10r01b04d00.json"
QUIRK = "fwh-fw10-q-705-v"
V_POINTS = [f"705.Crv[{c}].Pt[{p}].V" for c in range(1, 4) for p in range(1, 5)]  # 1-based
OTHERS = {"705.Crv[1].VRef": "VNomPct", "705.Crv[1].Pt[1].Var": "DeptRef",
          "705.Crv[2].VRefAuto": "VNomPct"}  # fmt: skip


def agate(firmware: str, maker: str = "FranklinWH") -> DeviceIdentity:
    return DeviceIdentity(maker, "aGate X", None, firmware, "SN-PLACEHOLDER", 1)


def found(identity: DeviceIdentity, off=()) -> ActiveQuirks:
    return ActiveQuirks([QuirkSet.load(FILE)], identity, off)


def units_after(quirks: ActiveQuirks, key: str, units: str = "VNomPct"):
    after = quirks.apply(state(key, 207, units=units, label="Voltage"))
    assert after is not None
    return after


def test_shipped_file_is_firmware_layer_with_sources() -> None:
    [qs] = load_sets([FILE])
    assert qs.layer == "firmware"
    assert [q.id for q in qs.quirks] == [QUIRK]
    assert qs.source and all(item.source for item in qs.items)


@pytest.mark.parametrize("maker", ["FranklinWH", "FranklinWH Technologies Co., Ltd"])
def test_v_points_read_as_volts_on_v10(maker: str) -> None:
    quirks = found(agate("V10R01B04D00", maker))
    for key in V_POINTS:
        after = units_after(quirks, key)
        assert (after.units, after.value, after.quirks) == ("V", 207, (QUIRK,)), key
    for key, units in OTHERS.items():
        assert units_after(quirks, key, units).units == units, key


@pytest.mark.parametrize(
    "identity",
    [agate("V12R02B60D00"), agate("V10R01B04D01"), agate("V10R01B04D00", "ExampleMaker")],
)
def test_other_firmware_or_maker_keeps_percent(identity: DeviceIdentity) -> None:
    quirks = found(identity)
    assert not quirks.sets
    assert units_after(quirks, V_POINTS[0]).units == "VNomPct"


def test_switched_off_keeps_percent() -> None:
    quirks = found(agate("V10R01B04D00"), off=[QUIRK])
    assert units_after(quirks, V_POINTS[0]).units == "VNomPct"


def test_ha_sees_a_voltage() -> None:
    after = units_after(found(agate("V10R01B04D00")), V_POINTS[0])
    point = point_json(after) | {"type": "uint16"}
    fields = sensor_classes(point)
    assert (fields["unit_of_measurement"], fields["device_class"]) == ("V", "voltage")
