"""Convert a published SunSpec PICS spreadsheet into a modbus-bridge PICS profile.

Usage:
    .venv/bin/python scripts/convert_pics.py PICS.xlsx --source-url URL [--out DIR]

Only two things are read from the spreadsheet:

1. the product fields in ALLOWED_INFO from the "Certification Info" sheet, and
2. the per-model sheets (named by model id): each point and whether it is
   "unimplemented" or not.

Nothing else is read, so the test lab's contact details never reach the profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from modbus_bridge.pics import (  # noqa: E402
    PROFILE_FORMAT,
    PROFILE_VERSION,
    pics_path_to_key_path,
)

INFO_SHEET = "Certification Info"
#: Spreadsheet field name to profile field name. Nothing else is copied.
ALLOWED_INFO = {
    "Certificate Number": "certificate",
    "Certificate Issue Date": "issued",
    "Archive Location": "certificate_url",
    "Manufacturer Name": "manufacturer",
    "Product Name": "product_name",
    "Product Models": "product_models",
}
UNIMPLEMENTED = "unimplemented"
HEADER_POINTS = {"ID", "L"}


def _text(value: object) -> str:
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return str(value).strip()


def convert(path: Path, source_url: str) -> dict:
    """Return the profile for one PICS spreadsheet."""
    workbook = load_workbook(path, read_only=True, data_only=True)
    profile: dict = {"format": PROFILE_FORMAT, "version": PROFILE_VERSION}
    for row in workbook[INFO_SHEET].iter_rows(values_only=True):
        if row and row[0] is not None and _text(row[0]) in ALLOWED_INFO and len(row) > 1:
            if row[1] is not None:
                profile[ALLOWED_INFO[_text(row[0])]] = _text(row[1])
    if "certificate" not in profile:
        raise ValueError(f"{path}: no certificate number in {INFO_SHEET!r}")
    profile["source_url"] = source_url
    profile["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()

    models: dict[str, dict[str, list[str]]] = {}
    for sheet in workbook.worksheets:
        if not sheet.title.strip().isdigit():
            continue
        implemented: list[str] = []
        not_implemented: list[str] = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            address, point, _subvalue, value = (list(row) + [None] * 4)[:4]
            if address is None or point is None or not _text(point):
                continue  # an enum or bitfield symbol row, or blank
            name = _text(point)
            if name in HEADER_POINTS:
                continue
            if value is None or _text(value) == "":
                raise ValueError(f"{path}: model {sheet.title} point {name} has no value")
            target = not_implemented if _text(value).lower() == UNIMPLEMENTED else implemented
            target.append(pics_path_to_key_path(name))
        models[sheet.title.strip()] = {
            "implemented": implemented,
            "not_implemented": not_implemented,
        }
    profile["models"] = models
    return profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pics", type=Path)
    parser.add_argument("--source-url", required=True, help="where the PICS is published")
    parser.add_argument(
        "--out", type=Path, default=ROOT / "src" / "modbus_bridge" / "pics_profiles"
    )
    args = parser.parse_args(argv)
    profile = convert(args.pics, args.source_url)
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"{profile['certificate']}.json"
    target.write_text(json.dumps(profile, indent=1, ensure_ascii=False) + "\n")
    counts = {
        model: (len(entry["implemented"]), len(entry["not_implemented"]))
        for model, entry in profile["models"].items()
    }
    print(f"wrote {target.relative_to(ROOT)}: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
