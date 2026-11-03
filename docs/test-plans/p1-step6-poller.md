# Test plan: P1 step 6, the poller

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that modbus-bridge can keep one device's values up to date:

1. connect once, discover the device and its implemented points (PICS if given, otherwise discovery),
2. read the chain on a timer, keeping one snapshot of the implemented points only,
3. give a change event only when a value changes or a point becomes unavailable or available again,
4. on a failed read, mark the affected points unavailable, never keeping old values or giving 0 (rule 8),
5. promote a not-implemented point that starts giving a value (D6.4), with a change event.

## 2. Setup

1. The project `.venv`, as in step 5.
2. The emulator at tag v0.2.3 (commit af7bc62), one instance:
   `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`
3. Only one Modbus client at a time (rule 7). The poller holds the only connection.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests against the mock: (a) the first poll gives one event per implemented point; (b) an unchanged poll gives none; (c) a changed value gives one event; (d) a refused model makes its points unavailable, and they come back when it reads again; (e) a lost connection makes every point unavailable; (f) a promoted point appears with an event; (g) not-implemented points never appear. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator (setup 2) | Listens on 127.0.0.1:5120 | Does not start |
| T4 | `.venv/bin/python -m modbus_bridge.poll --host 127.0.0.1 --port 5120 --unit 1 --pics src/modbus_bridge/pics_profiles/SM-000028.json --interval 2 --polls 5` | Exit code 0. Poll 1 reports 421 events. Later polls report only changes, fewer than 421 each. | Error, or the same full count on every poll |
| T5 | Stop the emulator while a second run of T4 is polling (`--polls 10`) | The poller reports the failure, marks points unavailable with events, and exits cleanly when its polls run out. No traceback. | Hang, traceback, or old values kept |
| T6 | Check port 5120 is free | Free | Still running |

## 4. Not covered

1. The REST API and server-sent events (step 7).
2. Several devices, or several units on one connection.
3. Holding the last values for a few failed polls before showing unavailable (hilman2 does this). This step shows unavailable at once. Any grace period is a later, separate decision.
4. Energy-total guards (hilman2), which belong with the quirk layers in P2.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, pytest 9.2.0 and ruff 0.17.3. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `139 passed`, including 4 new poller tests covering (a)–(g) |
| T2 | Pass | `All checks passed!`, no files to reformat |
| T3 | Pass | Listening on 127.0.0.1:5120 |
| T4 | Pass | Exit code 0. Poll 1: 421 changes. Polls 2–5: 1 change each (713.WHAvail and 714.DCWhInj counting). |
| T5 | Pass, second attempt | Emulator stopped after poll 3. Poll 4: `419 changes FAILED: ModbusConnectionError: could not connect to 127.0.0.1:5120`, every point `(unavailable)`. Polls 5–10: 0 changes, each reporting the failure. Exit code 0, no traceback. 419 rather than 421 because 703.ESDlyRemTms and 703.ESRndTms were already unavailable. |
| T6 | Pass | Port 5120 free |

Notes:

1. The first T5 attempt was not valid. The poller's output was buffered, so it had finished all 10 polls before the emulator was stopped. It was rerun with `python -u` and `--timeout 2`.
2. Finding: the library logged `Field 'stat': Status has no mapping for value 0; decoding as None`. 502.Stat gives the value 0, which its SunSpec enum does not name, and the library turns it into `None`. modbus-bridge then counts the point as not implemented. This is a silent fallback (rule 8) and is fixed in a separate step.
