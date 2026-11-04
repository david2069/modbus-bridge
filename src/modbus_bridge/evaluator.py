"""The evaluator: named constants and derived rules, held as data (design 3a).

Vendor, model and firmware layers supply constants and rules only; this module
is the same for every maker. A formula is a small, fixed expression language
checked when the file loads; no general code is run. A missing input gives no
value, never 0 (rule 8). Every output carries a trace of what produced it.
"""

from __future__ import annotations

import ast
import logging
import math
import operator
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .poller import PointState

_LOGGER = logging.getLogger(__name__)

LATCHED = "latched"
FUNCTIONS = ("abs", "min", "max", "lookup")
_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_RESERVED = {LATCHED, "true", "false", *FUNCTIONS}

_BINARY: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_COMPARE: dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}


class RuleError(ValueError):
    """A constant or rule in a quirk set is not valid."""


class EvalError(Exception):
    """A rule could not give a value this time (e.g. division by zero)."""


class Missing(Exception):
    """An input has no value, so the rule gives no value. Not an error."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name


# ----- formulas -------------------------------------------------------------


@dataclass(frozen=True)
class Formula:
    """A checked expression. ``names`` are the free names it uses."""

    text: str
    tree: ast.expr
    names: frozenset[str]

    @classmethod
    def compile(cls, text: str, what: str) -> Formula:
        if not isinstance(text, str) or not text.strip():
            raise RuleError(f"{what} must be non-empty text")
        try:
            tree = ast.parse(text.strip(), mode="eval").body
        except SyntaxError as err:
            raise RuleError(f"{what}: {err.msg}") from err
        names: set[str] = set()
        _check(tree, what, names)
        return cls(text, tree, frozenset(names))

    def evaluate(self, env: Callable[[str], Any], tables: Mapping[str, Mapping[Any, Any]]) -> Any:
        return _eval(self.tree, env, tables)


def _check(node: ast.AST, what: str, names: set[str]) -> None:
    def refuse(detail: str) -> RuleError:
        return RuleError(f"{what}: {detail} is not allowed")

    if isinstance(node, ast.Constant):
        if node.value is None or not isinstance(node.value, (int, float, str, bool)):
            raise refuse(f"the value {node.value!r}")
    elif isinstance(node, ast.Name):
        if node.id in FUNCTIONS:
            raise refuse(f"{node.id} without a call")
        if node.id not in ("true", "false"):
            names.add(node.id)
    elif isinstance(node, ast.BinOp):
        if type(node.op) not in _BINARY:
            raise refuse(f"the operator {type(node.op).__name__}")
        _check(node.left, what, names)
        _check(node.right, what, names)
    elif isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
            raise refuse(f"the operator {type(node.op).__name__}")
        _check(node.operand, what, names)
    elif isinstance(node, ast.BoolOp):
        for value in node.values:
            _check(value, what, names)
    elif isinstance(node, ast.Compare):
        _check(node.left, what, names)
        for op, right in zip(node.ops, node.comparators, strict=True):
            if type(op) not in _COMPARE:
                raise refuse(f"the comparison {type(op).__name__}")
            if isinstance(op, (ast.In, ast.NotIn)):
                if not isinstance(right, (ast.List, ast.Tuple, ast.Set)) or not all(
                    isinstance(e, ast.Constant) for e in right.elts
                ):
                    raise RuleError(f"{what}: 'in' needs a list of constants, e.g. [1, 2]")
                for element in right.elts:
                    _check(element, what, names)
            else:
                _check(right, what, names)
    elif isinstance(node, ast.IfExp):
        for part in (node.test, node.body, node.orelse):
            _check(part, what, names)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise refuse("a call to anything but abs, min, max or lookup")
        if node.keywords:
            raise refuse("a keyword argument")
        if node.func.id == "abs" and len(node.args) != 1:
            raise RuleError(f"{what}: abs takes one value")
        if node.func.id in ("min", "max") and len(node.args) < 2:
            raise RuleError(f"{what}: {node.func.id} takes two or more values")
        if node.func.id == "lookup":
            if len(node.args) != 2 or not isinstance(node.args[0], ast.Name):
                raise RuleError(f"{what}: lookup takes a table name and a value")
            _check(node.args[1], what, names)
            return
        for arg in node.args:
            _check(arg, what, names)
    else:
        raise refuse(type(node).__name__)


def _number(value: Any) -> Any:
    if isinstance(value, Enum):
        return int(value.value)
    return value


def _eval(node: ast.AST, env: Callable[[str], Any], tables: Mapping[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in ("true", "false"):
            return node.id == "true"
        return _number(env(node.id))
    if isinstance(node, ast.BinOp):
        left = _eval(node.left, env, tables)
        right = _eval(node.right, env, tables)
        try:
            result = _BINARY[type(node.op)](left, right)
        except ZeroDivisionError as err:
            raise EvalError("division by zero") from err
        except TypeError as err:
            raise EvalError(f"cannot combine {left!r} and {right!r}") from err
        if isinstance(result, float) and not math.isfinite(result):
            raise EvalError("result is not a finite number")
        return result
    if isinstance(node, ast.UnaryOp):
        value = _eval(node.operand, env, tables)
        if isinstance(node.op, ast.Not):
            return not value
        try:
            return -value if isinstance(node.op, ast.USub) else +value
        except TypeError as err:
            raise EvalError(f"cannot negate {value!r}") from err
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result: Any = True
            for part in node.values:
                result = _eval(part, env, tables)
                if not result:
                    return result
            return result
        result = False
        for part in node.values:
            result = _eval(part, env, tables)
            if result:
                return result
        return result
    if isinstance(node, ast.Compare):
        left = _eval(node.left, env, tables)
        for op, right_node in zip(node.ops, node.comparators, strict=True):
            if isinstance(right_node, (ast.List, ast.Tuple, ast.Set)):
                right: Any = [_eval(e, env, tables) for e in right_node.elts]
            else:
                right = _eval(right_node, env, tables)
            try:
                if not _COMPARE[type(op)](left, right):
                    return False
            except TypeError as err:
                raise EvalError(f"cannot compare {left!r} and {right!r}") from err
            left = right
        return True
    if isinstance(node, ast.IfExp):
        branch = node.body if _eval(node.test, env, tables) else node.orelse
        return _eval(branch, env, tables)
    if isinstance(node, ast.Call):
        assert isinstance(node.func, ast.Name)
        name = node.func.id
        if name == "lookup":
            assert isinstance(node.args[0], ast.Name)
            table = tables.get(node.args[0].id)
            if table is None:
                raise EvalError(f"no table {node.args[0].id!r}")
            key = _eval(node.args[1], env, tables)
            if key not in table:
                raise EvalError(f"table {node.args[0].id!r} has no entry for {key!r}")
            return table[key]
        args = [_eval(a, env, tables) for a in node.args]
        try:
            return {"abs": abs, "min": min, "max": max}[name](*args)
        except TypeError as err:
            raise EvalError(f"{name} cannot take {args!r}") from err
    raise EvalError(f"cannot evaluate {type(node).__name__}")  # refused at load


# ----- constants and rules as data -------------------------------------------


def _fields(data: Any, what: str, required: set[str], optional: set[str]) -> None:
    if not isinstance(data, dict):
        raise RuleError(f"{what} must be an object")
    missing = required - data.keys()
    unknown = data.keys() - required - optional
    if missing:
        raise RuleError(f"{what} is missing {', '.join(sorted(missing))}")
    if unknown:
        raise RuleError(f"{what} has unknown field(s) {', '.join(sorted(unknown))}")


def _text(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuleError(f"{what} must be non-empty text")
    return value


def _name(value: Any, what: str) -> str:
    if not isinstance(value, str) or not _NAME.match(value) or value in _RESERVED:
        raise RuleError(f"{what} {value!r} must be lower case letters, digits and _")
    return value


def _is_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))


@dataclass(frozen=True)
class Constant:
    id: str
    name: str
    value: float
    units: str | None
    reason: str
    source: str
    layer: str
    set_id: str

    def describe(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "value": self.value, "units": self.units,
                "set": self.set_id, "layer": self.layer, "reason": self.reason,
                "source": self.source}  # fmt: skip


def parse_constant(data: Any, layer: str, set_id: str, source: str) -> Constant:
    _fields(data, "constant", {"id", "name", "value", "reason"}, {"units", "source"})
    cid = _text(data["id"], "constant id")
    if not _is_number(data["value"]):
        raise RuleError(f"constant {cid}: value must be a number")
    return Constant(
        id=cid,
        name=_name(data["name"], f"constant {cid}: name"),
        value=data["value"],
        units=_text(data["units"], f"constant {cid}: units") if "units" in data else None,
        reason=_text(data["reason"], f"constant {cid}: reason"),
        source=_text(data.get("source", source), f"constant {cid}: source"),
        layer=layer,
        set_id=set_id,
    )


@dataclass(frozen=True)
class Rule:
    id: str
    output: str
    inputs: Mapping[str, str]
    formula: Formula
    latch: Formula | None
    tables: Mapping[str, Mapping[Any, Any]]
    values: Mapping[Any, str] | None
    units: str | None
    label: str | None
    reason: str
    source: str
    layer: str
    set_id: str
    constants: frozenset[str] = field(default_factory=frozenset)
    """Names in the formula that are not inputs: looked up as constants."""
    total: bool = False
    """The output only counts up over the device's life (a lifetime energy total)."""

    @property
    def key(self) -> str:
        return f"label.{self.output}"

    @property
    def options(self) -> tuple[Any, ...] | None:
        """The allowed output values, if the rule lists them."""
        return None if self.values is None else tuple(self.values)

    def depends_on(self) -> set[str]:
        """Outputs of other rules this rule reads."""
        return {k.removeprefix("label.") for k in self.inputs.values() if k.startswith("label.")}

    def describe(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "point": self.key,
            "set": self.set_id,
            "layer": self.layer,
            "inputs": dict(self.inputs),
            "formula": self.formula.text,
            "latch": None if self.latch is None else self.latch.text,
            "tables": {n: [[k, v] for k, v in t.items()] for n, t in self.tables.items()},
            "values": None if self.values is None else [[k, v] for k, v in self.values.items()],
            "units": self.units,
            "label": self.label,
            "total": self.total,
            "reason": self.reason,
            "source": self.source,
        }


