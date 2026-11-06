# Test plan: P2 step 8, a "removed" event so HA entities go away

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Check that a point taken away by a quirk change is removed cleanly from Home Assistant at once (design Q4, U7), with no restart.

1. **Poller.** A poll notes each point that was in the last snapshot and is not in the new one. A point that failed to read is not removed; it stays, unavailable, as now (rule 8). Removal happens when a quirk hides a point, a rule is switched off, or a user reading or rule is removed. Each removal is logged.
2. **Service and API (D9).** The event stream gains a `removed` event with `{"key": ...}`, under the same sequence number as that poll's changes. A poll with only removals still counts as a change and gets a sequence number.
3. **Publisher (D8).** On `removed`, the publisher sends an empty retained message to the point's discovery config topic, which makes HA delete the entity. It also clears the point's retained state and availability topics. If the point comes back later, its discovery config is sent again.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 7.
3. The API on 127.0.0.1:8120 as in step 7, with the FranklinWH set and `--user-quirks <scratch>/user8`.
4. The scratch broker (amqtt 0.12.1) on 127.0.0.1:18830 and the publisher, as in step 5.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. a point that is no longer built is listed as removed;<br>2. a point whose model failed to read is not removed;<br>3. a poll with only a removal gets a sequence number and reaches subscribers;<br>4. the event stream sends `removed` with the key;<br>5. the publisher's removal messages are three empty retained messages on the right topics;<br>6. after a removal, the point's next change sends its discovery config again. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher. Then:<br>1. `PUT …/quirks/fwh-n7-r5/off`;<br>2. after the next poll, read the retained messages;<br>3. `DELETE …/quirks/fwh-n7-r5/off`;<br>4. after the next poll, read the retained messages again. | 1. After step 2, no retained config, state or availability for `label.battery_operating_mode`; every other label config is still there.<br>2. The API log has one line for the removal; the publisher logs it.<br>3. After step 4, the config is back, with state `self_consumption`.<br>No restart of any part. | Any not met |
| T4 | Stop the publisher, broker, API and emulator; check ports 18830, 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. An entity whose point went away while the publisher was not running, for example a quirk removed while it was stopped. Its retained config stays in the broker. Cleaning these up needs the publisher to read back its own retained configs at start.
2. A change of unit, label or scale on a point that stays. Its discovery config is not sent again, so HA keeps the old unit (Q4). The poller only reports a point as changed when its value changes.
3. A real HA instance. The empty retained config is HA's documented way to delete a discovered entity.

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 7. Emulator v0.2.3 (commit af7bc62), broker amqtt 0.12.1 (scratch only).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `379 passed` (5 new in `tests/test_removed.py`, covering items 1–6) |
| T2 | Pass | `All checks passed!`, 61 files already formatted |
| T3 | Pass | Retained configs: 456 before (18 labels), 455 after switching `fwh-n7-r5` off (17 labels), 456 after switching it back on (18 labels). After the switch-off there was no retained config, state or availability for `label.battery_operating_mode`; after the switch-on all three were back, state `self_consumption`, available `online`. API log: `Point label.battery_operating_mode removed: the active quirks no longer give it`. Publisher log: `Removed label.battery_operating_mode from Home Assistant`. No part was restarted. |
| T4 | Pass | Ports 18830, 8120 and 5120 free; no traceback in any log. |
