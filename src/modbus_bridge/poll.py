"""Command line poller: discover one unit, then poll it and print what changed.

Usage: python -m modbus_bridge.poll --host 192.0.2.10 --port 502 --unit 1
       [--pics PROFILE.json] [--interval 5] [--polls 10]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.model.sunspec import SunSpecError
from modbus_connection.tmodbus import ModbusConnection

from .implemented import discover_implemented
from .pics import PicsProfile, apply_pics
from .poller import Poller
from .probe import format_value
from .sunspec import discover

SHOW_CHANGES = 8


async def run(args: argparse.Namespace, profile: PicsProfile | None) -> None:
    connection = ModbusConnection(
        ModbusTcpParams(host=args.host, port=args.port), timeout=args.timeout
    )
    try:
        await connection.connect()
        unit = connection.for_unit(args.unit)
        device = await discover(unit)
        implemented, _ = await discover_implemented(unit, device.chain, args.reads, 1.0)
        if profile is not None:
            implemented, _ = apply_pics(implemented, profile)
        ident = device.identity
        print(f"Device: {ident.manufacturer} {ident.model} {ident.version}")
        print(f"Implemented points: {len(implemented.implemented)} ({implemented.source})")
        poller = Poller(unit, device.chain, implemented)
        for number in range(1, args.polls + 1):
            if number > 1:
                await asyncio.sleep(args.interval)
            changes = await poller.poll()
            status = f" FAILED: {poller.last_error}" if poller.last_error else ""
            print(f"Poll {number}: {len(changes)} changes{status}")
            for state in changes[:SHOW_CHANGES]:
                units = f" {state.units}" if state.units and state.available else ""
                print(f"  {state.key:<28} {format_value(state.value)}{units}")
            if len(changes) > SHOW_CHANGES:
                print(f"  ... and {len(changes) - SHOW_CHANGES} more")
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--pics", type=Path, help="a PICS profile from scripts/convert_pics.py")
    parser.add_argument("--reads", type=int, default=3, help="reads used to sort the points")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds between polls")
    parser.add_argument("--polls", type=int, default=10, help="number of polls, then stop")
    args = parser.parse_args(argv)
    profile = PicsProfile.load(args.pics) if args.pics else None
    try:
        asyncio.run(run(args, profile))
    except (ModbusError, SunSpecError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