def _pairs(value: Any, what: str) -> dict[Any, Any]:
    if not isinstance(value, list) or not value:
        raise RuleError(f"{what} must be a non-empty list of [key, value] pairs")
    pairs: dict[Any, Any] = {}
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise RuleError(f"{what} must be a list of [key, value] pairs")
        key, item = pair
        if not isinstance(key, (int, float, str)) or isinstance(key, bool):
            raise RuleError(f"{what}: key {key!r} must be a number or text")
        if key in pairs:
            raise RuleError(f"{what}: key {key!r} is given twice")
        pairs[key] = item
    return pairs


def parse_rule(data: Any, layer: str, set_id: str, source: str, key_check: re.Pattern[str]) -> Rule:
    _fields(data, "rule", {"id", "output", "inputs", "formula", "reason"},
            {"latch", "tables", "values", "units", "label", "source", "total"})  # fmt: skip
    rid = _text(data["id"], "rule id")
    what = f"rule {rid}"
    inputs = data["inputs"]
    if not isinstance(inputs, dict):
        raise RuleError(f"{what}: inputs must be an object of name to point key")
    for name, key in inputs.items():
        _name(name, f"{what}: input name")
        if not isinstance(key, str) or not key_check.match(key) or "[*]" in key:
            raise RuleError(f"{what}: input {name} {key!r} is not a point key")
    tables = {
        _name(n, f"{what}: table name"): _pairs(t, f"{what}: table {n}")
        for n, t in (data.get("tables") or {}).items()
    }
    formula = Formula.compile(data["formula"], f"{what} formula")
    latch = Formula.compile(data["latch"], f"{what} latch") if "latch" in data else None
    for part in (formula, latch):
        if part is not None:
            for table in _table_names(part.tree) - tables.keys():
                raise RuleError(f"{what}: lookup uses unknown table {table!r}")
    values = None
    if "values" in data:
        values = _pairs(data["values"], f"{what}: values")
        for description in values.values():
            _text(description, f"{what}: value description")
    names = formula.names | (latch.names if latch else frozenset())
    if latch is not None and LATCHED in latch.names:
        raise RuleError(f"{what}: latch cannot use 'latched'")
    if LATCHED in names and latch is None:
        raise RuleError(f"{what}: 'latched' needs a latch")
    total = data.get("total", False)
    if not isinstance(total, bool):
        raise RuleError(f"{what}: total must be true or false")
    return Rule(
        id=rid,
        output=_name(data["output"], f"{what}: output"),
        inputs=dict(inputs),
        formula=formula,
        latch=latch,
        tables=tables,
        values=values,
        units=_text(data["units"], f"{what}: units") if "units" in data else None,
        label=_text(data["label"], f"{what}: label") if "label" in data else None,
        reason=_text(data["reason"], f"{what}: reason"),
        source=_text(data.get("source", source), f"{what}: source"),
        layer=layer,
        set_id=set_id,
        constants=frozenset(names - inputs.keys() - {LATCHED}),
        total=total,
    )


