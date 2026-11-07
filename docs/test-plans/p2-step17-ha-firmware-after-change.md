# Test plan: P2 step 17, HA shows the new firmware after a change

Status: run on 2026-11-07. T1, T2 and T4 passed; T3 could not test a firmware change (see section 5).

## 1. Purpose

Fix the stale firmware version in HA left open by step 14 (its "not covered" item 3). The MQTT publisher builds the HA device info (manufacturer, model, serial, `sw_version`) once, at its own start, from the API's device answer. After step 14 a reconnect can find new firmware or options and update the bridge, but HA keeps showing the old firmware until the publisher is restarted.

The fix:

1. **A `device` event on the event stream.** When a check after a reconnect finds the same device with changed firmware or options, the service tells each subscriber, and the event stream sends `event: device` with the new identity (the same fields as `identity` in the device answer). Older clients ignore unknown events.
2. **The publisher updates HA.** On a `device` event, the publisher rebuilds its HA device info and sends every entity config it has sent again, so HA's device shows the new `sw_version` and the retained configs match. Point values are not sent again.
3. **On every reconnect to the API**, the publisher reads the device answer again before following the stream, so a change made while it was not connected also reaches HA.
4. **Another serial is refused.** If the device answer or a `device` event names a serial other than the one the publisher started with, the publisher marks the device offline in HA, logs an error and stops (exit 1). It never publishes another device's data under the first device's entities (rule 8). Today an API restarted against another device would be published under the old serial.
5. Nothing changes when the identity is the same.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 16.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile.
4. The test MQTT broker from step 11 (`broker-venv`, amqtt) on 127.0.0.1:18830, and the publisher pointed at it.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. a firmware change found after a reconnect sends one `device` update to subscribers, and the event stream sends `event: device` with the new version;<br>2. no `device` update when the device is unchanged, or when it is refused;<br>3. on a `device` event the publisher resends every sent config once, each with the new `sw_version`, and no states;<br>4. an unchanged `device` event sends nothing;<br>5. a `device` event or device answer with another serial raises `IdentityError`;<br>6. the publisher reads the device answer again on each reconnect and uses its firmware. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator, API, broker and publisher. Read the retained config of one entity. Stop the emulator; start it again with the same serial and another firmware version (if the emulator allows it). Wait for the check and read the config again. | The retained config's `device.sw_version` is the new firmware; the publisher log shows the update; no restart of the publisher | Any not met |
| T4 | Stop the publisher, API, broker and emulator; check ports 8120, 5120 and 18830 are free | All free | Any in use |

If the emulator cannot report another firmware version with the same serial, T3 is not run and the change is tested by T1 only; this is noted in the results.

## 4. Not covered

1. A real firmware update on a real aGate.
2. HA itself: that HA's device page shows the new `sw_version` after the configs are sent again is HA's documented behaviour for MQTT Discovery, not checked here.
3. A changed model chain: its points are already added and removed through `change` and `removed` events (steps 8–10); only the device info is new here.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 16. Emulator v0.2.3 (commit af7bc62); the broker is amqtt in `broker-venv`, as in step 11.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `438 passed` (9 new in `tests/test_device_event.py`, covering items 1–6; item 2 has two cases). To check the tests can fail: with the service's `device` update taken out, 2 tests failed; with the publisher's identity update taken out, 4 failed. The code was then put back. |
| T2 | Pass | `All checks passed!`, 79 files already formatted |
| T3 | **Not a firmware test** | The emulator cannot change only the firmware. Its V10 profile (`agate-v10r01b04d00`) with the same serial also reports another manufacturer name, so the bridge refused it (step 14) instead of taking the new firmware. What was seen: 1. Start (V12 profile): API firmware V12R02B60D00; 453 retained configs, all `sw_version` V12R02B60D00. 2. After the V10 profile with the same serial: `refused` "it reports FranklinWH Technologies Co., Ltd aGate X …, but this bridge was started for FranklinWH aGate X …"; the configs keep V12R02B60D00, which is right for a refused device. No `device` event was sent. The firmware change itself is covered by T1 only. |
| T4 | Pass | Ports 8120, 5120 and 18830 free; no traceback in any log. My first stop used SIGINT, which background processes started from a script ignore: the publisher kept running and the API waited for its stream. Stopped with SIGTERM, the publisher marked the device offline and stopped, and the API and broker then stopped. |

**Found during T3 (wrong data in HA, not fixed here):**

1. The aGate reports a different Model 1 manufacturer on each firmware: "FranklinWH" on V12R02B60D00 and "FranklinWH Technologies Co., Ltd" on V10R01B04D00. The emulator's V10 value comes from a reference scan of a real aGate (franklinwh-gateway-emulator `tests/data/reference_scan_static_2026-10-07.json`).
2. The FranklinWH quirk set matches the manufacturer exactly, so on V10R01B04D00 it does not apply at all: no N1–N11 labels, no 0xFFFF fixes (steps 13 and 15), and 714.DCA is not hidden although it was measured always 0 on V10. Checked: with the V10 name, the set is listed as not matched.
3. A real update from V10 to V12 changes the manufacturer, so step 14 refuses the device until the bridge is restarted.
