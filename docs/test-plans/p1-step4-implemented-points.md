# Test plan: P1 step 4, discover implemented points (D6, without a PICS)

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that modbus-bridge can:

1. read the chain several times and sort every point into implemented or not implemented (D6.4),
2. show only implemented points,
3. show an implemented point with no value as unavailable (D6.2),
4. list the not-implemented points separately, on request,
5. show a SunSpec string that is all zeros as not set, never as an empty value.

Loading a PICS (D6.3) is the next step, not this one.

## 2. Setup

1. The project `.venv`, as in step 3.
2. The emulator at tag v0.2.3 (commit af7bc62), in its own scratch virtual environment.
3. One emulator instance:
   `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`
4. Only one Modbus client at a time (rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: (a) a point with a value on any read is implemented; (b) a point with no value on every read is not implemented; (c) a point in a model that failed on every read is in neither set, and the model is reported; (d) an implemented point with no value now shows "unavailable"; (e) an all-zero string is `None`. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator (setup 3) | Listens on 127.0.0.1:5120 | Does not start |
| T4 | `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5120 --unit 1 --points --reads 3 --interval 2` | Exit code 0. A summary line gives the implemented and not-implemented counts, and they add up to 642, the point count from step 3's run | Error, or counts that do not add up |
| T5 | Same as T4, plus `--show-not-implemented` | The not-implemented list appears, and none of its points appear among the readings | Overlap, or the list is missing |
| T6 | Check T4's readings | No line shows "unavailable" for a point that had a value on any read | Any such line |
| T7 | Stop the emulator and check port 5120 is free | Free | Still running |

Step 3's 642 points are the sum of its per-model counts: 6 + 60 + 42 + 9 + 45 + 59 + 24 + 4 × 73 + 21 + 40 + 5 + 17 + 5 + 17.

## 4. Not covered

1. Loading a PICS (next step).
2. A point that only gets a value at some times of day. The emulator run is short, so the "later becomes implemented" rule (D6.4) is tested by unit test only.
3. Keeping the discovered result between runs.
4. Publishing to Home Assistant.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, pytest 9.2.0 and ruff 0.17.3. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `126 passed`, including the 5 new tests (a)–(e) |
| T2 | Pass | `All checks passed!`, no files to reformat |
| T3 | Pass | Listening on 127.0.0.1:5120 |
| T4 | Pass | Exit code 0. `Points: 419 implemented, 223 not implemented (discovered over 3 reads)`. 419 + 223 = 642. All 17 models read. |
| T5 | Pass | 419 points shown, 223 listed as not implemented, no key in both |
| T6 | Pass | No line shows "(unavailable)". Every shown point had a value. |
| T7 | Pass | Port 5120 free after the stop |

Points per model after sorting (step 3 count in brackets): 1: 6 (6), 701: 58 (60), 702: 25 (42), 703: 7 (9), 704: 18 (45), 705: 56 (59), 706: 21 (24), 707: 39 (73), 708: 39 (73), 709: 29 (73), 710: 29 (73), 711: 16 (21), 712: 37 (40), 713: 5 (5), 714: 17 (17), 715: 5 (5), 502: 12 (17).

Examples of not-implemented points: 701.ThrotPct, 701.ThrotSrc, 702.AMax, 502.Ctl, 502.InWh.
