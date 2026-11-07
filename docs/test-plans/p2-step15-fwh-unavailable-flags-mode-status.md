# Test plan: P2 step 15, FranklinWH: 0xFFFF as no value on 15500, 15501, 15507 and 15016

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

Finish G1 from the study `docs/research/fwh-bridge-modbus.md` for the uint16 readings left out of step 13 (its "not covered" item 2). Today a 0xFFFF on these registers is published as 65535 on the raw readings (rule 8):

| Reading | Address | Label rule that reads it |
|---|---|---|
| `raw.pv_local_installed` | 15500 | N5 |
| `raw.pv_remote_installed` | 15501 | N5 |
| `raw.operating_mode` | 15507 | N7, R5 |
| `raw.grid_status` | 15016 | N10, R4 |

The label rules already refuse 65535, as an unknown value. Only the raw readings are wrong.

The change is data only, in `quirk_sets/franklinwh.json`:

- each reading gets `"unavailable": [65535]`, with "0xFFFF gives no value" in its reason;
- each gets an explicit source naming franklinwh-modbus-bridge `poller.py` (commit f560db9), as in step 13.

No value is lost: 65535 is not a known flag, mode or status.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 14.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile, as in step 14.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. Tests changed or added:<br>1. 65535 on each of the four readings gives no value; 0 and a normal value still read; each has a source naming `poller.py`;<br>2. with no value on each of the four readings, its label rule gives no value and no error. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API, then `GET …/points` | The four raw readings and their labels show the emulator's normal values | Any missing or wrong |
| T4 | Stop the API and emulator; check ports 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. **0xFFFF on the int16 PV readings (15502–15505) still shows as -1 W.** This needs measuring first (study section 5).
2. The emulator does not send 0xFFFF, so the change is tested by unit tests only.
3. The other extension readings (15510–15513 energy, 15012–15013 and the ratings) are 32-bit or scaled. Whether the aGate sends all-ones there has not been seen in public evidence.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 14. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `424 passed` (item 1 extends the step 13 test to the four readings; item 2 adds 4 tests). With the data change taken out, the item 1 test failed; the change was then put back. The one warning is a deprecation notice from FastAPI's test client, not from this change. |
| T2 | Pass | `All checks passed!`, 75 files already formatted |
| T3 | Pass | `raw.pv_local_installed` 1, `raw.pv_remote_installed` 0, `raw.operating_mode` 2, `raw.grid_status` 2; labels: local solar 1 (Fitted), remote solar 0 (Not fitted), `self_consumption`, `on_grid`. |
| T4 | Pass | Ports 8120 and 5120 free; no traceback in either log. |
