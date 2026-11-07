"""Tests for the bundled FranklinWH quirk set (design N1-N11, R1-R5). Values are made up."""

from pathlib import Path

import pytest
from test_quirks import state

import modbus_bridge
from modbus_bridge.quirks import ActiveQuirks, QuirkSet, load_sets
from modbus_bridge.sunspec import DeviceIdentity

FILE = Path(modbus_bridge.__file__).parent / "quirk_sets" / "franklinwh.json"
AGATE = DeviceIdentity("FranklinWH", "aGate X", None, "V12R02B60D00", "SN-PLACEHOLDER", 1)
OTHER = DeviceIdentity("ExampleMaker", "ExampleModel", None, "1.0.0", "SN-PLACEHOLDER", 1)

LABELS = {
    "home_load_power",  # N1
    "solar_local_power",  # N2
    "solar_remote_power_1",  # N3
    "solar_remote_power_2",
    "solar_total_power",  # N4
    "solar_local_installed",  # N5
    "solar_remote_installed",
    "solar_energy_total",  # N6
    "solar_local_energy",
    "battery_operating_mode",  # N7
    "battery_reserve_active",  # N8
    "battery_reserve_self",
    "battery_reserve_tou",
    "battery_inverter_state",  # N9
    "grid_connection_status",  # N10
    "battery_power_fine",  # N11
    "battery_charge_rating",  # R3
    "battery_discharge_rating",
}


def found(off=()) -> ActiveQuirks:
    return ActiveQuirks([QuirkSet.load(FILE)], AGATE, off)


def run(quirks: ActiveQuirks, **values) -> dict:
    """Rule outputs by label name, from point keys given as e.g. raw__mode or p701__InvSt."""
    states = {}
    for name, value in values.items():
        key = name.removeprefix("p").replace("__", ".")
        states[key] = state(key, value)
    return {s.key.removeprefix("label."): s for s in quirks.engine.evaluate(states)}


def test_loads_and_matches_franklinwh_only() -> None:
    [qs] = load_sets([FILE])
    assert qs.layer == "vendor"
    assert {r.output for r in qs.rules} == LABELS
    assert found().sets
    assert not ActiveQuirks([qs], OTHER, ()).sets
    for item in qs.items:
        assert item.source


@pytest.mark.parametrize(
    ("invst", "dcw", "expected"),
    [
        (3, -51, "charging"),
        (3, -50, "idle"),
        (3, 50, "idle"),
        (3, 51, "discharging"),
        (0, 2000, "idle"),
        (1, 2000, "idle"),
        (6, -2000, "idle"),
        (7, 100, "idle"),
    ],
)
def test_r1_battery_inverter_state(invst: int, dcw: int, expected: str) -> None:
    out = run(found(), p701__InvSt=invst, p714__DCW=dcw)["battery_inverter_state"]
    assert out.value == expected
    if invst == 3:
        assert out.trace["constants"]["battery_idle_band_w"]["value"] == 50


def test_r2_home_load_latches_on_fine_value() -> None:
    quirks = found()
    first = run(quirks, raw__home_load_fine=300, raw__home_load_coarse=300)["home_load_power"]
    assert (first.value, first.trace["latched"]) == (300, False)
    second = run(quirks, raw__home_load_fine=1000, raw__home_load_coarse=900)["home_load_power"]
    assert second.value == 900
    third = run(quirks, raw__home_load_fine=312, raw__home_load_coarse=300)["home_load_power"]
    assert (third.value, third.trace["latched"]) == (312, True)
    fourth = run(quirks, raw__home_load_fine=400, raw__home_load_coarse=500)["home_load_power"]
    assert fourth.value == 400


@pytest.mark.parametrize(("raw", "watts"), [(160, 16000), (192, 19200), (5000, 5000), (0, 0)])
def test_r3_ratings(raw: int, watts: int) -> None:
    outs = run(found(), p702__WChaRteMaxRtg=raw, p702__WDisChaRteMaxRtg=raw)
    assert outs["battery_charge_rating"].value == watts
    assert outs["battery_discharge_rating"].value == watts


@pytest.mark.parametrize(
    ("code", "status"),
    [(1, "restarting"), (2, "on_grid"), (3, "off_grid"), (6, "dispatch_active"), (4, None)],
)
def test_r4_grid_status(code: int, status: str | None) -> None:
    quirks = found()
    assert run(quirks, raw__grid_status=code)["grid_connection_status"].value == status
    assert ("fwh-n10-r4" in quirks.engine.errors) is (status is None)


@pytest.mark.parametrize(
    ("code", "mode"),
    [(1, "emergency_backup"), (2, "self_consumption"), (3, "time_of_use"), (0, None), (4, None)],
)
def test_r5_operating_mode(code: int, mode: str | None) -> None:
    quirks = found()
    out = run(quirks, raw__operating_mode=code)["battery_operating_mode"]
    assert out.value == mode
    assert ("fwh-n7-r5" in quirks.engine.errors) is (mode is None)


