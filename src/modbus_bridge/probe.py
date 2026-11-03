"""Command line probe: find SunSpec on one unit and print Model 1 and the model chain.

Usage: python -m modbus_bridge.probe --host 192.0.2.10 --port 502 --unit 1 [--points]
       [--reads 3] [--interval 2] [--show-not-implemented] [--pics PROFILE.json]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from enum import Enum, Flag
from pathlib import Path

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.model.sunspec import SunSpecError
from modbus_connection.tmodbus import ModbusConnection

from .implemented import ImplementedPoints, discover_implemented, implemented_only
from .pics import PicsProfile, PicsReport, apply_pics
from .points import ModelReading
from .sunspec import SunSpecDevice, discover

#: Model 1 text the device left empty.
NOT_SET = "(not set)"
#: An implemented point that gave no value (design D6.2).
UNAVAILABLE = "(unavailable)"


def format_device(device: SunSpecDevice) -> str:
    """Return a plain-text report of a discovered device."""
    ident = device.identity

    def show(value: object) -> str:
        return NOT_SET if value is None else str(value)

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


def format_value(value: object) -> str:
    """Show a point's value; enums and flags by their SunSpec symbol names."""
    if value is None:
        return UNAVAILABLE
    if isinstance(value, Flag):
        names = [member.name for member in type(value) if member in value and member.value]
        return f"{int(value)} [{', '.join(names) or 'none set'}]"
    if isinstance(value, Enum):
        return f"{value.value} ({value.name})"
    return str(value)


def format_readings(
    readings: list[ModelReading], points: ImplementedPoints, show_not_implemented: bool
) -> str:
    """Return the implemented points, one per line, grouped by model."""
    lines = [
        f"Points: {len(points.implemented)} implemented,"
        f" {len(points.not_implemented)} not implemented ({points.source})"
    ]
    for reading in implemented_only(readings, points):
        header = f"Model {reading.prefix} at {reading.model.address}"
        if reading.error is not None:
            lines.append(f"{header}: NOT READ: {reading.error}")
            continue
        lines.append(f"{header}: {len(reading.points)} points")
        for point in reading.points:
            units = f" {point.units}" if point.units and point.value is not None else ""
            lines.append(f"  {point.key:<28} {format_value(point.value)}{units}")
    if show_not_implemented:
        lines.append(f"Not implemented ({len(points.not_implemented)}):")
        lines += [f"  {key}" for key in sorted(points.not_implemented)]
    return "\n".join(lines)


def format_pics_report(report: PicsReport) -> str:
    """List where the device and the PICS disagree."""
    sections = [
        ("Certified, no value (shown as unavailable)", report.certified_no_value),
        ("Value, not certified (now implemented)", report.value_not_certified),
        ("Not listed in the PICS (sorted by discovery)", report.not_in_pics),
        ("In the PICS, no point read (e.g. scale factors)", report.pics_only),
    ]
    lines = ["PICS comparison:"]
    for title, keys in sections:
        lines.append(f"  {title}: {len(keys)}")
        lines += [f"    {key}" for key in keys]
    return "\n".join(lines)


async def run(
    host: str,
    port: int,
    unit_id: int,
    request_timeout: float,
    reads: int | None,
    interval: float,
) -> tuple[SunSpecDevice, tuple[ImplementedPoints, list[ModelReading]] | None]:
    """Connect once, discover the device, and always close the connection.

    With ``reads``, also read the chain that many times and sort its points.
    """
    connection = ModbusConnection(ModbusTcpParams(host=host, port=port), timeout=request_timeout)
    try:
        await connection.connect()
        unit = connection.for_unit(unit_id)
        device = await discover(unit)
        found = None
        if reads is not None:
            found = await discover_implemented(unit, device.chain, reads, interval)
        return device, found
    finally:
        await connection.close()


def main(argv: list[str] | None = None) -> int:
    """Run the probe and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--points", action="store_true", help="also read every model's points")
    parser.add_argument("--reads", type=int, default=3, help="reads used to sort the points")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between reads")
    parser.add_argument(
        "--show-not-implemented", action="store_true", help="list the not-implemented points"
    )
    parser.add_argument("--pics", type=Path, help="a PICS profile from scripts/convert_pics.py")
    args = parser.parse_args(argv)
    profile = PicsProfile.load(args.pics) if args.pics else None
    try:
        device, found = asyncio.run(
            run(
                args.host,
                args.port,
                args.unit,
                args.timeout,
                args.reads if args.points else None,
                args.interval,
            )
        )
    except (ModbusError, SunSpecError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    print(format_device(device))
    if found is not None:
        points, readings = found
        report = None
        if profile is not None:
            points, report = apply_pics(points, profile)
        print(format_readings(readings, points, args.show_not_implemented))
        if report is not None:
            print(format_pics_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
