"""A made-up SunSpec solar inverter over Modbus TCP, for tests only.

Usage: python scripts/sunspec_sim.py [--host 127.0.0.1] [--port 5121]

The register map is built from the official SunSpec model files bundled in
``modbus_bridge.sunspec_models`` (models 1, 103, 120 and 160 with 2 modules).
The identity is a placeholder; it is not any real maker's device. Points with
no value set give SunSpec's "not implemented" value for their type. Only
function 3 (read holding registers) is answered.
"""

from __future__ import annotations

import argparse
import asyncio
import math
import struct
import time
from collections.abc import Callable, Mapping
from typing import Any

from modbus_bridge.sunspec_models import definition

BASE_ADDRESS = 40000
MODULES = 2

#: "Not implemented" value for each SunSpec type, as registers.
_NOT_IMPLEMENTED: dict[str, tuple[int, ...]] = {
    "int16": (0x8000,),
    "sunssf": (0x8000,),
    "pad": (0x8000,),
    "uint16": (0xFFFF,),
    "enum16": (0xFFFF,),
    "bitfield16": (0xFFFF,),
    "count": (0x0000,),
    "acc16": (0x0000,),
    "int32": (0x8000, 0x0000),
    "uint32": (0xFFFF, 0xFFFF),
    "enum32": (0xFFFF, 0xFFFF),
    "bitfield32": (0xFFFF, 0xFFFF),
    "acc32": (0x0000, 0x0000),
    "float32": (0x7FC0, 0x0000),
    "ipaddr": (0x0000, 0x0000),
    "int64": (0x8000, 0, 0, 0),
    "uint64": (0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF),
    "acc64": (0, 0, 0, 0),
    "eui48": (0xFFFF,) * 4,
    "ipv6addr": (0,) * 8,
}

_STRUCT: dict[str, str] = {
    "int16": ">h",
    "sunssf": ">h",
    "uint16": ">H",
    "enum16": ">H",
    "bitfield16": ">H",
    "count": ">H",
    "acc16": ">H",
    "int32": ">i",
    "uint32": ">I",
    "enum32": ">I",
    "bitfield32": ">I",
    "acc32": ">I",
    "float32": ">f",
    "int64": ">q",
    "uint64": ">Q",
    "acc64": ">Q",
}


def encode(sunspec_type: str, size: int, value: Any) -> list[int]:
    """Registers for one point; ``None`` gives the "not implemented" value."""
    if sunspec_type == "string":
        raw = b"" if value is None else str(value).encode("ascii")
        if len(raw) > size * 2:
            raise ValueError(f"string {value!r} longer than {size} registers")
        raw = raw.ljust(size * 2, b"\0")
        return list(struct.unpack(f">{size}H", raw))
    if value is None:
        return list(_NOT_IMPLEMENTED[sunspec_type])
    fmt = _STRUCT.get(sunspec_type)
    if fmt is None:
        raise ValueError(f"no encoder for SunSpec type {sunspec_type!r}")
    raw = struct.pack(fmt, value)
    return list(struct.unpack(f">{len(raw) // 2}H", raw))


def _group(
    group: Mapping[str, Any], values: Mapping[str, Any], prefix: str, counts: Mapping[str, int]
) -> list[int]:
    regs: list[int] = []
    for point in group["points"]:
        name = point["name"]
        regs += encode(point["type"], point["size"], values.get(f"{prefix}{name}"))
    for child in group.get("groups", []):
        count = child.get("count", 1)
        if isinstance(count, str) or count == 0:  # 0: repeats to fill the model length
            count = counts[f"{prefix}{child['name']}"]
        for index in range(1, count + 1):
            regs += _group(child, values, f"{prefix}{child['name']}[{index}].", counts)
    return regs


def build_model(model_id: int, values: Mapping[str, Any], counts: Mapping[str, int]) -> list[int]:
    """Registers for one model, including ID and L. ``values`` holds raw (unscaled) values."""
    body = _group(definition(model_id)["group"], {**values, "ID": model_id, "L": 0}, "", counts)
    body[1] = len(body) - 2
    return body


def build_map(models: list[tuple[int, Mapping[str, Any], Mapping[str, int]]]) -> list[int]:
    """The whole SunSpec map from the base address: marker, models, end model."""
    regs = [0x5375, 0x6E53]  # "SunS"
    for model_id, values, counts in models:
        regs += build_model(model_id, values, counts)
    return regs + [0xFFFF, 0]


IDENTITY = {
    "Mn": "ExampleSolar",
    "Md": "SimInverter 5000",
    "Vr": "1.0.0",
    "SN": "SIM-0000-0001",
    "DA": 1,
}


