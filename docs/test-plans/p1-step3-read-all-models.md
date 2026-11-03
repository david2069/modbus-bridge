# Test plan: P1 step 3, read every model's points with standard SunSpec names

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that modbus-bridge can:

1. read every model in the chain, using the official SunSpec definitions (sunspec/models, Apache-2.0, pinned commit, see `src/modbus_bridge/sunspec_models/SOURCE.md`),
2. name each point with its standard SunSpec name, label and units,
3. apply scale factors,
4. show a value the device does not report as missing (rule 8),
5. show a model it cannot read as not read, with the reason, without stopping the other models.

## 2. Setup

1. The project `.venv`, as in step 2.
2. The emulator at tag v0.2.3 (commit af7bc62), in its own scratch virtual environment, as in step 2.
3. One emulator instance:
   `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`
4. Only one Modbus client at a time (rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. Includes: (a) every point of every generated model maps to one generated field; (b) model 713 from fake registers gives the right scaled values, names and units; (c) an unreported value is `None`; (d) a model without a definition is "not read" with a reason; (e) a model the device refuses is "not read" while the next model is still read; (f) a repeated model gets the key `N#2`. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Regenerate with `scripts/generate_sunspec_models.py` from sunspec/models at the pinned commit, then `git status` | No changes to the generated files | Any change |
| T4 | Start the emulator (setup 3) | Listens on 127.0.0.1:5120 | Does not start |
| T5 | `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5120 --unit 1 --points` | All 17 models read, none "NOT READ", exit code 0 | Any model not read, error, or traceback |
| T6 | Check values in T5 are plausible: 713 SoC 0–100 Pct; 701 Hz 45–65 Hz; 701 LNV 100–300 V; 701 InvSt shows a symbol name | All plausible | Any implausible |
| T7 | Stop the emulator and check port 5120 is free | Free | Still running |

## 4. Not covered

1. Whether each value matches what the emulator meant to send. T6 checks only plausibility.
2. A second SunSpec device (needed for P1 done-when, a later step).
3. Writing any point.
4. Repeated polling and connection loss.
5. Model 63001, which the generator cannot express. It would show as "not read".
6. Publishing to Home Assistant or anything else.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, pytest 9.2.0 and ruff 0.17.3. Emulator v0.2.3 (commit af7bc62). sunspec/models commit 90b4a331.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `121 passed`: 111 mapping tests (one per generated model), plus catalogue size, 713 values, no definition, refused model, repeated model, and the step 2 tests |
| T2 | Pass | `All checks passed!`, no files to reformat. The generated folder is excluded from ruff and kept exactly as generated. |
| T3 | Pass | Regenerating gave files identical to the previous output (`diff -r`) |
| T4 | Pass | Listening on 127.0.0.1:5120 |
| T5 | Pass | Exit code 0. All 17 models read and none "NOT READ": 1 (6 points), 701 (60), 702 (42), 703 (9), 704 (45), 705 (59), 706 (24), 707–710 (73 each), 711 (21), 712 (40), 713 (5), 714 (17), 715 (5), 502 (17). 223 points show as `(missing)`. |
| T6 | Pass | 713 SoC `40.0 Pct`; 701 Hz `49.99 Hz`; 701 LNV `241.8 V`; 701 InvSt `3 (RUNNING)` |
| T7 | Pass | Port 5120 free, no emulator `serve` process left |

Notes:

1. In models 707–710, the generator merges the MustTrip, MayTrip and MomCess groups into one. They are shown under their own SunSpec names, e.g. `707.Crv[1].MustTrip[1].Pt[1].V`.
2. The mapping from SunSpec names to generated fields uses modbus-connection's private `_snake` function. T1(a) fails if a library update changes it.
