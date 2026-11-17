# Test plan: P2 step 23, volt-var curve voltages read as volts on the aGate

Status: written on 2026-11-18, before the code; run the same day, all passed. Results are in section 5.

## 1. Purpose

Model 705 (volt-var) gives each curve point's voltage in percent of nominal voltage (`VNomPct`). The reference aGate gives volts instead: `Crv[n].Pt[0..3].V` = 20700, 22000, 24000, 25800 with `V_SF` −2, so 207, 220, 240 and 258. These are the Australian volt-var points in volts, not 207–258 %. The PICS ranges for these points are percent (about 77–118). `VRef` (10000, so 100 %) and the `Var` points (44, 0, 0, −60 %) are in percent as the model says, so only the `V` points are wrong.

Evidence: read-only scan of the reference aGate, 2026-10-07 (firmware V10R01B04D00), in franklinwh-gateway-emulator `tests/data/reference_scan_static_2026-10-07.json`, commit 32a7af7 (MIT). The V12R02B60D00 snapshot in franklinwh-modbus (`docs/SUNSPEC_SNAPSHOT_2026-10-20_V12R02B60D00.md`) has no 705 values, so V12 is not covered (design 2b, S2: the scope is what was seen).

1. **A new firmware-layer quirk set**, `quirk_sets/franklinwh-v10r01b04d00.json`, matched on the FranklinWH maker names and firmware V10R01B04D00 only (min = max). It holds one quirk, `fwh-fw10-q-705-v`: point `705.Crv[*].Pt[*].V`, units `V`, with its reason and source.
2. The value is not changed; only its unit. In HA the entity gets unit V and device class voltage. Model 705 entities stay disabled by default in HA.
3. On any other firmware the quirk does not apply and the point keeps `VNomPct` (S5).
4. The quirk can be switched off by its id, like any quirk (rule 9).

## 2. Setup

1. The project `.venv`.
2. The emulator (franklinwh-gateway-emulator v0.2.3-38, commit 46b0605) on 127.0.0.1:5122 with `--no-control`, run twice: profile `agate-v10r01b04d00` and profile `agate-v12r02b60d00-candidate`. Ports 5120 and 8080 are the owner's run and are left alone.
3. The API on 127.0.0.1:8120 with `--quirks src/modbus_bridge/quirk_sets` (both files) and the PICS profile SM-000028.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. the shipped file loads, is the firmware layer, matches only V10R01B04D00 and both FranklinWH maker names;<br>2. on a made-up 705 block with V10R01B04D00, every `Crv[n].Pt[n].V` has units `V` and the same value as without the quirk; `VRef` and `Var` points keep `VNomPct` and `DeptRef` (the units the bridge gives them);<br>3. with firmware V12R02B60D00, or another maker, the points keep `VNomPct`;<br>4. switched off by id, the points keep `VNomPct`;<br>5. the HA config for such a point has unit V and device class voltage.<br>To check the tests can fail: change the match to V12R02B60D00. | All pass; the changed match fails | Any fails, or the change passes |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Emulator profile `agate-v10r01b04d00`: `GET …/points` and `…/quirks` | All 12 `705.Crv[n].Pt[n].V` points: units `V`, values 207, 220, 240, 258; `VRef` 100 `VNomPct`; the quirk listed as applied | Any not met |
| T4 | Emulator profile `agate-v12r02b60d00-candidate`, same reads | The 12 points keep `VNomPct`; the quirk set is not applied | Any not met |
| T5 | Stop the emulator and API; check ports 5122 and 8120 | Both free | Any in use |

## 4. Not covered

1. Firmware V12R02B60D00 and later: no 705 values have been read from them. If someone reads them, the scope can be widened with that evidence.
2. The "not verified" mark of S5 for a device outside a quirk's scope: not built yet.
3. Other countries' aGates: their curves may be in percent as the model says.
4. A real aGate.

## 5. Results

Run on 2026-11-18 with the emulator v0.2.3-38 (commit 46b0605), `--no-control`.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `502 passed` (8 new in `tests/test_volt_var_volts.py`). Checked they can fail: the match moved to V12R02B60D00 gave 4 failures; put back. |
| T2 | Pass | `All checks passed!`, 89 files already formatted |
| T3 | Pass | Profile `agate-v10r01b04d00`, firmware V10R01B04D00: all 12 `705.Crv[1..3].Pt[1..4].V` have units `V`, values 207, 220, 240, 258, quirk `fwh-fw10-q-705-v`. `705.Crv[1].VRef` 100 `VNomPct`, `Crv[1].Pt[1].Var` 44 `DeptRef`, no quirk. `/quirks` lists the set and the quirk as `active`. |
| T4 | Pass | Profile `agate-v12r02b60d00-candidate`, firmware V12R02B60D00: the 12 points keep `VNomPct` with no quirk; the set is not applied. |
| T5 | Pass | My emulator and API stopped with SIGTERM; ports 5122 and 8120 free; no error or traceback in the API logs. The owner's run on 5120 and 8080 was not touched. |

Found in the run: point keys count curves and points from 1 (`Crv[1]`, as the PICS does), not 0 as the scan file does. The first T3 script asked for `Crv[0].VRef` and got nothing; the test and the run were done again with 1-based keys.
