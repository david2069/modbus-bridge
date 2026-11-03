# Test plan: P1 step 1, repo skeleton

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that the empty `modbus_bridge` package installs, imports and passes lint.

## 2. Setup

1. Python 3.12 or later.
2. Make a fresh virtual environment in `.venv`: `python3.12 -m venv .venv`.
3. Install the package in development mode with the dev tools: `.venv/bin/pip install -e '.[dev]'`.

No emulator or device is used. Nothing talks to the network except pip.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest` | 1 test passes | Any test fails or errors |
| T2 | `.venv/bin/ruff check .` | No problems reported | Any problem reported |
| T3 | `.venv/bin/ruff format --check .` | No files to reformat | Any file would be reformatted |

## 4. Not covered

1. Any Modbus or SunSpec behaviour (P1 step 2 onwards).
2. Python versions other than the one used here.
3. CI, packaging for release, and Home Assistant.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, pytest 9.2.0 and ruff 0.17.3.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `1 passed` |
| T2 | Pass | `All checks passed!` |
| T3 | Pass | `7 files already formatted` |
