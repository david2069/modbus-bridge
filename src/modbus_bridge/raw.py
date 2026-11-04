"""Raw register readings defined as data in quirk sets (design 1.2, 1.4).

A reading names a register address, table, type, word order, scale and units.
It is published as point ``raw.<name>``. A failed read, a raw value listed as
unavailable, or a NaN gives no value, never 0 or a guess (rule 8).
"""

from __future__ import annotations

import math
import re
import struct
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from modbus_connection import ModbusExceptionError, ModbusUnit

#: Registers per read (the Modbus limit for function codes 3 and 4).
MAX_BLOCK = 125
TABLES = ("holding", "input")
#: Type: (registers, struct format).
TYPES: dict[str, tuple[int, str]] = {
    "uint16": (1, ">H"),
    "int16": (1, ">h"),
    "uint32": (2, ">I"),
    "int32": (2, ">i"),
    "uint64": (4, ">Q"),
    "int64": (4, ">q"),
    "float32": (2, ">f"),
}
_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_FIELDS_REQUIRED = {"id", "name", "reason", "address", "type"}
_FIELDS_OPTIONAL = {"source", "table", "word_order", "scale", "invert", "units", "label",
                    "unavailable", "total"}  # fmt: skip


class RawReadingError(ValueError):
    """A raw reading in a quirk set is not valid."""


@dataclass(frozen=True)
class RawReading:
    id: str
    name: str
    reason: str
    source: str
    layer: str
    set_id: str
    address: int
    type: str
    table: str = "holding"
    word_order: str = "big"
    scale: float = 1
    invert: bool = False
    units: str | None = None
    label: str | None = None
    unavailable: frozenset[float] = field(default_factory=frozenset)
    total: bool = False
    """The value only counts up over the device's life (a lifetime energy total)."""

    @property
    def key(self) -> str:
        return f"raw.{self.name}"

    @property
    def count(self) -> int:
        return TYPES[self.type][0]

    def describe(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "point": self.key,
            "set": self.set_id,
            "layer": self.layer,
            "table": self.table,
            "address": self.address,
            "type": self.type,
            "word_order": self.word_order,
            "scale": self.scale,
            "invert": self.invert,
            "units": self.units,
            "label": self.label,
            "unavailable": sorted(self.unavailable),
            "total": self.total,
            "reason": self.reason,
            "source": self.source,
        }

    def decode(self, registers: Sequence[int]) -> Any:
        """The value from this reading's registers, or ``None`` for no value."""
        if len(registers) != self.count:
            raise RawReadingError(f"{self.id}: expected {self.count} registers")
        words = list(registers) if self.word_order == "big" else list(reversed(registers))
        raw = struct.unpack(TYPES[self.type][1], struct.pack(f">{self.count}H", *words))[0]
        if isinstance(raw, float) and math.isnan(raw):
            return None
        if raw in self.unavailable:
            return None
        value = raw if self.scale == 1 else round(raw * self.scale, 9)
        return -value if self.invert else value


