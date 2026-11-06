# Test plan: P2 step 10, remove stale entities from HA at each snapshot

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Fix a gap that gives wrong data in HA today (rule 8). The `removed` event (step 8) only reaches HA while the publisher is running. A point that goes away at any other time leaves its retained config, last value and `online` flag in the broker, so HA shows the old value as live, forever. Examples:

- a quirk removed or switched off while the publisher was stopped;
- a shipped quirk dropped by an app update;
- a firmware change that selects other quirks;
- `--quirk-off` or the PICS profile changed on the command line.

The fix: after publishing each snapshot, the publisher reads back the retained discovery configs in the broker and removes those of this device that the snapshot does not have.

1. **Read back.** Subscribe to `homeassistant/sensor/+/config`, collect the retained messages until none arrive for 1 s (at most 10 s), then unsubscribe. If the 10 s run out, the publisher logs a warning and works with what it read. Missing some can only leave a stale entity, never remove a live one.
2. **Which are ours.** A config counts only if its `device.identifiers` equal this device's. A topic name alone is not enough: another device's serial could share the start of ours. Configs that are not JSON are skipped.
3. **Removal.** For each of our configs whose topic is not in the snapshot, the publisher sends empty retained messages to the config topic and to the `state_topic` and point availability topic named in that config. The device-wide availability topic is never cleared. Each removal is logged with its unique id.
4. **Where.** In the publisher only. The bridge and API do not change.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 9.
3. The API on 127.0.0.1:8120 with the FranklinWH set and `--user-quirks <scratch>/user10`.
4. The scratch broker (amqtt 0.12.1) on 127.0.0.1:18830, and the publisher, as in step 9.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. a retained config of ours that is not in the snapshot gives the three empty messages, using the topics named in it;<br>2. configs in the snapshot are kept;<br>3. another device's config is kept, even when its topic starts like ours;<br>4. a config that is not JSON, or has no device, is skipped;<br>5. the read-back stops after 1 s without messages and unsubscribes;<br>6. the publisher runs the clean-up after a snapshot. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher. Then:<br>1. publish by hand a retained config for another device whose topic starts with our device's id;<br>2. stop the publisher;<br>3. `PUT …/quirks/fwh-n7-r5/off`;<br>4. start the publisher again;<br>5. read the retained messages. | 1. No retained config, state or availability for `label.battery_operating_mode`.<br>2. The other device's config is still there.<br>3. All other configs of ours are still there (455).<br>4. The publisher logs one stale removal, for that entity. | Any not met |
| T4 | Stop the publisher, broker, API and emulator; check ports 18830, 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

**Wrong data today, found while testing this step (not fixed here):**

- **A clean stop leaves the device `online`.** After Ctrl-C (SIGINT) the publisher exits with code 0 and a clean MQTT disconnect, so the broker never sends the last-will `offline`. The retained device availability stays `online`, and HA shows every last value as live (rule 8). SIGTERM is not affected: the connection drops and the will marks the device `offline`. Checked on 2026-11-06 with the scratch broker.
- **A lost broker ends the publisher.** When the broker stopped, the publisher died with `MqttCodeError: The client is not currently connected` instead of reconnecting: the run loop only catches API errors. After a broker restart (for example an HA Mosquitto add-on update), nothing publishes again, and a broker that keeps retained messages still shows the device `online` with its last values.

Other gaps:

1. A device whose serial changed. Its entities belong to another device id, so they are not touched.
2. Entities of a device that is no longer published at all. Nothing runs for that device to clean them up.
3. A real HA instance. The empty retained config is HA's documented way to delete a discovered entity.

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 9. Emulator v0.2.3 (commit af7bc62), broker amqtt 0.12.1 (scratch only).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `388 passed` (4 new in `tests/test_stale_entities.py`, covering items 1–6; the fake MQTT client in `tests/test_removed.py` now keeps retained messages). `tests/conftest.py` shortens the 1 s quiet wait in tests. |
| T2 | Pass | `All checks passed!`, 66 files already formatted |
| T3 | Pass | The first try did not start the publisher (a shell quoting slip in the test script), so it was rerun from the start of step 2. 1. A retained config for another device (`…0cd0e8_x_label_battery_operating_mode`, identifiers `…_x`) was published by hand. 2. Publisher running: 456 of our configs. 3. Publisher stopped, `fwh-n7-r5` switched off: still 456 configs, and the mode entity's config, state `self_consumption` and `online` stayed in the broker (the stale case). 4. Publisher started: log `Snapshot: 455 points, 1364 messages`, then `Removed stale entity modbus_bridge_mock0001efc63f0cd0e8_label_battery_operating_mode from Home Assistant`. 5. Retained afterwards: 455 of our configs, with no config, state or availability for the mode entity (1368 → 1365 unique topics). The other device's config was still there. The scratch broker sent most retained messages twice to the dump script, so counts are of unique topics. |
| T4 | Pass | Ports 18830, 8120 and 5120 free; no traceback in any log. |
