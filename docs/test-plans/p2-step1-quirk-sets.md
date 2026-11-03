# Test plan: P2 step 1, quirk sets as data (SunSpec points only)

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that quirks for the vendor, model and firmware layers (design L2–L4) are data, are chosen by Model 1, are visible with their source, and can be switched off (rule 9):

1. A quirk-set file (`modbus-bridge/quirk-set` v1, JSON) has an id, a layer (`vendor`, `model` or `firmware`), a Model 1 match, a source, and a list of quirks. Each quirk has an id, a point, a reason, and one or more changes: `scale` (a multiplier), `invert` (flip the sign), `units`, `label` or `hide`.
2. Match rules:
   - vendor: Mn;
   - model: Mn and Md (a list), and optionally Opt;
   - firmware: Mn, optionally Md, and a Vr range (`min` and/or `max`, inclusive). Versions are compared by their numbers in order, e.g. `V12R02B60D00` is 12, 2, 60, 0. A device with no Vr does not match a firmware set.
3. A point is a key such as `103.W`. `[*]` matches any group index (`160.module[*].DCW`). A key without `#k` also covers repeated models (`701.W` covers `701#2.W`).
4. Layers apply lowest first; for each change, a higher layer overrides a lower one. Two quirks in the same layer making the same change to one point is a clash: both are marked failing and the point has no value.
5. A quirk switched off (`--quirk-off ID`) is ignored, so the point falls back to the layer below.
6. Scale or invert on a value that is not a number (enum, flags, text) fails: the point has no value and the quirk is marked failing, with the error (rule 8, design U9).
7. A hidden point is not published.
8. The REST API gives `GET /api/v1/devices/{id}/quirks`: each quirk of a matching set with its layer, set, point, changes, source, reason and state (`active`, `overridden` when every change it makes is replaced by a higher layer, `off`, `failing` or `unused`), and the sets that did not match. Each point's JSON has a `quirks` list of the quirk ids applied to it.
9. A file that breaks the format is refused at start with a clear error. So are a duplicate quirk id and a `--quirk-off` id that no file defines.

No real maker's quirk is shipped in this step. The test quirk files are made up.

## 2. Setup

1. The project `.venv`.
2. The simulator from P1 step 9 on 127.0.0.1:5121 (Mn `ExampleSolar`, Md `SimInverter 5000`, Vr `1.0.0`).
3. Made-up quirk files in the scratchpad (not in the repo):
   - `vendor.json` (vendor, Mn `ExampleSolar`): `v-w-kw` scales 103.W by 0.001 and sets units `kW`; `v-dcw-label` relabels `160.module[*].DCW` as `MPPT power`; `v-hide-evt2` hides 103.Evt2.
   - `firmware.json` (firmware, Mn `ExampleSolar`, Vr 1.0.0 to 1.9.9): `f-w-watts` sets 103.W scale back to 1 and units to `W`; `f-st-scale` scales 103.St (an enum, so it must fail).
   - `other.json` (vendor, Mn `OtherMaker`): must not match.
4. The API on 127.0.0.1:8121 with the step-7 scratch token file.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests cover: loading and refusing bad files; each match rule, including firmware ranges and a missing Vr; `[*]` and `#k` keys; layer override; switching off; a same-layer clash; scale or invert on an enum failing; hide; `unused`; the quirks endpoint and the `quirks` list in point JSON. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the simulator and the API with `--quirks` for the three files. Log, `GET …/quirks`, `GET …/points` | The log names each matching set and quirk with its source. `other` is listed as not matched. 103.W is in `W` (firmware overrides vendor), its `quirks` list shows `v-w-kw` and `f-w-watts`. Both 160 module DCW labels read `MPPT power`. 103.Evt2 is absent. 103.St is unavailable and `f-st-scale` is `failing` with its error. | Any of these not met |
| T4 | Restart the API adding `--quirk-off f-w-watts`; `GET …/points` | 103.W is in `kW`, about one thousandth of the watts shown in T3; `f-w-watts` is `off` | Otherwise |
| T5 | Start the API with `--quirk-off no-such-id`; and with a quirk file containing an unknown field | Both refuse to start with a clear error | Either starts |
| T6 | Stop the API and simulator; check ports 5121 and 8121 are free | Both free | Either in use |

## 4. Not covered

1. Raw register maps and readings added by a quirk (P2 step 2).
2. Neutral labels, constants and derived rules (the evaluator, design 3a).
3. User quirks (L5): saving from the UI, the audit log and export (design 2b).
4. Switching a quirk on or off through the API while running. In this step it is done with a start option.
5. Any real maker's quirks.
6. The MQTT publisher. It takes labels, units and the point list from the API, so it is not retested here.

## 5. Results

Run on 2026-11-03 against the P1 step 9 simulator, same versions as P1 step 9.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `225 passed` (43 new in `tests/test_quirks.py`) |
| T2 | Pass | `All checks passed!`, 45 files already formatted |
| T3 | Pass, after one change | Log: both matching sets and each quirk with its changes, reason and source; `Quirk set test-other does not match this device`; `Quirk f-st-scale failing: 103.St is not a number (OperatingState)`. API: `not_matched ['test-other']`. 103.W `4406 W`. Both 160 module DCW labelled `MPPT power`. 103.Evt2 absent. 103.St unavailable, `f-st-scale` `failing`. **Plan expectation corrected:** the plan said 103.W would list both `v-w-kw` and `f-w-watts`. The firmware quirk replaces every change the vendor quirk makes, so only `f-w-watts` applies. The first run still showed `v-w-kw` as `active`, which hid that it had no effect. A new state, `overridden`, was added (with a test), and the rerun shows `v-w-kw overridden`. |
| T4 | Pass | Log: `Quirk f-w-watts on 103.W switched off`. API: `f-w-watts off`, `v-w-kw active`; 103.W `4.489 kW`, quirks `['v-w-kw']`. |
| T5 | Pass | `Error: cannot switch off unknown quirk id(s) no-such-id`, exit 2. `Error: …/bad.json: quirk has unknown field(s) colour`, exit 2. |
| T6 | Pass | Ports 5121 and 8121 free; no traceback in the logs. |