def _table_names(tree: ast.AST) -> set[str]:
    return {
        node.args[0].id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "lookup"
        and isinstance(node.args[0], ast.Name)
    }


def find_loop(rules: Sequence[Rule]) -> list[str] | None:
    """The outputs in a dependency loop among ``rules``, or ``None``."""
    _, loop = _order(rules)
    return loop


def _order(rules: Sequence[Rule]) -> tuple[list[Rule], list[str] | None]:
    """Rules sorted so each comes after the rules it reads; and any loop found."""
    by_output = {r.output: r for r in rules}
    done: set[str] = set()
    visiting: list[str] = []
    order: list[Rule] = []
    loop: list[str] | None = None

    def visit(rule: Rule) -> None:
        nonlocal loop
        if rule.output in done:
            return
        if rule.output in visiting:
            loop = loop or visiting[visiting.index(rule.output) :]
            return
        visiting.append(rule.output)
        for dep in sorted(rule.depends_on()):
            if dep in by_output:
                visit(by_output[dep])
        visiting.pop()
        done.add(rule.output)
        order.append(rule)

    for rule in rules:
        visit(rule)
    return order, loop


def _loops(rules: Sequence[Rule]) -> set[str]:
    """Outputs of rules that are in a dependency loop."""
    by_output = {r.output: r for r in rules}
    return {
        rule.output
        for rule in rules
        if any(rule.output in _reach(by_output, dep) for dep in rule.depends_on())
    }


