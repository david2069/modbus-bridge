# Test plan: P2 step 3, the evaluator (constants and derived rules)

Status: run on 2026-11-04, all passed after one fix. Results are in section 5.

## 1. Purpose

Check the vendor-independent evaluator of design 3a. Vendor, model and firmware layers supply data only; there is no maker-specific code.

1. A quirk set may have `constants` and `rules`.
   - A constant has `id`, `name`, `value` (a number), optional `units`, `reason` and optional `source`.
   - A rule has `id`, `output` (published as `label.<output>`), `inputs` (local name to point key: SunSpec, `raw.` or `label.`), `formula`, optional `latch`, optional `tables` (lookup tables as `[key, value]` pairs), optional `values` (allowed output values with a plain-English description each), optional `units` and `label`, `reason` and optional `source`.
2. The formula language is small and fixed. It allows numbers, text, `true`/`false`, `+ - * / // %`, comparisons, `and`/`or`/`not`, `x if c else y`, `in` and `not in` with a list of constants, `abs`, `min`, `max` and `lookup(table, x)`. Anything else is refused when the file loads. No general code is run.
3. Names in a formula are the rule's inputs, `latched`, or constants. Constants are looked up across layers (highest wins) when the rule runs.
4. A missing input gives no value (never 0), and the trace shows which input was missing. A runtime error gives no value and the rule is `failing` with the error until it next succeeds. Errors include division by zero, an unknown constant, a lookup with no entry, or a value outside `values`.
5. `latch`: once the latch expression is true, `latched` stays true until the bridge restarts ("a rule may remember one flag between polls").
6. Rules run in dependency order, so a rule may use another rule's output. A loop inside one file is refused when it loads. A loop formed across files is reported as `failing` on each rule in it, and those rules give no value.
7. Layers: a higher layer's constant or rule with the same name or output replaces the lower one. Switching off by id falls back to the layer below. Two in the same layer clash: both are `failing` and give no value.
8. Each output's point JSON has a `trace`: the rule id and source, each input's key and value, and each constant used with its value, units and source.
9. The quirks endpoint lists constants and rules with their state (`active`, `overridden`, `off`, `failing`) and error.
10. Ids stay unique across quirks, readings, constants and rules.

## 2. Setup

1. The project `.venv`.
2. The simulator on 127.0.0.1:5121 with `--extra`.
3. Made-up files in the scratchpad: `raw.json` from step 2, plus `rules.json` (vendor, Mn `ExampleSolar`):
   - constant `band_w` = 50 W;
   - rule `x-state`: output `battery_state`, inputs `p = raw.batt_w` and `st = 103.St`. Formula: `"idle" if st not in [4, 5] else ("discharging" if p > band_w else ("charging" if p < -band_w else "idle"))`. Its `values` are idle, charging and discharging.
   - rule `x-mode`: output `mode_name`, input `m = raw.mode`, `lookup(modes, m)` with table 1 = `backup`, 2 = `self_consumption`.
   - rule `x-share`: output `mppt1_share`, inputs `a = 160.module[1].DCW` and `w = 103.DCW`. Formula `a * 100 / w`, units `%`.
   - rule `x-spare`: output `spare_x2`, input `s = raw.spare` (always unavailable), formula `s * 2`.
4. The API on 127.0.0.1:8121 with `--quirks` for both files.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: the formula language (each allowed form, and refusals such as attribute access, calls to other functions, comprehensions, `**`); missing input; division by zero; unknown constant; lookup miss; `values` check; latch; dependency order; loop refused in one file and failing across files; layer override, off and clash for constants and rules; trace; quirks endpoint. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the simulator and API; `GET …/points` and `GET …/quirks` | `label.battery_state` is `discharging` (simulator power is about +1000 to +1500 W after invert, St is MPPT). `label.mode_name` is `self_consumption`. `label.mppt1_share` is about 55 %. `label.spare_x2` is unavailable, with `spare` missing in its trace, and `x-spare` is not `failing`. Each trace names the rule, inputs and constants. All rules `active`. | Any of these not met |
| T4 | Restart with `--quirk-off x-mode` | `label.mode_name` is absent; `x-mode` is `off` | Otherwise |
| T5 | Stop the API and simulator; check ports 5121 and 8121 are free | Both free | Either in use |

## 4. Not covered

1. Real FranklinWH rules R1–R5 and labels N1–N11 (next step, from public sources only).
2. The MQTT publisher for text outputs (it publishes them as text already; a discovery check comes with the FranklinWH step).
3. User rules (L5) and editing rules in a UI.
4. Keeping a latch across restarts.
5. Rules seeing points that a quirk hides (rules see published points only).

## 5. Results

Run on 2026-11-04 against the simulator with `--extra`, same versions as P1 step 9.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `315 passed` (54 new in `tests/test_evaluator.py`, one added after T4's fix) |
| T2 | Pass | `All checks passed!`, 51 files already formatted |
| T3 | Pass | First start refused, correctly: `quirk id 'r-mode' is used twice`. The test file's rule ids clashed with step 2's reading ids. The rules were renamed `x-…` (this plan updated to match) and rerun. Log names the constant and each rule with its formula, reason and source. `label.battery_state` `discharging` (trace: `st` 4 MPPT, `p` 1472, `band_w` 50 W from `c-band`, description `Discharging`). `label.mode_name` `self_consumption`. `label.mppt1_share` 54.01 % (1818 / 3366). `label.spare_x2` unavailable, trace `missing: "s"`, `x-spare` `active` (not failing). All rules and the constant `active`. |
| T4 | Pass after a fix | First run: `Error: cannot switch off unknown quirk id(s) x-mode`. **Bug:** the start-up check in `serve.py` only knew point-quirk ids, so readings (step 2), constants and rules could not be switched off from the command line. Fixed by one shared check (`quirks.check_off`) used by `serve.py` and the quirk set, with a new test covering all four kinds of id. Rerun: log `Rule x-mode … switched off`; `label.mode_name` absent; `x-mode` `off`. |
| T5 | Pass | Ports 5121 and 8121 free; no traceback in the logs. |
