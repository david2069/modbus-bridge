# Test plan: P1 step 6b, keep enum values that SunSpec does not name

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

modbus-connection turns an enum value with no name in the SunSpec definition into `None` (it logs a warning). modbus-bridge then counts the point as not implemented. That is a silent fallback (rule 8). After this fix:

1. such a value is kept as its number, marked `UNKNOWN`, and logged once,
2. the point counts as implemented,
3. SunSpec's real "not implemented" value (0xFFFF for enum16) is still `None`.

## 2. Setup

1. The project `.venv`.
2. The emulator at tag v0.2.3 (commit af7bc62), one instance, as in step 6.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: (a) 713.Sta = 7, which model 713 does not name, gives `7 (UNKNOWN)` and is implemented; (b) 713.Sta = 0xFFFF gives `None`; (c) a named value is unchanged. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator, run `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5120 --unit 1 --points --pics src/modbus_bridge/pics_profiles/SM-000028.json`, then stop the emulator and check port 5120 is free | 502.Stat shows `0 (UNKNOWN)`; implemented is 422 and not implemented 220; no "has no mapping … decoding as None" warning; port free | Any of these not met |

## 4. Not covered

1. Bitfields. The library already keeps unknown bits.
2. Whether 0 for 502.Stat is a device quirk. That is for the P2 quirk layers.

## 5. Results

Run on 2026-11-03, same versions as step 6.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `142 passed`, including 3 new enum tests (a)–(c) |
| T2 | Pass | `All checks passed!` |
| T3 | Pass | `502.Stat  0 (UNKNOWN)`; `Points: 422 implemented, 220 not implemented`; the library's "decoding as None" warning no longer appears, ours does once: `Status: value 0 is not named in the SunSpec definition; kept`; port 5120 free afterwards |
