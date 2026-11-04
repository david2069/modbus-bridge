# Test plan: P2 step 4, the FranklinWH quirk set (N1–N11, R1–R5)

Status: run on 2026-11-04, all passed after one fix. Results are in section 5.

## 1. Purpose

Check the first real quirk set, `src/modbus_bridge/quirk_sets/franklinwh.json`. It is data only and comes from public sources:

- franklinwh-modbus, `docs/FRANKLINWH_MODBUS_EXTENSIONS.md`, commit `028498126d83c58facdd764b923fe644f3446147` (MIT). It provides the registers, types, units and the 15507 and 15016 values.
- hilman2/ha-sunspec2, `custom_components/sunspec2/vendors/franklinwh.py` and `franklinwh_controls.py`, commit `cb91e42205baba3d28cd4a381cf45e1e93b83c3e` (MIT). It provides R1–R3, the 50 W band, the 100 W step, the 1000 W and × 100 constants, and the signed PV powers.

The set is at the vendor layer and matches Mn `FranklinWH`. It holds:

1. Raw readings: 15500–15513, 15012–15013 (int32), 15016, 16000 and 16001.
2. Constants: `battery_idle_band_w` 50 W, `coarse_step_w` 100 W, `rating_min_plausible_w` 1000 W and `rating_scale_fix` 100.
3. Rules for the neutral labels:
   - N1 `home_load_power` (R2): uses 16000 once 16000 has shown a value that is not a multiple of 100 (latched); until then 15506.
   - N2 `solar_local_power` (15503).
   - N3 `solar_remote_power_1` and `_2` (15504, 15505).
   - N4 `solar_total_power` (15502).
   - N5 `solar_local_installed` and `solar_remote_installed` (15500, 15501). Only 0 (not fitted) and 1 (fitted) are accepted; any other value fails.
   - N6 `solar_energy_total` and `solar_local_energy` (15510–11, 15512–13).
   - N7 `battery_operating_mode` (R5): looks up 15507. 1 is `emergency_backup`, 2 `self_consumption`, 3 `time_of_use`.
   - N8 `battery_reserve_active`, `_self` and `_tou` (16001, 15508, 15509).
   - N9 `battery_inverter_state` (R1): `idle` if 701.InvSt is in {0, 1, 6, 7}; otherwise from 714.DCW with the ±50 W band.
   - N10 `grid_connection_status` (R4): looks up 15016. 1 is `restarting`, 2 `on_grid`, 3 `off_grid`, 6 `dispatch_active`. Every value is marked unconfirmed.
   - N11 `battery_power_fine` (15012–15013 as int32; negative means charging).
4. R3: `battery_charge_rating` and `battery_discharge_rating` from 702.WChaRteMaxRtg and 702.WDisChaRteMaxRtg. A value with 0 < v < 1000 is multiplied by 100.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) in its scratch virtual environment, one instance, started with `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`.
3. The API on 127.0.0.1:8120 as in P1 step 7 (`--pics src/modbus_bridge/pics_profiles/SM-000028.json --interval 2`), plus `--quirks src/modbus_bridge/quirk_sets/franklinwh.json`, with the scratch token file.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests check that:<br>1. the bundled file loads, matches `FranklinWH` and does not match another maker;<br>2. every N1–N11 label and the R3 outputs is present;<br>3. R1 gives idle, charging and discharging at the band edges and idle for each resting InvSt;<br>4. R2 uses the coarse value, latches on a fine value that is not a multiple of 100, then stays on the fine value;<br>5. R3 multiplies 160 to 16000 and leaves 5000 and 0 unchanged;<br>6. R4 and R5 handle each value, and an unknown value fails with no value;<br>7. N5 with 2 fails;<br>8. `--quirk-off` on an R rule removes its label. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and the API; `GET …/points` and `GET …/quirks` | 1. Every N1–N11 label and the R3 outputs are present, each with a trace.<br>2. Each label equals its raw register (and the SunSpec point, where one exists): `solar_total_power` = `raw.pv_total`, `solar_energy_total` = 502.OutWh, `battery_operating_mode` = `self_consumption` for 15507 = 2, `grid_connection_status` = `on_grid`, `battery_inverter_state` agrees with 701.InvSt and 714.DCW, `battery_charge_rating` = 5000.<br>3. Every item is `active`, and the log names each one with its source. | Any not met |
| T4 | Stop the API and emulator; check ports 5120 and 8120 are free | Both free | Either in use |

## 4. Not covered

1. Firmware differences. On V10R01B04D00, 15509 repeats 15508; on the aGate X (V10R11B40D00), 15508 and 15509 repeat 16001 and 16000 steps by 1000 W. They need firmware or model layers once public evidence is complete.
2. More than one model 714. hilman2 sums DCW over them; this set reads `714.DCW` only.
3. Grid status values other than 2. The emulator holds 15016 at 2 unless its islanded quirk is set; the other values are tested by unit test only.
4. The MQTT discovery check for text and true/false labels (left to the publisher step that handles label types).
5. Writes (P2W).
6. Label names are drafts until the owner's review (D3).

## 5. Results

Run on 2026-11-04 with the same versions as P2 step 3. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass after a fix | First run: 5 of 28 new tests failed. (1) N5 used a true/false table, but the evaluator publishes true/false as 1/0 (step 3 design), so the label read 1, not true. N5 now passes the flag through with `values` 0 "Not fitted" and 1 "Fitted"; any other value still fails. (2) The R1 test expected the band constant in the trace for a resting InvSt; the formula never reads the band then, so the test was wrong and now checks it only for RUNNING. Rerun: `343 passed` (28 new in `tests/test_franklinwh_set.py`). |
| T2 | Pass | `All checks passed!`, 53 files already formatted |
| T3 | Pass | All 18 labels present, each with a trace. `solar_total_power` 0 = `raw.pv_total` 0 = 502.OutPw 0 (night). `solar_energy_total` 12959408 Wh = 502.OutWh. `battery_operating_mode` `self_consumption` (15507 = 2). `grid_connection_status` `on_grid` (15016 = 2). `battery_inverter_state` `discharging` (InvSt 3 RUNNING, DCW 800 W > 50 W). `home_load_power` 773 W from 16000, latched on the first poll (773 is not a multiple of 100; 15506 read 800). `battery_power_fine` 773 W. `battery_charge_rating` and `battery_discharge_rating` 5000 W = 702 points. Reserves 20 % (emulator seed). 16 readings, 4 constants and 18 rules all `active`; 38 log lines name each one with its reason and source. |
| T4 | Pass | Ports 5120 and 8120 free; no traceback in either log. |
