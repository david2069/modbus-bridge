# Test plan: P2 step 13, FranklinWH: 0xFFFF as no value, hide 714.DCA and 701.DERMode

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

Fix three gaps that give wrong data in HA today (rule 8), found in the study `docs/research/fwh-bridge-modbus.md` (G1–G3). The changes are data only, in `quirk_sets/franklinwh.json`:

1. **G1: 0xFFFF gives no value** on the uint16 readings for home load and reserves: 15506, 16000, 15508, 15509 and 16001 get `"unavailable": [65535]`. Today a 0xFFFF there shows as 65535 W or 65535 %. It also matters for N1: 65535 is not a multiple of 100, so one 0xFFFF on 16000 would make the rule trust 16000 from then on. The int16 PV readings (15502–15505) are left as they are, because -1 W can be a real reading at night; that needs measuring first.
2. **G2: hide 714.DCA and 714.Prt[n].DCA.** franklinwh-modbus-bridge measured them always at 0 on an aGate X (V10R01B04D00), although the PICS lists them as implemented. Today HA shows 0 A as a real current. The quirk says it is measured on V10R01B04D00 only, and can be switched off if an aGate reports a real current.
3. **G3: hide 701.DERMode.** The PICS (SM-000028) marks it unimplemented, but the device returns values, which franklinwh-modbus-bridge saw report "PV clipped" at night. Our PICS step keeps a point that gives a value, so it is published today (the emulator gives one too).

Each item names its source (rule 9) and can be switched off by its id.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 12.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile, as in step 12.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. 65535 on each of the five readings gives no value; 0 and a normal value still read;<br>2. the int16 PV readings are unchanged (0xFFFF still reads -1);<br>3. 65535 on 16000 does not make N1 trust 16000;<br>4. the two hide quirks match `714.DCA`, `714.Prt[1].DCA`, `714.Prt[2].DCA` and `701.DERMode`, and nothing else in 714 or 701;<br>5. each new item has a source and can be switched off. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API. Then:<br>1. `GET …/points`;<br>2. `GET …/quirks`;<br>3. `PUT …/quirks/fwh-q-dermode/off`, wait for the next poll, `GET …/points` again. | 1. No `714.DCA`, `714.Prt[1].DCA` or `701.DERMode` in the points; `714.DCW` and `701.Alrm` are still there; the five readings show normal values.<br>2. The quirks report lists both hide quirks with their sources.<br>3. After the switch-off, `701.DERMode` is back. | Any not met |
| T4 | Stop the API and emulator; check ports 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. 0xFFFF on the int16 PV readings (15502–15505) reads as -1 W. This is not known to be wrong: a small negative PV power at night is normal for many inverters (standby draw), and no evidence shows the aGate sends 0xFFFF there as "no value". Left as it is unless a measurement shows otherwise (study section 5).
2. 0xFFFF on the other uint16 readings (15500, 15501, 15507, 15016). Their rules already refuse unknown values (N5, R4, R5), but the raw readings `raw.*` still show 65535. The same fix applies; it is left for a separate yes.
3. The emulator does not send 0xFFFF, so G1 is tested by unit tests only.
4. 714.DCA on V12R02B60D00 firmware. If it gives a real current there, the hide should move to a firmware layer for V10.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 12. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `413 passed` (13 new in `tests/test_franklinwh_set.py`, covering items 1–5). The full run took about 31 s against 15 s before, because the machine was busy (load average 24); `tests/test_franklinwh_set.py` alone runs in 0.8 s. |
| T2 | Pass | `All checks passed!`, 72 files already formatted |
| T3 | Pass | 1. Points: `714.DCA`, `714.Prt[1].DCA` and `701.DERMode` absent; `714.DCW` 800 and `701.Alrm` 0 present; readings home load 800 / 766 W, reserves 20 / 20 / 20 %; `label.home_load_power` 766. 2. The quirks report lists `fwh-q-dca`, `fwh-q-dca-port` and `fwh-q-dermode` with their sources. 3. After `fwh-q-dermode` was switched off, `701.DERMode` was back with value 1 (`GRID_FOLLOWING`). |
| T4 | Pass | Ports 8120 and 5120 free; no traceback in either log; no new macOS crash report. |