def inverter_models(t: float) -> list[tuple[int, Mapping[str, Any], Mapping[str, int]]]:
    """The made-up inverter at time ``t`` (seconds). Power follows a slow wave."""
    w = round(3000 + 1500 * math.sin(t / 30))
    mppt_w = [w * 55 // 100, w - w * 55 // 100]
    energy = 1_234_000 + int(t * 1.25)
    m103 = {
        "A_SF": -1, "A": round(w / 230 * 10), "AphA": round(w / 690 * 10),
        "AphB": round(w / 690 * 10), "AphC": round(w / 690 * 10),
        "V_SF": 0, "PPVphAB": 400, "PPVphBC": 400, "PPVphCA": 400,
        "PhVphA": 230, "PhVphB": 231, "PhVphC": 229,
        "W_SF": 0, "W": w, "Hz_SF": -2, "Hz": 5000, "VA_SF": 0, "VA": w,
        "VAr_SF": 0, "VAr": 0, "PF_SF": 0, "PF": 100, "WH_SF": 0, "WH": energy,
        "DCA_SF": -1, "DCA": round(sum(mppt_w) / 380 * 10), "DCV_SF": 0, "DCV": 380,
        "DCW_SF": 0, "DCW": sum(mppt_w) + 60, "Tmp_SF": 0, "TmpCab": 35,
        "St": 4, "Evt1": 0, "Evt2": 0,
    }  # fmt: skip
    m120 = {"DERTyp": 4, "WRtg_SF": 0, "WRtg": 5000, "VARtg_SF": 0, "VARtg": 5000,
            "ARtg_SF": 0, "ARtg": 24}  # fmt: skip
    m160: dict[str, Any] = {"DCA_SF": -2, "DCV_SF": -1, "DCW_SF": 0, "DCWH_SF": 0,
                            "Evt": 0, "N": MODULES}  # fmt: skip
    for i, pw in enumerate(mppt_w, start=1):
        p = f"module[{i}]."
        m160 |= {
            f"{p}ID": i, f"{p}IDStr": f"MPPT {i}", f"{p}DCA": round(pw / 380 * 100),
            f"{p}DCV": 3800, f"{p}DCW": pw, f"{p}DCWH": energy // 2, f"{p}DCSt": 4,
            f"{p}DCEvt": 0,
        }  # fmt: skip
    return [(1, IDENTITY, {}), (103, m103, {}), (120, m120, {}), (160, m160, {"module": MODULES})]


def extra_registers(t: float) -> dict[int, int]:
    """Made-up registers outside SunSpec, for raw-reading tests (``--extra``).

    1000 mode (uint16, 2); 1001-1002 power (int32, low word first, negative and
    changing); 1003 always 65535; 1004-1005 energy (uint32, high word first).
    Nothing at 1006 or above.
    """
    power = -round(1000 + 500 * math.sin(t / 5))
    low, high = struct.unpack(">HH", struct.pack(">i", power))[::-1]
    energy = 500_000 + int(t)
    return {
        1000: 2,
        1001: low,
        1002: high,
        1003: 0xFFFF,
        1004: energy >> 16,
        1005: energy & 0xFFFF,
    }


class SunSpecSimulator:
    """Serve a register map over Modbus TCP (function 3 only)."""

    def __init__(
        self,
        models: Callable[[float], list[tuple[int, Mapping[str, Any], Mapping[str, int]]]],
        extra: Callable[[float], Mapping[int, int]] | None = None,
    ) -> None:
        self._models = models
        self._extra = extra
        self._start = time.monotonic()

    def registers(self) -> list[int]:
        return build_map(self._models(time.monotonic() - self._start))

    def _extra_block(self, address: int, count: int) -> list[int] | None:
        if self._extra is None:
            return None
        values = self._extra(time.monotonic() - self._start)
        if all(a in values for a in range(address, address + count)):
            return [values[a] for a in range(address, address + count)]
        return None

    def answer(self, unit: int, pdu: bytes) -> bytes:
        function = pdu[0]
        if function != 3 or len(pdu) != 5:
            return bytes([function | 0x80, 1])  # illegal function
        address, count = struct.unpack(">HH", pdu[1:5])
        if not 1 <= count <= 125:
            return bytes([0x83, 3])  # illegal data value
        regs = self.registers()
        offset = address - BASE_ADDRESS
        if 0 <= offset and offset + count <= len(regs):
            block = regs[offset : offset + count]
        else:
            block = self._extra_block(address, count)
            if block is None:
                return bytes([0x83, 2])  # illegal data address
        data = struct.pack(f">{count}H", *block)
        return bytes([3, len(data)]) + data

    async def _client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while True:
                header = await reader.readexactly(7)
                tid, pid, length, unit = struct.unpack(">HHHB", header)
                pdu = await reader.readexactly(length - 1)
                reply = self.answer(unit, pdu)
                writer.write(struct.pack(">HHHB", tid, pid, len(reply) + 1, unit) + reply)
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            writer.close()

    async def start(self, host: str, port: int) -> asyncio.Server:
        return await asyncio.start_server(self._client, host, port)


async def _serve(host: str, port: int, extra: bool) -> None:
    sim = SunSpecSimulator(inverter_models, extra_registers if extra else None)
    server = await sim.start(host, port)
    print(f"SunSpec simulator on {host}:{port} (base {BASE_ADDRESS})", flush=True)
    async with server:
        await server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5121)
    parser.add_argument("--extra", action="store_true", help="serve made-up registers 1000-1005")
    args = parser.parse_args(argv)
    try:
        asyncio.run(_serve(args.host, args.port, args.extra))
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
