# Test plan: P2 step 9, unit, label and scale changes reach HA, with a warning

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Fix a gap that gives wrong data in HA today. A quirk that changes a point's unit, label or scale, while the point stays, never reaches HA: the bridge reports a point only when its value changes, and the publisher sends an entity's config only the first time. With a W → kW quirk, HA shows 2.056 labelled **W**. Design Q4 also asks for a warning before a unit or scale change.

1. **Bridge.** A point is reported as changed when anything HA shows changes: value, label, units, options, `total`, or its list of quirks. Only `trace` is left out.
2. **Publisher.** It remembers the discovery config it last sent for each entity. On a change it builds the config again and sends it if it differs, so HA picks up the new unit, name or classes. While a point is unavailable its config is not resent, because without a value an enum point cannot be told from a number.
3. **Units HA can convert.** `kW` and `kWh` get HA units and device classes (`power`, `energy` / `energy_storage`), like `W` and `Wh`. Without this, a W → kW quirk would also lose the `power` device class.
4. **Preview fix found while testing.** The preview compared the new quirks with the last poll's snapshot. Between a save and the next poll that snapshot does not include the save, so a second check or save showed the first change again (this also affected step 6's preview). Both sides are now worked out from the same poll's data: current quirks against new quirks.
5. **Warnings (Q4).** The answers to check, save, remove, off and on gain a `warnings` list: one entry for each point that stays but changes unit, or whose value is rescaled by a `scale` quirk. Each says what changes, for example `label.home_load_power: unit W → kW`, and that HA's history and long-term statistics for the entity are affected. For check and save the warning comes before anything is used. For remove, off and on it comes with the answer, because those have no check step yet.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 8.
3. The API on 127.0.0.1:8120 with the FranklinWH set and `--user-quirks <scratch>/user9`.
4. The scratch broker (amqtt 0.12.1) on 127.0.0.1:18830 and the publisher, as in step 8.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. a unit-only or label-only change is reported as a change;<br>2. a poll with nothing changed reports nothing;<br>3. the publisher resends a config when units or label change, and not when only the value changes;<br>4. no config is resent while the point is unavailable;<br>5. `kW` and `kWh` get their HA classes;<br>6. check and save warn for a unit change and for a `scale` quirk, not for a label-only change;<br>7. remove and off warn when the unit goes back. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher. Then:<br>1. `check` the `u-load-kw` quirk (scale 0.001, kW);<br>2. `PUT` it;<br>3. after the next poll, read the retained messages;<br>4. `PUT` a label-only quirk `u-load-name` on `label.home_load_power`;<br>5. after the next poll, read them again;<br>6. `DELETE` both;<br>7. after the next poll, read them again. | 1. Check and save each warn about W → kW.<br>2. After step 3 the retained config for `label.home_load_power` has unit `kW`, device class `power`, and the state is about 2.05.<br>3. After step 5 the config has the new name, with no warning for it.<br>4. After step 7 the config is back to `W` and the old name, the state is about 2050, and the removal answers warn about kW → W.<br>No restart of any part. | Any not met |
| T4 | Stop the publisher, broker, API and emulator; check ports 18830, 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. **Wrong data today, the next step:** an entity whose point went away while the publisher was not running keeps its last value and shows as online in HA (rule 8). Fixed when the publisher reads back its own retained configs at start (step 10).
2. A change of a non-number value (an enum or text label). Only unit changes and number changes under the same unit warn; a rule formula that rescales does warn, because it changes the number.
3. A check step for remove, off and on. Their warnings come with the answer.
4. A real HA instance. How HA treats a unit change on an entity with statistics is from HA's documentation.

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 8. Emulator v0.2.3 (commit af7bc62), broker amqtt 0.12.1 (scratch only).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `384 passed` (5 new in `tests/test_unit_changes.py`, covering items 1–7). The first run failed item 6: a label-only save straight after a scale save warned about the scale again. That was the preview flaw in section 1.4; fixed, then all passed. |
| T2 | Pass | `All checks passed!`, 63 files already formatted |
| T3 | Pass | Home load on the emulator was about 1.3 kW in this run (it varies), not the 2 kW expected in the plan. 1. Check and save each warned `label.home_load_power: unit W → kW. …`. 2. Next poll: retained config `Home load power`, `kW`, `power`, `measurement`; state 1.371. 3. Name quirk: no warning; config `House load`, still `kW`; state 1.344. 4. After removing both: config `Home load power`, `W`, `power`; state 1273; the `u-load-kw` removal warned `unit kW → W`, the name removal gave no warning. No part was restarted. |
| T4 | Pass | Ports 18830, 8120 and 5120 free; no traceback in any log. |
