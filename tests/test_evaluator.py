"""Tests for the evaluator: constants and derived rules (design 3a). All rules are made up."""

import asyncio
from enum import IntEnum

import pytest
from fastapi.testclient import TestClient
from modbus_connection.mock import MockModbusUnit
from test_api import AUTH, TOKEN, load_device
from test_quirks import active, quirk_set, state

from modbus_bridge.api import create_app
from modbus_bridge.evaluator import EvalError, Formula, Missing, RuleError
from modbus_bridge.quirks import QuirkError, QuirkSet
from modbus_bridge.service import DeviceService


def run(text: str, **env) -> object:
    def lookup(name: str):
        if name not in env:
            raise Missing(name)
        return env[name]

    return Formula.compile(text, "test").evaluate(lookup, {"t": {1: "one", 2: "two"}})


@pytest.mark.parametrize(
    ("text", "env", "expected"),
    [
        ("1 + 2 * 3 - 4 / 2", {}, 5.0),
        ("7 // 2 + 7 % 2", {}, 4),
        ("-x", {"x": 3}, -3),
        ("x > 1 and x < 5", {"x": 3}, True),
        ("x < 1 or not x", {"x": 0}, True),
        ("1 < x <= 3", {"x": 3}, True),
        ("'a' if x == 1 else 'b'", {"x": 2}, "b"),
        ("x in [1, 2, 3]", {"x": 2}, True),
        ("x not in [1, 2]", {"x": 2}, False),
        ("abs(x) + min(1, 2, x) + max(x, 0)", {"x": -4}, 0),
        ("lookup(t, x)", {"x": 2}, "two"),
        ("true and not false", {}, True),
        ("s == 'on'", {"s": "on"}, True),
    ],
)
def test_formula_language(text: str, env: dict, expected: object) -> None:
    assert run(text, **env) == expected


@pytest.mark.parametrize(
    "text",
    [
        "x.real",
        "__import__('os')",
        "round(x)",
        "x ** 2",
        "[i for i in [1]]",
        "x[0]",
        "lambda: 1",
        "x in y",
        "None",
        "f'{x}'",
        "max(x)",
        "abs",
        "x := 1",
        "",
        "1 +",
        "x & 1",
    ],
)
def test_formula_refusals(text: str) -> None:
    with pytest.raises(RuleError):
        Formula.compile(text, "test")


@pytest.mark.parametrize(
    ("text", "env", "message"),
    [
        ("1 / x", {"x": 0}, "division by zero"),
        ("lookup(t, x)", {"x": 9}, "no entry"),
        ("x + 1", {"x": "text"}, "cannot combine"),
    ],
)
def test_runtime_errors(text: str, env: dict, message: str) -> None:
    with pytest.raises(EvalError, match=message):
        run(text, **env)


def test_enum_inputs_are_their_numbers() -> None:
    class St(IntEnum):
        MPPT = 4

    assert run("x in [4, 5]", x=St.MPPT) is True


def rule(rid: str, output: str, formula: str, inputs: dict | None = None, **more) -> dict:
    return {"id": rid, "output": output, "inputs": inputs or {}, "formula": formula,
            "reason": "test", **more}  # fmt: skip


def const(cid: str, name: str, value, **more) -> dict:
    return {"id": cid, "name": name, "value": value, "reason": "test", **more}


def rules_set(*rules: dict, constants=(), layer="vendor", set_id=None) -> dict:
    match = {
        "vendor": {"manufacturer": "ExampleMaker"},
        "model": {"manufacturer": "ExampleMaker", "model": ["ExampleModel"]},
    }[layer]
    return quirk_set(layer, match, set_id=set_id) | {
        "rules": list(rules),
        "constants": list(constants),
    }


def outputs(found, *states) -> dict:
    return {s.key: s for s in found.engine.evaluate({s.key: s for s in states})}


STATE = rule(
    "r-state",
    "battery_state",
    "'idle' if st not in [4, 5] else ('discharging' if p > band else "
    "('charging' if p < -band else 'idle'))",
    {"p": "raw.batt_w", "st": "103.St"},
    values=[["idle", "No power flow"], ["charging", "Charging"], ["discharging", "Discharging"]],
)


def test_rule_with_constant_and_trace() -> None:
    found = active(rules_set(STATE, constants=[const("c-band", "band", 50, units="W")]))
    out = outputs(found, state("raw.batt_w", 1200), state("103.St", 4))["label.battery_state"]
    assert out.value == "discharging"
    assert out.quirks == ("r-state",)
    assert out.trace["rule"] == "r-state"
    assert out.trace["inputs"]["p"] == {"key": "raw.batt_w", "value": 1200}
    assert out.trace["constants"]["band"]["value"] == 50
    assert out.trace["constants"]["band"]["units"] == "W"
    assert out.trace["description"] == "Discharging"


