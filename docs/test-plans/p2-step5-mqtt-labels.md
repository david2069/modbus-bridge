# Test plan: P2 step 5, publishing raw readings and labels over MQTT

Status: run on 2026-11-04, all passed. Results are in section 5.

## 1. Purpose

Check that the MQTT Discovery publisher (design D8) handles `raw.*` and `label.*` points, using the FranklinWH set.

1. Today the publisher reads a model number from the start of every key, so a `raw.` or `label.` key stops it. Keys without a model number are handled.
2. `label.*` entities are enabled by default. They are the neutral face of the device. `raw.*` entities are created but disabled by default, like SunSpec settings. Neither is a diagnostic entity.
3. A rule with a `values` list is an HA enum sensor. Its `options` are the allowed values as text, so the mode, grid status and battery state show as choices. The point JSON gains `options` for such rules.
4. A label or reading with units gets a unit, device class and state class, as SunSpec points do.
5. Lifetime energy: a rule or reading may say `"total": true`. Its Wh value then counts up over the device's life and is published as `energy` / `total_increasing`, so HA's Energy dashboard can use it. The point JSON gains `total`. The FranklinWH set marks 15510–11 and 15512–13 and their N6 labels with it. Without it, a Wh value is `energy_storage`, as for SunSpec points that are not lifetime counters.
6. A rule without units or values is a plain text sensor.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 4.
3. The API on 127.0.0.1:8120 as in step 4, with `--quirks src/modbus_bridge/quirk_sets/franklinwh.json`.
4. The scratch broker (amqtt 0.12.1) on 127.0.0.1:18830 and the publisher, as in P1 step 8.
5. `scripts/mqtt_dump.py` in the scratchpad, to save every retained message.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. discovery for a `label.` and a `raw.` point does not fail;<br>2. enabled by default for labels and disabled for raw;<br>3. an enum label has `device_class` `enum` and its options, and no unit;<br>4. a label with units has the unit and classes;<br>5. `total` gives `energy` / `total_increasing`;<br>6. a text label has no classes;<br>7. point JSON carries `options` and `total`;<br>8. a bad `total` is refused when the file loads. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher. Dump the retained messages. | 1. The publisher reports a snapshot with no error.<br>2. One discovery config for each of the 18 labels and 16 raw readings.<br>3. `battery_operating_mode`: enum with the options `emergency_backup`, `self_consumption`, `time_of_use`; state `self_consumption`.<br>4. `grid_connection_status` and `battery_inverter_state`: enum with their options; the states agree with the API.<br>5. `solar_energy_total`: `Wh`, `energy`, `total_increasing`.<br>6. `home_load_power`: `W`, `power`, `measurement`.<br>7. Labels are enabled by default and raw readings disabled.<br>8. The SunSpec configs are unchanged in count from P1 step 8. | Any not met |
| T4 | Stop the publisher, broker, API and emulator; check ports 18830, 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. Taking a real HA instance through discovery. The messages are checked against HA's documented fields only.
2. Changes arriving by server-sent events. They use the same point JSON, and step 8's tests cover the path.
3. HA entity names for labels are drafts until the owner's label review (D3).
4. A binary sensor for the N5 flags. They are enum sensors with options `0` and `1` for now.

## 5. Results

Run on 2026-11-04 with the same versions as P1 step 8 and P2 step 4. Emulator v0.2.3 (commit af7bc62), broker amqtt 0.12.1 (scratch only).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `350 passed` (7 new: 4 in `test_mqtt_publisher.py`, 1 each in `test_franklinwh_set.py`, `test_raw.py` and `test_evaluator.py`) |
| T2 | Pass | `All checks passed!`, 54 files already formatted |
| T3 | Pass | Publisher: `Snapshot: 456 points, 1367 messages`, no error. 456 configs: 422 SunSpec (as in P1 step 8), 18 labels and 16 raw readings. All 18 labels enabled by default and all 16 raw readings disabled. Enums: `battery_operating_mode` options emergency_backup, self_consumption, time_of_use, state `self_consumption`; `grid_connection_status` options restarting, on_grid, off_grid, dispatch_active, state `on_grid`; `battery_inverter_state` options idle, charging, discharging, state `discharging`; N5 flags options `0`, `1`. `solar_energy_total` and `solar_local_energy`: `Wh`, `energy`, `total_increasing`. `home_load_power`: `W`, `power`, `measurement`. Reserves: `%`, `measurement`. Every label's MQTT state equals its API value. |
| T4 | Pass | Ports 18830, 8120 and 5120 free; no traceback in any log. |