def parse_reading(data: Any, layer: str, set_id: str, source: str) -> RawReading:
    """One reading from a quirk-set file."""
    if not isinstance(data, dict):
        raise RawReadingError("reading must be an object")
    missing = _FIELDS_REQUIRED - data.keys()
    unknown = data.keys() - _FIELDS_REQUIRED - _FIELDS_OPTIONAL
    rid = data.get("id")
    if missing:
        raise RawReadingError(f"reading {rid!r} is missing {', '.join(sorted(missing))}")
    if unknown:
        raise RawReadingError(f"reading {rid!r} has unknown field(s) {', '.join(sorted(unknown))}")

    def text(name: str, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RawReadingError(f"reading {rid!r}: {name} must be non-empty text")
        return value

    name = data["name"]
    if not isinstance(name, str) or not _NAME.match(name):
        raise RawReadingError(f"reading {rid!r}: name must be lower case letters, digits and _")
    address = data["address"]
    if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address <= 65535:
        raise RawReadingError(f"reading {rid!r}: address must be 0 to 65535")
    rtype = data["type"]
    if rtype not in TYPES:
        raise RawReadingError(f"reading {rid!r}: type must be one of {', '.join(TYPES)}")
    if address + TYPES[rtype][0] > 65536:
        raise RawReadingError(f"reading {rid!r}: registers run past 65535")
    table = data.get("table", "holding")
    if table not in TABLES:
        raise RawReadingError(f"reading {rid!r}: table must be holding or input")
    word_order = data.get("word_order", "big")
    if word_order not in ("big", "little"):
        raise RawReadingError(f"reading {rid!r}: word_order must be big or little")
    scale = data.get("scale", 1)
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or scale == 0:
        raise RawReadingError(f"reading {rid!r}: scale must be a non-zero number")
    invert = data.get("invert", False)
    if not isinstance(invert, bool):
        raise RawReadingError(f"reading {rid!r}: invert must be true or false")
    unavailable = data.get("unavailable", [])
    if not isinstance(unavailable, list) or any(
        isinstance(v, bool) or not isinstance(v, (int, float)) for v in unavailable
    ):
        raise RawReadingError(f"reading {rid!r}: unavailable must be a list of numbers")
    total = data.get("total", False)
    if not isinstance(total, bool):
        raise RawReadingError(f"reading {rid!r}: total must be true or false")
    return RawReading(
        id=text("id", rid),
        name=name,
        reason=text("reason", data["reason"]),
        source=text("source", data.get("source", source)),
        layer=layer,
        set_id=set_id,
        address=address,
        type=rtype,
        table=table,
        word_order=word_order,
        scale=scale,
        invert=invert,
        units=text("units", data["units"]) if "units" in data else None,
        label=text("label", data["label"]) if "label" in data else None,
        unavailable=frozenset(unavailable),
        total=total,
    )


@dataclass(frozen=True)
class Block:
    table: str
    address: int
    count: int
    readings: tuple[RawReading, ...]


def plan_blocks(readings: Sequence[RawReading]) -> list[Block]:
    """Group readings whose registers touch or overlap into reads of up to 125 registers."""
    blocks: list[Block] = []
    for reading in sorted(readings, key=lambda r: (r.table, r.address, r.count)):
        end = reading.address + reading.count
        if blocks:
            last = blocks[-1]
            last_end = last.address + last.count
            new_end = max(last_end, end)
            if (
                last.table == reading.table
                and reading.address <= last_end
                and new_end - last.address <= MAX_BLOCK
            ):
                blocks[-1] = Block(
                    last.table, last.address, new_end - last.address, (*last.readings, reading)
                )
                continue
        blocks.append(Block(reading.table, reading.address, reading.count, (reading,)))
    return blocks


async def _read(unit: ModbusUnit, table: str, address: int, count: int) -> list[int]:
    if table == "input":
        return await unit.read_input_registers(address, count)
    return await unit.read_holding_registers(address, count)


@dataclass(frozen=True)
class RawResult:
    value: Any
    error: str | None = None


async def read_raw(unit: ModbusUnit, readings: Sequence[RawReading]) -> dict[str, RawResult]:
    """Read every reading once; the result is keyed by reading id.

    A Modbus exception on a block makes each of its readings be read alone, so
    one bad address does not hide its neighbours. Other Modbus errors (e.g. a
    lost connection) are raised to the caller.
    """
    results: dict[str, RawResult] = {}
    for block in plan_blocks(readings):
        try:
            registers = await _read(unit, block.table, block.address, block.count)
        except ModbusExceptionError as err:
            if len(block.readings) > 1:
                for reading in block.readings:
                    results |= await read_raw(unit, [reading])
                continue
            [reading] = block.readings
            results[reading.id] = RawResult(None, _error(block, err))
            continue
        for reading in block.readings:
            start = reading.address - block.address
            results[reading.id] = RawResult(
                reading.decode(registers[start : start + reading.count])
            )
    return results


def _error(block: Block, err: Exception) -> str:
    return f"{block.table} read at {block.address} (count {block.count}): {err}"


def by_name(readings: Sequence[RawReading]) -> Mapping[str, list[RawReading]]:
    """Readings grouped by name, in the order given."""
    grouped: dict[str, list[RawReading]] = {}
    for reading in readings:
        grouped.setdefault(reading.name, []).append(reading)
    return grouped