def test_missing_input_gives_no_value_and_is_not_failing() -> None:
    found = active(rules_set(STATE, constants=[const("c-band", "band", 50)]))
    out = outputs(found, state("raw.batt_w", None), state("103.St", 4))["label.battery_state"]
    assert out.value is None
    assert out.trace["missing"] == "p"
    assert {r["id"]: r["state"] for r in found.report()["rules"]} == {"r-state": "active"}


def test_unknown_constant_fails_until_it_succeeds() -> None:
    found = active(rules_set(rule("r", "x2", "a * k", {"a": "raw.a"})))
    out = outputs(found, state("raw.a", 2))["label.x2"]
    assert out.value is None
    [entry] = found.report()["rules"]
    assert entry["state"] == "failing"
    assert "unknown constant 'k'" in entry["error"]


def test_value_outside_values_fails() -> None:
    found = active(rules_set(rule("r", "x", "a", {"a": "raw.a"}, values=[[1, "One"]])))
    assert outputs(found, state("raw.a", 2))["label.x"].value is None
    assert found.report()["rules"][0]["state"] == "failing"
    assert outputs(found, state("raw.a", 1))["label.x"].value == 1
    assert found.report()["rules"][0]["state"] == "active"


def test_latch_remembers_one_flag() -> None:
    found = active(
        rules_set(
            rule(
                "r",
                "load",
                "fine if latched else coarse",
                {"fine": "raw.fine", "coarse": "raw.coarse"},
                latch="fine % 100 != 0",
            )
        )  # fmt: skip
    )
    first = outputs(found, state("raw.fine", 300), state("raw.coarse", 300))["label.load"]
    assert (first.value, first.trace["latched"]) == (300, False)
    assert (
        outputs(found, state("raw.fine", 312), state("raw.coarse", 300))["label.load"].value == 312
    )
    assert (
        outputs(found, state("raw.fine", 400), state("raw.coarse", 500))["label.load"].value == 400
    )


def test_total_must_be_true_or_false() -> None:
    with pytest.raises(QuirkError, match="total must be true or false"):
        QuirkSet.from_json(rules_set(rule("r", "x", "1") | {"total": 1}))


def test_latch_rules_checked() -> None:
    with pytest.raises(QuirkError, match="needs a latch"):
        QuirkSet.from_json(rules_set(rule("r", "x", "1 if latched else 0")))
    with pytest.raises(QuirkError, match="cannot use 'latched'"):
        QuirkSet.from_json(rules_set(rule("r", "x", "1", latch="latched")))


def test_dependency_order_and_lookup() -> None:
    found = active(
        rules_set(
            rule("r2", "mode_text", "lookup(modes, m) if ok else 'off'",
                 {"m": "raw.mode", "ok": "label.mode_ok"},
                 tables={"modes": [[1, "backup"], [2, "self_consumption"]]}),
            rule("r1", "mode_ok", "m > 0", {"m": "raw.mode"}),
        )
    )  # fmt: skip
    outs = outputs(found, state("raw.mode", 2))
    assert outs["label.mode_ok"].value == 1
    assert outs["label.mode_text"].value == "self_consumption"


def test_loop_in_one_file_refused() -> None:
    with pytest.raises(QuirkError, match="loop"):
        QuirkSet.from_json(
            rules_set(rule("a", "x", "y", {"y": "label.y"}), rule("b", "y", "x", {"x": "label.x"}))
        )


def test_loop_across_files_fails_both() -> None:
    a = rules_set(rule("a", "x", "y", {"y": "label.y"}), set_id="a")
    b = rules_set(rule("b", "y", "x", {"x": "label.x"}), layer="model", set_id="b")
    found = active(a, b)
    outs = outputs(found)
    assert outs["label.x"].value is None and outs["label.y"].value is None
    assert {r["id"]: r["state"] for r in found.report()["rules"]} == {
        "a": "failing",
        "b": "failing",
    }