def test_n5_flags_accept_0_and_1_only() -> None:
    quirks = found()
    outs = run(quirks, raw__pv_local_installed=1, raw__pv_remote_installed=2)
    assert outs["solar_local_installed"].value == 1
    assert outs["solar_remote_installed"].value is None
    assert "fwh-n5-remote" in quirks.engine.errors


def test_pass_through_labels_keep_value_and_units() -> None:
    outs = run(found(), raw__pv_total=-12, raw__battery_power_fine=-4998, raw__reserve_tou=15)
    assert (outs["solar_total_power"].value, outs["solar_total_power"].units) == (-12, "W")
    assert outs["battery_power_fine"].value == -4998
    assert (outs["battery_reserve_tou"].value, outs["battery_reserve_tou"].units) == (15, "%")


def test_missing_input_gives_no_value() -> None:
    out = run(found(), p701__InvSt=3)["battery_inverter_state"]
    assert out.value is None
    assert out.trace["missing"] == "p"


def test_rule_can_be_switched_off() -> None:
    outs = run(found(off=["fwh-n7-r5"]), raw__operating_mode=2)
    assert "battery_operating_mode" not in outs


def test_point_json_carries_options_and_total() -> None:
    from modbus_bridge.service import point_json

    outs = run(found(), raw__operating_mode=2, raw__pv_energy_total=10)
    mode = point_json(next(s for k, s in outs.items() if k == "battery_operating_mode"))
    assert mode["options"] == ["emergency_backup", "self_consumption", "time_of_use"]
    assert "total" not in mode
    energy = point_json(outs["solar_energy_total"])
    assert energy["total"] is True
    assert "options" not in energy


NO_VALUE_READINGS = {"fwh-r-load-coarse", "fwh-r-load-fine", "fwh-r-reserve-self",
                     "fwh-r-reserve-tou", "fwh-r-reserve-active", "fwh-r-pv-local-fitted",
                     "fwh-r-pv-remote-fitted", "fwh-r-mode", "fwh-r-grid-status"}  # fmt: skip
PV_INT16 = {"fwh-r-pv-total", "fwh-r-pv-local", "fwh-r-pv-remote-1", "fwh-r-pv-remote-2"}


def readings() -> dict:
    return {r.id: r for r in QuirkSet.load(FILE).readings}


def test_0xffff_gives_no_value_on_load_and_reserves() -> None:
    by_id = readings()
    for rid in NO_VALUE_READINGS:
        reading = by_id[rid]
        assert reading.decode([0xFFFF]) is None, rid
        assert (reading.decode([0]), reading.decode([42])) == (0, 42), rid
        assert "poller.py" in reading.source


@pytest.mark.parametrize(
    ("reading", "label"),
    [
        ("pv_local_installed", "solar_local_installed"),
        ("pv_remote_installed", "solar_remote_installed"),
        ("operating_mode", "battery_operating_mode"),
        ("grid_status", "grid_connection_status"),
    ],
)
def test_no_value_on_flags_mode_and_status_gives_no_label(reading: str, label: str) -> None:
    out = run(found(), **{f"raw__{reading}": None})[label]
    assert out.value is None


def test_int16_pv_readings_unchanged() -> None:
    by_id = readings()
    for rid in PV_INT16:
        assert by_id[rid].decode([0xFFFF]) == -1, rid


def test_no_value_on_16000_does_not_latch_n1() -> None:
    quirks = found()
    out = run(quirks, raw__home_load_fine=None, raw__home_load_coarse=300)["home_load_power"]
    assert out.value == 300
    assert out.trace["latched"] is False
    later = run(quirks, raw__home_load_fine=400, raw__home_load_coarse=500)["home_load_power"]
    assert later.value == 500


@pytest.mark.parametrize(
    ("key", "hidden"),
    [
        ("714.DCA", True), ("714.Prt[1].DCA", True), ("714.Prt[2].DCA", True),
        ("701.DERMode", True), ("714.DCW", False), ("714.Prt[1].DCAlrm", False),
        ("714.Prt[1].DCV", False), ("701.Alrm", False), ("701.DERModeX", False),
    ],
)  # fmt: skip
def test_hide_quirks_match_only_their_points(key: str, hidden: bool) -> None:
    assert (found().apply(state(key, 0)) is None) is hidden


def test_hide_quirks_have_sources_and_switch_off() -> None:
    [qs] = load_sets([FILE])
    ids = {"fwh-q-dca", "fwh-q-dca-port", "fwh-q-dermode"}
    assert {q.id for q in qs.quirks} == ids
    assert all("vendor-issues.md" in q.source for q in qs.quirks)
    quirks = found(off=sorted(ids))
    for key in ("714.DCA", "714.Prt[1].DCA", "701.DERMode"):
        assert quirks.apply(state(key, 0)) is not None
