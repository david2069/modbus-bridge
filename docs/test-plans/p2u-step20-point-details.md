# Test plan: P2U step 20, where each point is read and what the PICS says

Status: written on 2026-11-08; run on 2026-11-15, all passed. Results are in section 5. The unit tests in T1 were written and run before this plan, against rule 3; they are run again under it. Extended on 2026-11-15 (owner): certified value, Min/Max and a simple/full view (items 5 to 7, tests T1.6 to T1.9); this part of the plan was written before its tests.

## 1. Purpose

The owner asked for the metadata a SunSpec explorer shows, next to each point in the UI (owner, 2026-11-08). It is built from what the bridge already has: no new store and no new input.

1. **Address.** Each SunSpec point gets the Modbus address of its first register (0-based, holding registers) and its size in registers. It is worked out from the official definition, starting at the model's place in the chain, and counts the points we do not show: the header, scale factors and pads.
   - The layout must end exactly where the device's model length says. If it doesn't, the model's points get no address, never a guessed one (rule 8), and a warning is logged.
   - A raw reading keeps its address, size and table (holding or input) from its quirk set.
   - A rule's output has no address.
2. **PICS status** for each SunSpec point, from the loaded PICS profile:
   - `implemented`;
   - `unimplemented`;
   - `not listed` (the PICS covers the model but not this point);
   - `model not covered`.
   It is `null` with no PICS, and for labels and raw readings.
3. **API.** A new route, `GET /api/v1/devices/{id}/point-info`, gives these for every point the device has now, plus the PICS certificate and source. It needs the token. The points answer and the event stream do not change, so the HA publisher is not affected.
4. **UI.** The Points table gains Type, Access (R or RW), Address and PICS columns. An address switch shows addresses 0-based (as sent on the wire) or 1-based.
5. **Certified value and Min/Max.** The PICS spreadsheet also gives, for each point, the value the test lab recorded (where it is a number or text, not just "supported" or "unimplemented") and a Min and Max for writable settings (96 rows in SM-000028). The converter keeps them, the profile becomes version 2, and version 1 profiles still load (with none). SM-000028.json is made again from the published spreadsheet, whose SHA-256 must equal the one already recorded. Values are kept as the PICS gives them; they are not scaled or checked against the device. Nothing else new is read: the Testing Info sheet and the signer's name stay out.
6. **API.** Each point in `point-info` gains `certified`, `min` and `max` (`null` when the PICS gives none), and `ha_default`: whether HA enables the point's entity by default (the same rule as the MQTT publisher).
7. **Simple and full view.** A switch in the UI, kept in the browser. Simple shows only points with `ha_default` and the columns Label, Value, Units and Quirks. Full shows every point and all columns, including Certified, Min and Max. It is a view choice for anyone with the token, not a role: there are no roles yet.

## 2. Setup