def test_layers_override_off_and_clash() -> None:
    vendor = rules_set(rule("v", "x", "k", {}), constants=[const("vk", "k", 1)])
    model = rules_set(rule("m", "x", "k * 10", {}), constants=[const("mk", "k", 2)], layer="model")
    found = active(vendor, model)
    assert outputs(found)["label.x"].value == 20
    states = {r["id"]: r["state"] for r in (*found.report()["rules"], *found.report()["constants"])}
    assert states == {"v": "overridden", "m": "active", "vk": "overridden", "mk": "active"}
    found = active(vendor, model, off=["m", "mk"])
    assert outputs(found)["label.x"].value == 1
    clash = active(vendor, rules_set(rule("v2", "x", "2", {}), set_id="other"))
    assert outputs(clash)["label.x"].value is None
    assert {r["id"]: r["state"] for r in clash.report()["rules"]} == {
        "v": "failing",
        "v2": "failing",
    }


def test_constant_clash_fails_rules_that_use_it() -> None:
    a = rules_set(rule("r", "x", "k", {}), constants=[const("k1", "k", 1)], set_id="a")
    b = rules_set(constants=[const("k2", "k", 2)], set_id="b")
    found = active(a, b)
    assert outputs(found)["label.x"].value is None
    assert "clashes" in found.report()["rules"][0]["error"]


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (rule("r", "x", "a", {"a": "nope"}), "not a point key"),
        (rule("r", "x", "a", {"a": "103.module[*].W"}), "not a point key"),
        (rule("r", "X", "1"), "output"),
        (rule("r", "x", "lookup(t, 1)"), "unknown table"),
        (rule("r", "x", "1", tables={"t": [[1, "a"], [1, "b"]]}), "twice"),
        (rule("r", "x", "1", values=[[1, ""]]), "description"),
        (rule("r", "x", "1", colour="red"), "unknown field"),
    ],
)
def test_bad_rules_refused(bad: dict, message: str) -> None:
    with pytest.raises(QuirkError, match=message):
        QuirkSet.from_json(rules_set(bad))


def test_bad_constants_refused() -> None:
    with pytest.raises(QuirkError, match="number"):
        QuirkSet.from_json(rules_set(constants=[const("c", "k", "50")]))
    with pytest.raises(QuirkError, match="used twice"):
        QuirkSet.from_json(rules_set(constants=[const("c1", "k", 1), const("c2", "k", 2)]))


def test_through_the_service_and_api(mock_modbus_unit: MockModbusUnit) -> None:
    load_device(mock_modbus_unit)
    sets = [
        QuirkSet.from_json(
            rules_set(
                rule("r-full", "full", "soc >= limit", {"soc": "713.SoC"}),
                rule("r-gone", "gone", "x", {"x": "713.SoH"}),
                constants=[const("c-limit", "limit", 80, units="%")],
            )
        )
    ]
    service = DeviceService(
        "unit1", mock_modbus_unit, interval=60, reads=1, read_interval=0, quirk_sets=sets
    )
    asyncio.run(service.setup())
    client = TestClient(create_app({"unit1": service}, [TOKEN]))
    points = client.get("/api/v1/devices/unit1/points", headers=AUTH).json()["points"]
    assert points["label.full"]["value"] == 1
    assert points["label.full"]["trace"]["inputs"]["soc"] == {"key": "713.SoC", "value": 87.5}
    assert points["label.gone"]["available"] is False
    assert points["label.gone"]["trace"]["missing"] == "x"
    assert "trace" not in points["713.SoC"]
    body = client.get("/api/v1/devices/unit1/quirks", headers=AUTH).json()
    assert {r["id"]: r["state"] for r in body["rules"]} == {"r-full": "active", "r-gone": "active"}
    assert body["constants"][0]["value"] == 80


def test_serve_accepts_off_for_every_kind_of_id(tmp_path) -> None:
    import argparse
    import json

    from modbus_bridge.serve import build

    data = rules_set(rule("rule-1", "x", "1"), constants=[const("const-1", "k", 1)])
    data["quirks"] = [{"id": "quirk-1", "point": "103.W", "scale": 2, "reason": "test"}]
    data["readings"] = [{"id": "read-1", "name": "r", "address": 1, "type": "uint16",
                         "reason": "test"}]  # fmt: skip
    (tmp_path / "set.json").write_text(json.dumps(data))
    (tmp_path / "token").write_text("not-secret\n")
    args = argparse.Namespace(
        token_file=tmp_path / "token", pics=None, quirks=[tmp_path / "set.json"],
        quirk_off=["rule-1", "const-1", "quirk-1", "read-1"], device_host="192.0.2.10",
        device_port=502, timeout=1.0, device_id=None, unit=1, interval=5.0, user_quirks=None,
    )  # fmt: skip
    build(args)  # no error
    args.quirk_off = ["nope"]
    with pytest.raises(QuirkError, match="nope"):
        build(args)
