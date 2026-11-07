"""Tests for maker names that differ by firmware (design Q3). Values are made up."""

import asyncio
import logging

import pytest
from modbus_connection.mock import MockModbusUnit
from test_franklinwh_set import FILE, run
from test_quirks import q, quirk_set, state
from test_recheck import load, setup  # noqa: F401 (fixture)

from modbus_bridge.quirks import ActiveQuirks, QuirkError, QuirkSet
from modbus_bridge.service import DeviceChanged, DeviceService
from modbus_bridge.sunspec import DeviceIdentity

V10 = DeviceIdentity("FranklinWH Technologies Co., Ltd", "aGate X", None, "V10R01B04D00",
                     "SN-PLACEHOLDER", 1)  # fmt: skip


def ident(maker: str) -> DeviceIdentity:
    return DeviceIdentity(maker, "ExampleModel", None, "1.0.0", "SN-PLACEHOLDER", 1)


def matched(match: dict, maker: str) -> bool:
    qs = QuirkSet.from_json(quirk_set("vendor", match, quirks=[q("a", "713.SoC", label="x")]))
    return bool(ActiveQuirks([qs], ident(maker), []).sets)


@pytest.mark.parametrize(
    ("maker", "expected"),
    [("Maker", True), ("Maker Co., Ltd", True), ("Maker Co.", False), ("maker", False),
     ("Maker Co., Ltd ", False), ("Other", False)],
)  # fmt: skip
def test_list_of_makers_matches_each_name_exactly(maker: str, expected: bool) -> None:
    assert matched({"manufacturer": ["Maker", "Maker Co., Ltd"]}, maker) is expected


def test_one_name_as_text_still_works() -> None:
    assert matched({"manufacturer": "Maker"}, "Maker")
    assert not matched({"manufacturer": "Maker"}, "Maker Co., Ltd")


@pytest.mark.parametrize("bad", [[], [""], [1], 1, ""])
def test_bad_maker_names_are_refused(bad) -> None:
    with pytest.raises(QuirkError):
        QuirkSet.from_json(quirk_set("vendor", {"manufacturer": bad}))


def test_franklinwh_set_applies_on_v10() -> None:
    quirks = ActiveQuirks([QuirkSet.load(FILE)], V10, [])
    assert [s.id for s in quirks.sets] == ["franklinwh"]
    assert quirks.apply(state("714.DCA", 0)) is None  # hidden
    assert [r.id for r in quirks.readings] and quirks.engine.all_rules
    out = run(quirks, raw__home_load_fine=None, raw__home_load_coarse=300)["home_load_power"]
    assert out.value == 300


def test_shipped_set_names_both_makers_with_a_source() -> None:
    qs = QuirkSet.load(FILE)
    assert qs.match.manufacturers == ("FranklinWH", "FranklinWH Technologies Co., Ltd")
    assert "reference_scan_static_2026-10-07.json" in qs.source


def test_same_serial_and_model_other_maker_is_the_same_device(setup, caplog) -> None:  # noqa: F811
    service, unit, conn, _ = setup
    queue = service.subscribe()
    load(unit, maker="ExampleMaker Co., Ltd", version="2.0.0")
    conn.simulate_connection_lost()
    with caplog.at_level(logging.WARNING):
        asyncio.run(service.poll_once())
    assert service.refused is None
    assert service.device.identity.manufacturer == "ExampleMaker Co., Ltd"
    assert service.device.identity.version == "2.0.0"
    assert service.poller.snapshot["713.SoC"].value == 87.5
    items = []
    while not queue.empty():
        items.append(queue.get_nowait())
    [notice] = [i for i in items if isinstance(i, DeviceChanged)]
    assert notice.identity["manufacturer"] == "ExampleMaker Co., Ltd"
    [warning] = [r.getMessage() for r in caplog.records if "changed after" in r.getMessage()]
    assert "maker ExampleMaker -> ExampleMaker Co., Ltd" in warning


def test_other_serial_is_still_refused(setup) -> None:  # noqa: F811
    service, unit, conn, _ = setup
    load(unit, maker="ExampleMaker Co., Ltd", serial="SN-OTHER")
    conn.simulate_connection_lost()
    asyncio.run(service.poll_once())
    assert service.refused is not None
    assert "ExampleMaker Co., Ltd" in service.refused and "SN-OTHER" in service.refused


def test_no_serial_other_maker_is_still_refused(
    mock_modbus_unit: MockModbusUnit, mock_modbus_connection
) -> None:
    load(mock_modbus_unit, serial="")
    service = DeviceService("unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0)
    asyncio.run(service.setup())
    load(mock_modbus_unit, serial="", maker="OtherMaker")
    mock_modbus_connection.simulate_connection_lost()
    asyncio.run(service.poll_once())
    assert service.refused is not None and "OtherMaker" in service.refused