1. The project `.venv`.
2. The emulator on 127.0.0.1:5122 with `--no-control` (run with v0.2.3-34, commit c034ef6). Port 5120 is the owner's own run and is left alone.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile SM-000028.
4. A browser for T4: headless Google Chrome, driven over its DevTools port by a scratch script outside the repo, as in step 19.
5. For T5, a scratch script that reads holding registers from the emulator. It runs only after the bridge has stopped, so the emulator never has two clients (rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests in `tests/test_point_info.py`:<br>1. on a made-up inverter with repeating groups (models 1, 103, 120, 160 with 2 modules), the registers at each point's address are exactly that point's raw value;<br>2. a model whose layout does not fill its length gives no addresses;<br>3. a raw reading keeps its address, size and table;<br>4. each PICS status, and `null` with no PICS or for labels and raw readings;<br>5. the route answers for every point in the points answer, with the right addresses; it gives the PICS certificate when loaded; it needs the token;<br>6. the converter keeps a numeric value, a text value, and Min/Max, and keeps nothing for "supported" or "unimplemented"; the Testing Info sheet and the signer's name still do not reach the profile;<br>7. a version 1 profile loads with no details; an unknown version is refused;<br>8. `point-info` gives `certified`, `min`, `max` from the PICS, `null` without one, and `ha_default` true for `713.SoC` and a label, false for `raw.*` and `1.Mn`;<br>9. the shipped SM-000028.json: `702.WMax` has min 0 and max 10000, `702.WChaRteMaxRtg` has certified 0.<br>To check the tests can fail: shift every address by one register. | All pass; the shifted addresses fail | Any fails, or the shift passes |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T2b | Run the converter on the published SM-000028 spreadsheet (local copy; its SHA-256 equals the recorded one) and diff the profile | Only `version`, the per-model `details` change; implemented and not implemented lists are unchanged | Anything else changes, or the hash differs |
| T3 | Start the emulator and API; `GET …/point-info`; check the log | Every SunSpec point has an address and a PICS status; raw readings have their addresses; certified and Min/Max present where the PICS has them; no layout warning in the log | Any not met |
| T4 | Open `/ui`; in full view pick 702, then 714, then "Raw readings"; switch to 1-based; switch to simple; reload; 390 px wide in both views | Full: Type, Access, Address, PICS, Certified, Min, Max shown and agree with `point-info`; 1-based is 0-based + 1. Simple: only `ha_default` points, four columns, counts in the list match. The choice survives a reload. No sideways page scroll | Any not met |
| T5 | Stop the API. With the scratch script as the only client, read each 702 point's registers at its address, and the registers of `1.SN` and `714.Prt[1].IDStr` | Each read value matches the points answer saved in T3 (702 ratings are static) | Any mismatch |
| T6 | Stop the emulator and browser; check ports 5122, 8120 and 9223 are free | All free | Any in use |

## 4. Not covered

1. Points the bridge does not read (unimplemented by the PICS, or never giving a value) are still not listed. Showing all points of a model, as a SunSpec explorer does, would be a separate step.
2. Address formats other than 0-based and 1-based (for example 4xxxx).
3. A real aGate.
4. Whether a certified value is scaled the same way as our value: the PICS does not say. Both are shown side by side, labelled, and not compared.
5. Roles: anyone with the token can pick either view.

## 5. Results

Run on 2026-11-15 with the emulator v0.2.3-34 (commit c034ef6), profile `agate-v12r02b60d00-candidate`, `--no-control`, and the PICS profile SM-000028 (version 2).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `476 passed`. New: 15 in `tests/test_point_info.py`, and in `tests/test_pics.py` the converter test extended plus 5 new tests (version 1 loads, version 2 loads, version 3 refused, details need a PICS and a SunSpec key, the shipped SM-000028). Checked they can fail: addresses shifted by one (2 failed); `ha_default` always true (1 failed); Min/Max not read by the converter (1 failed). Each was put back. |
| T2 | Pass | `All checks passed!`, 84 files already formatted |
| T2b | Pass | The local copy of the published spreadsheet has the recorded SHA-256 (`7ee9cfd5…`). Only `version` changed at the top; every implemented and not implemented list is unchanged; 210 points gained details. `702.WMax` min 0, max 10000; `702.WChaRteMaxRtg` certified 0. The sunspec.org link returned a Cloudflare challenge page, not the file, so it was not used. |
| T3 | Pass | 453 points, the same keys as the points answer. All 419 SunSpec points have an address and a PICS status; all 16 raw readings have their address; no label has one. 159 points carry a certified value or Min/Max. 108 points are `ha_default`. No layout warning; the one warning in the log is the existing `Status: value 0 is not named`. |
| T4 | Pass | Full view: 702 (25 rows), 714 (15) and Raw readings (16) agree with `point-info` on Address, PICS, Certified, Min and Max (0 mismatches). 1-based: `702.WMax` 40252 against 40251. Simple view: 108 rows, the four columns, list counts 701 57, 713 5, 714 15, 502 13, Labels 18 (adding up to 108). The choice is still simple after a reload. At 390 px the page is 390 px wide in both views. |
| T5 | Pass | With the API stopped, 27 points read straight from the emulator: all 25 702 points (layout walked from the definition in the test script, not by `points.py`; values scaled by their scale factors), `1.SN` and `714.Prt[1].IDStr`. 0 mismatches against T3. |
| T6 | Pass | My emulator, API and browser stopped with SIGTERM; ports 5122, 8120 and 9223 free; no traceback in the API log. The owner's run on 5120 and 8080 was not touched. |

Found and fixed in T4:

1. The view and address switches showed as the text "[object HTMLButtonElement]": the helper that builds them returned a nested list. Fixed; no unit test covers the page's script, only this browser step.
2. "implemented" broke mid-word in the PICS column; that cell now stays on one line.

The first browser runs had a fault in my test script, not the page: the 1-based choice from one run carried into the next. The script now clears the browser's storage and reloads before signing in.

Seen, not acted on: the emulator's 702 ratings differ from the certified values (for example `702.VMaxRtg` 288 against 270, `702.WChaRteMaxRtg` 5000 against 0). The PICS records the unit that was certified, not this emulator profile, so nothing is compared (section 4, item 4).
