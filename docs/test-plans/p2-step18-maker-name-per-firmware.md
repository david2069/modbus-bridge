# Test plan: P2 step 18, the aGate's maker name differs by firmware

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

Fix the wrong data found in step 17 (section 5). The aGate reports a different Model 1 manufacturer on each firmware: "FranklinWH" on V12R02B60D00 and "FranklinWH Technologies Co., Ltd" on V10R01B04D00 (reference scan of a real aGate, franklinwh-gateway-emulator `tests/data/reference_scan_static_2026-10-07.json`). So:

- on V10 the FranklinWH quirk set does not match at all: no N1–N11 labels, no 0xFFFF fixes, and 714.DCA is not hidden although it was measured always 0 on V10;
- a firmware update from V10 to V12 changes the manufacturer, and step 14 refuses the device as another one.

The fix:

1. **A set can name several manufacturers.** `match.manufacturer` takes one name, as today, or a list of names. A device matches if its Model 1 manufacturer is one of them, exactly (no partial or case-blind match: a guessed match would apply the wrong quirks). The FranklinWH set lists both names, with the reference scan as the source.
2. **Same serial and model, other maker name: the same device.** After a reconnect, a device with the same serial and model but another manufacturer is treated like a firmware change (step 14, item 4): the identity is updated, the quirks are rebuilt, a warning names both makers, and the `device` event (step 17) updates HA.
3. **Without a serial, nothing changes:** a device with no serial and another manufacturer is still refused, because only the maker and model tell it apart.
4. User quirks and proposals keep using the device's current manufacturer, as today.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, with `--no-control` and a fixed serial.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile; the broker and publisher as in step 17.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. a set with a list of manufacturers matches each name and nothing else (not a prefix, not another case);<br>2. one name as text still works; an empty list or a non-text name is refused;<br>3. the shipped FranklinWH set matches both names, and its quirks, readings and rules apply on V10R01B04D00;<br>4. after a reconnect, the same serial and model with another maker name updates the identity, rebuilds the quirks and sends a `device` update; it is not refused;<br>5. another serial is still refused; with no serial, another maker name is still refused. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator with the V10 profile, the API, broker and publisher. Read the device answer, `GET …/quirks` and `GET …/points`. | The FranklinWH set applies; `label.*` points are present; `714.DCA` is absent | Any not met |
| T4 | Stop the emulator; start it with the V12 profile and the same serial. Wait for the check. Read the device answer, the points and one retained HA config. | Not refused; firmware V12R02B60D00 and maker "FranklinWH" in the device answer; points live; the retained config has the new `sw_version` and maker; the log has one warning naming both makers | Any not met |
| T5 | Stop everything with SIGTERM; check ports 8120, 5120 and 18830 are free | All free | Any in use |

## 4. Not covered

1. Other maker names the aGate may report on other firmware. Each would have to be added to the set from a scan.
2. A real firmware update on a real aGate.
3. A device that changes its serial on a firmware update; it would be refused.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 17. Emulator v0.2.3 (commit af7bc62) with `--serial MOCK0001EFC63F0CD0E8` (its own mock serial) and `--no-control`.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `455 passed` (17 new in `tests/test_maker_names.py`, covering items 1–5). To check the tests can fail: with the maker compared again and the set back to one name, 3 tests failed; the code was then put back. `tests/test_recheck.py`'s `load` helper gained a `maker` argument. |
| T2 | Pass | `All checks passed!`, 81 files already formatted |
| T3 | Pass | V10 profile: maker "FranklinWH Technologies Co., Ltd", V10R01B04D00; set `franklinwh` applies; 453 points, 451 with a value; 18 labels; `714.DCA` absent; `label.home_load_power` 1052. Retained HA configs: 453, all `sw_version` V10R01B04D00. |
| T4 | Pass | V12 profile, same serial: not refused; maker "FranklinWH", V12R02B60D00; set still applies; 451 of 453 with a value; 18 labels; `714.DCA` absent. One warning: "changed after a reconnect: firmware V10R01B04D00 -> V12R02B60D00, … maker FranklinWH Technologies Co., Ltd -> FranklinWH, model chain changed; quirks rebuilt". Publisher: "Device info changed (firmware V12R02B60D00); 453 configs sent again", without a restart; all 453 retained configs now have `sw_version` V12R02B60D00 and maker FranklinWH. This also covers step 17's T3, which the emulator could not run then. |
| T5 | Pass | Stopped with SIGTERM; ports 8120, 5120 and 18830 free; none of the processes left; no traceback in any log. |

Seen in T4, not a fault: the HA device name is built from the maker, so it changes from "FranklinWH Technologies Co., Ltd aGate X …" to "FranklinWH aGate X …". Entity ids do not change, because they are built from the serial and point, and a name the user gave the device in HA is kept.
