"""Command line probe: find SunSpec on one unit and print Model 1 and the model chain.

Usage: python -m modbus_bridge.probe --host 192.0.2.10 --port 502 --unit 1
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.model.sunspec import SunSpecError
from modbus_connection.tmodbus import ModbusConnection

from .sunspec import SunSpecDevice, discover

MISSING = "(missing)"


def format_device(device: SunSpecDevice) -> str:
    """Return a plain-text report of a discovered device."""
    ident = device.identity

    def show(value: object) -> str:
        return MISSING if value is None else str(value)

    lines = [
        f"SunSpec start: {device.base_address}",
        "Model 1:",
        f"  Mn  {show(ident.manufacturer)}",
        f"  Md  {show(ident.model)}",
        f"  Opt {show(ident.options)}",
        f"  Vr  {show(ident.version)}",
        f"  SN  {show(ident.serial)}",
        f"  DA  {show(ident.device_address)}",
        f"Model chain ({len(device.chain)} models):",
    ]
    lines += [
        f"  {model.model_id:>5}  at {model.address:>5}  length {model.length}"
        for model in device.chain
    ]
    return "\n".join(lines)


async def run(host: str, port: int, unit_id: int, request_timeout: float) -> SunSpecDevice:
    """Connect once, discover the device, and always close the connection."""
    connection = ModbusConnection(ModbusTcpParams(host=host, port=port), timeout=request_timeout)
    try:
        await connection.connect()
        return await discover(connection.for_unit(unit_id))
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    """Run the probe and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args(argv)
    try:
        device = asyncio.run(run(args.host, args.port, args.unit, args.timeout))
    except (ModbusError, SunSpecError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    print(format_device(device))
    return 0


if __name__ == "__main__":
    sys.exit(main())
