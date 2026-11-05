"""Run the REST API for one device.

Usage:
    python -m modbus_bridge.serve --device-host 192.0.2.10 --device-port 502 --unit 1
        --token-file PATH [--pics PROFILE.json] [--interval 5]
        [--quirks FILE_OR_DIR ...] [--quirk-off ID ...] [--user-quirks DIR]
        [--listen-host 127.0.0.1] [--listen-port 8080] [--device-id unit1]

The API token is read from a file, never from the command line, so it does not
show in the process list.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from .api import create_app
from .pics import PicsProfile
from .quirks import QuirkError, check_off, check_unique, load_sets
from .service import DeviceService
from .user_quirks import UserQuirkStore


def build(args: argparse.Namespace) -> FastAPI:
    tokens = [line.strip() for line in args.token_file.read_text().splitlines() if line.strip()]
    profile = PicsProfile.load(args.pics) if args.pics else None
    quirk_sets = load_sets(args.quirks)
    check_off(quirk_sets, args.quirk_off)
    connection = ModbusConnection(
        ModbusTcpParams(host=args.device_host, port=args.device_port), timeout=args.timeout
    )
    device_id = args.device_id or f"unit{args.unit}"
    user_store = None
    if args.user_quirks is not None:
        # Check the saved user quirks now, so a bad file stops start-up with a clear error.
        user_store = UserQuirkStore(args.user_quirks, device_id)
        user_set = user_store.load().quirk_set(device_id, "any")
        check_unique([*quirk_sets, *([user_set] if user_set else [])])
    service = DeviceService(
        device_id,
        connection.for_unit(args.unit),
        interval=args.interval,
        profile=profile,
        quirk_sets=quirk_sets,
        quirks_off=args.quirk_off,
        user_store=user_store,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        await connection.connect()
        try:
            await service.setup()
            service.start()
            yield
        finally:
            await service.stop()
            await connection.close()

    return create_app({service.device_id: service}, tokens, lifespan=lifespan)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device-host", required=True)
    parser.add_argument("--device-port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--device-id", help="id used in API paths (default: unit<N>)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Modbus request timeout")
    parser.add_argument("--pics", type=Path, help="a PICS profile from scripts/convert_pics.py")
    parser.add_argument("--interval", type=float, default=5.0, help="seconds between polls")
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument(
        "--quirks", type=Path, action="append", default=[],
        help="a quirk-set file, or a directory of them (repeatable)",
    )  # fmt: skip
    parser.add_argument(
        "--quirk-off", action="append", default=[], metavar="ID",
        help="switch off the quirk with this id (repeatable)",
    )  # fmt: skip
    parser.add_argument(
        "--user-quirks", type=Path, metavar="DIR",
        help="directory for the user's own quirks, one file per device (off if not given)",
    )  # fmt: skip
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=8080)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        app = build(args)
    except QuirkError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 2
    uvicorn.run(app, host=args.listen_host, port=args.listen_port, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