def _reach(by_output: Mapping[str, Rule], start: str) -> set[str]:
    seen: set[str] = set()
    stack = [start]
    while stack:
        output = stack.pop()
        if output in seen or output not in by_output:
            continue
        seen.add(output)
        stack.extend(by_output[output].depends_on())
    return seen


# ----- choosing by layer, and running -----------------------------------------


def choose(
    items: Iterable[Any], name_of: Callable[[Any], str], disabled: frozenset[str]
) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    """For each name, the highest-layer item that is switched on; and same-layer clashes.

    ``items`` must be in layer order, lowest first.
    """
    grouped: dict[str, list[Any]] = {}
    for item in items:
        if item.id not in disabled:
            grouped.setdefault(name_of(item), []).append(item)
    chosen: dict[str, Any] = {}
    clashes: dict[str, list[Any]] = {}
    for name, same in grouped.items():
        top = [i for i in same if i.layer == same[-1].layer]
        if len(top) > 1:
            clashes[name] = top
        else:
            chosen[name] = top[0]
    return chosen, clashes


class RuleEngine:
    """The constants and rules in use for one device."""

    def __init__(
        self,
        constants: Sequence[Constant],
        rules: Sequence[Rule],
        disabled: frozenset[str],
        fail: Callable[[str, str], None],
    ) -> None:
        self.all_constants = list(constants)
        self.all_rules = list(rules)
        self.disabled = disabled
        self._fail = fail
        self.constants, constant_clashes = choose(constants, lambda c: c.name, disabled)
        self.constant_clashes = constant_clashes
        chosen, rule_clashes = choose(rules, lambda r: r.output, disabled)
        self.rule_clashes = rule_clashes
        for group in (*constant_clashes.values(), *rule_clashes.values()):
            for item in group:
                others = ", ".join(i.id for i in group if i is not item)
                fail(item.id, f"clashes with {others} (same layer)")
        looped = _loops(list(chosen.values()))
        for output in sorted(looped):
            fail(chosen[output].id, f"is in a dependency loop through label.{output}")
        self.rules, _ = _order([r for o, r in chosen.items() if o not in looped])
        self.blocked = {f"label.{o}" for o in (*looped, *rule_clashes)}
        """Outputs that never have a value: clashing or looping rules."""
        self.latched: dict[str, bool] = {}
        self.errors: dict[str, str] = {}
        """The last runtime error of each rule, cleared when it next succeeds."""

    def evaluate(self, states: Mapping[str, PointState]) -> list[PointState]:
        """Run every rule in order; outputs are added to the inputs seen by later rules."""
        from .poller import PointState

        known: dict[str, PointState] = dict(states)
        out: list[PointState] = []
        for key in sorted(self.blocked):
            rule = next(r for r in self.all_rules if r.key == key)
            out.append(
                PointState(key, rule.output, rule.label, rule.units, False, None, "rule",
                           options=rule.options, total=rule.total)
            )  # fmt: skip
        for rule in self.rules:
            value, trace = self._run(rule, known)
            state = PointState(
                key=rule.key,
                name=rule.output,
                label=rule.label,
                units=rule.units,
                writable=False,
                value=value,
                sunspec_type="rule",
                quirks=(rule.id,),
                trace=trace,
                options=rule.options,
                total=rule.total,
            )
            known[rule.key] = state
            out.append(state)
        return out

    def _run(self, rule: Rule, known: Mapping[str, PointState]) -> tuple[Any, dict[str, Any]]:
        inputs: dict[str, Any] = {}
        constants: dict[str, Any] = {}
        trace: dict[str, Any] = {
            "rule": rule.id,
            "source": rule.source,
            "inputs": inputs,
            "constants": constants,
            "missing": None,
            "error": None,
        }

        def env(name: str) -> Any:
            if name in rule.inputs:
                key = rule.inputs[name]
                state = known.get(key)
                value = None if state is None else state.value
                inputs[name] = {"key": key, "value": _plain(value)}
                if value is None:
                    raise Missing(name)
                return value
            if name == LATCHED:
                return self.latched.get(rule.id, False)
            constant = self.constants.get(name)
            if constant is None:
                if name in self.constant_clashes:
                    raise EvalError(f"constant {name!r} clashes in one layer")
                raise EvalError(f"unknown constant {name!r}")
            constants[name] = {"value": constant.value, "units": constant.units,
                               "id": constant.id, "source": constant.source}  # fmt: skip
            return constant.value

        try:
            if rule.latch is not None and not self.latched.get(rule.id, False):
                try:
                    if rule.latch.evaluate(env, rule.tables):
                        self.latched[rule.id] = True
                        _LOGGER.info("Rule %s latched", rule.id)
                except Missing:
                    pass
            if rule.latch is not None:
                trace["latched"] = self.latched.get(rule.id, False)
            value = rule.formula.evaluate(env, rule.tables)
            if isinstance(value, bool):
                value = int(value)
            if rule.values is not None and value not in rule.values:
                raise EvalError(f"value {value!r} is not one of the rule's values")
        except Missing as missing:
            trace["missing"] = missing.name
            self._clear(rule)
            return None, trace
        except EvalError as err:
            trace["error"] = str(err)
            if self.errors.get(rule.id) != str(err):
                _LOGGER.warning("Rule %s gave no value: %s", rule.id, err)
            self.errors[rule.id] = str(err)
            return None, trace
        self._clear(rule)
        if rule.values is not None:
            trace["description"] = rule.values[value]
        return value, trace

    def _clear(self, rule: Rule) -> None:
        if self.errors.pop(rule.id, None) is not None:
            _LOGGER.info("Rule %s gives a value again", rule.id)

    def state_of(self, item: Constant | Rule, failing: Mapping[str, str]) -> str:
        if item.id in self.disabled:
            return "off"
        if item.id in failing or item.id in self.errors:
            return "failing"
        chosen = self.constants.values() if isinstance(item, Constant) else self.rules
        return "active" if item in chosen else "overridden"


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return {"value": int(value.value), "name": value.name}
    return value
