# Test plan: P2U step 16, a small read-only web UI

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

Give the owner a page to see what the bridge reads without calling the API by hand. The owner agreed this on 2026-11-07, ahead of P5. It is read only.

1. **Served by the bridge** at `/ui`: one HTML file with plain JavaScript in the package (`src/modbus_bridge/ui/index.html`). There is no build step and nothing is loaded from the internet.
2. **Token.** The page asks for an API token and keeps it in the browser tab only (sessionStorage). The page itself holds no data; every value comes from the token-protected API. A wrong token shows the API's refusal.
3. **Devices.** Each device with its maker, model, firmware and serial, and its state:
   - `refused`, with the reason;
   - `failing`, with the last error;
   - `not ready`;
   - otherwise `live`.
4. **Points.** Key, label, value, units and the quirks that changed the point. A point with no value shows "no value", never blank or 0 (rule 8). A filter box narrows the list by key or label.
5. **Quirks.** The quirk sets that apply, with their sources, and each quirk, reading and rule with its reason, source and state (on, off, failing).
6. **Audit log.** User-quirk changes with time, who, action, item, version and reason. If user quirks are off, the page says so.
7. **Refresh.** The page reloads the device and its points every poll interval. To do this, the device answer gains `interval` (seconds). If a refresh fails, the page says so and shows when the shown values were last fetched, so old values are never shown as live (rule 8).

The API has no read time for each point, so the page shows the time of its last fetch, not of each read.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 15.
3. The API on 127.0.0.1:8120 with the FranklinWH set, the PICS profile and user quirks on.
4. A browser for T4: headless Google Chrome on this Mac, driven over its DevTools port (127.0.0.1:9223) by a scratch script outside the repo, with its own empty profile. Screenshots were checked by eye.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. `GET /ui` gives HTML without a token;<br>2. the page holds no device data (no serial, no value);<br>3. the page loads nothing from outside (no `http://` or `https://` URLs in `src` or `href`);<br>4. the device answer has `interval`;<br>5. the API still refuses data without a token. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API; `GET /ui` and the API answers the page uses | Page served; API answers as expected | Any not met |
| T4 | Open `/ui`, enter the token, and look at each part:<br>1. devices;<br>2. points, including one with no value and the filter;<br>3. quirks;<br>4. audit log, after one user quirk is switched off through the API;<br>5. stop the emulator and wait two polls;<br>6. a wrong token. | 1. The device shows FranklinWH, its firmware and serial, and `live`.<br>2. Values match `GET …/points`; a point with no value shows "no value"; the filter works.<br>3. The FranklinWH set and quirks show with their sources.<br>4. The switch-off shows in the log with its reason.<br>5. The device shows `failing` and its points "no value".<br>6. The refusal is shown and no data. | Any not met |
| T5 | Stop the API and emulator; check ports 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. Browsers other than the one used in T4, and phones.
2. Editing anything: user quirks, switching quirks off, adding devices. Each is a later step.
3. Per-point read times (the API has none).
4. Anyone on the network can load the empty page; the data still needs a token. There is no login beyond the API token.
5. Plain HTTP: the token crosses the network in clear text unless the bridge is put behind HTTPS. This is as for the API today.
6. The bridge cannot start while the device is unreachable, so the page cannot show a device that was never reached.
7. The live event stream (`…/events`) is not used: a browser cannot send the token header on it, so the page polls instead.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 15. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `429 passed` (5 new in `tests/test_ui.py`, covering items 1–5). The one warning is FastAPI's test-client deprecation notice, as in step 15. |
| T2 | Pass | `All checks passed!`, 77 files already formatted |
| T3 | Pass | `GET /ui`: 200, `text/html`. Device answer: `interval` 2.0, FranklinWH V12R02B60D00, no error, not refused. |
| T4 | Pass | 1. Device card: `unit1 live`, FranklinWH · aGate X · firmware V12R02B60D00 · its serial; the token form is hidden after sign-in. 2. Points: compared with `GET …/points` at the same poll sequence, 453 of 453 rows matched; the 2 points with no value (703.ESDlyRemTms, 703.ESRndTms) show "no value"; the filter "reserve" gave the 6 reserve points, and clearing it gave all back. 3. Quirks: the franklinwh set with its source, 3 quirks, 16 raw readings, 18 rules and 4 constants, each with reason, source and state; fwh-q-dermode shows `off` after it was switched off. 4. Audit log: one entry, `token 1 · off · fwh-q-dermode · UI audit test`. 5. Emulator stopped: the card shows `failing` with the error, and all 454 points show "no value" (713.SoC included). With the emulator back, `live` again. Also checked: with the API stopped, the page shows "Refresh failed … The values below were fetched at 15:54:11 and are not live" and greys them out. 6. Wrong token: "The API refused the token (401 …)", no data shown, nothing kept in the tab. |
| T5 | Pass | Ports 8120, 5120 and 9223 free; no traceback in the logs of the final runs. |

Problems found and fixed during T4:

1. The token form stayed visible after sign-in, because its `display: flex` overrode the `hidden` class. `hidden` now always wins. Quirk ids no longer wrap mid-word.
2. The first compare of points had 10 differences, all values that change every poll (energy counters, fine power), because the page and the check fetched about 2 s apart. The compare was redone at one poll sequence, with no differences.
3. One try did not count: the API was restarted while the emulator was stopped, and the API cannot start without the device (existing behaviour, not this step).

All T4 checks were run again on the final page after fix 1.
