"""Regenerate src/modbus_bridge/sunspec_models from a checkout of sunspec/models.

Usage:
    git clone https://github.com/sunspec/models.git /path/to/sunspec-models
    git -C /path/to/sunspec-models checkout <commit>
    .venv/bin/python scripts/generate_sunspec_models.py /path/to/sunspec-models

It copies each json/model_N.json and generates a component module for it with
modbus-connection's SunSpec generator. A model the generator cannot express is
left out and listed in SOURCE.md.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "modbus_bridge" / "sunspec_models"
REPO_URL = "https://github.com/sunspec/models"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args(argv)
    checkout: Path = args.checkout
    commit = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    json_dir = TARGET / "json"
    gen_dir = TARGET / "generated"
    for folder in (json_dir, gen_dir):
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
    (gen_dir / "__init__.py").write_text('"""Generated SunSpec components. Do not edit."""\n')
    shutil.copyfile(checkout / "LICENSE", TARGET / "LICENSE")

    sources = sorted(
        (checkout / "json").glob("model_*.json"), key=lambda p: int(p.stem.split("_")[1])
    )
    generated: list[int] = []
    skipped: list[tuple[int, str]] = []
    for source in sources:
        model_id = int(source.stem.split("_")[1])
        out = gen_dir / f"model_{model_id}.py"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "modbus_connection.model.sunspec.generate",
                str(source),
                "-o",
                str(out),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            reason = (result.stderr.strip().splitlines() or ["unknown error"])[-1]
            skipped.append(
                (
                    model_id,
                    reason.split(": ", 1)[-1] if reason.lower().startswith("error: ") else reason,
                )
            )
            out.unlink(missing_ok=True)
            continue
        text = out.read_text()
        # The generator names the absolute path it read; keep only the repo path.
        text = text.replace(str(source), f"json/{source.name}")
        out.write_text(text)
        shutil.copyfile(source, json_dir / source.name)
        generated.append(model_id)

    lines = [
        "# SunSpec model definitions",
        "",
        f"- Source: <{REPO_URL}>, commit `{commit}`, folder `json/`.",
        "- Licence: Apache License 2.0, copied in `LICENSE` here.",
        "- `json/` holds the unmodified model files.",
        "- `generated/` is produced from them by `scripts/generate_sunspec_models.py`,",
        "  using modbus-connection's generator. Do not edit it by hand.",
        "",
        f"Generated: {len(generated)} models.",
        "",
        "Left out, because the generator cannot express them:",
        "",
        *(f"- Model {model_id}: {reason}" for model_id, reason in skipped),
        "",
    ]
    (TARGET / "SOURCE.md").write_text("\n".join(lines))
    print(f"generated {len(generated)}, skipped {len(skipped)}, commit {commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
