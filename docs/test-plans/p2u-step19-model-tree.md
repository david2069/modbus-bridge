# Test plan: P2U step 19, points grouped by model

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

The owner asked for the Points tab to be easier to read: a list of models on the left, as in a SunSpec explorer, and the chosen model's points on the right (owner, 2026-11-07). It stays read only.

1. **Model names in the device answer.** Each entry of `chain` in `GET /api/v1/devices/{id}` gains `name`: the model's label from the official SunSpec definition we ship (`sunspec_models/json/model_N.json`), such as "DER Capacity" for 702. A model we have no definition for gets `name: null`, and the page shows "unknown model", never a guess.
2. **Left list.** One entry per group, with its point count:
   - "All points" first;
   - each SunSpec model in the chain, as "702 DER Capacity". A model found twice in the chain is shown as `702#2`, as its point keys are;
   - points from quirk sets: `label.*` as "Labels" and `raw.*` as "Raw readings";
   - any other key prefix as its own group, named by the prefix.
   A group with points that have no value shows how many.
3. **Right table.** The chosen group's points with the columns we have today: key, label, value, units and quirks. A point with no value still shows "no value" (rule 8).
4. **Filter.** The filter box narrows the list and the table by key or label. A model whose name matches keeps all its points.
5. **Kept choice.** The chosen group stays chosen across refreshes. If it disappears (for example, after a firmware change), the page goes back to "All points".
6. **Phone width.** Below 700 px the list sits above the table, with no sideways page scroll.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5122, as in step 18. Port 5120 was in use by the owner's own run, which was left alone.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile.
4. A browser for T4: headless Google Chrome, driven over its DevTools port by a scratch script outside the repo, as in step 16. Screenshots are checked by eye.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. every `chain` entry has `name`, taken from the shipped definition;<br>2. a model with no definition gets `name: null`;<br>3. the step 16 page tests still pass (no device data in the page, nothing loaded from outside). | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API; `GET …/devices/unit1` and `GET …/points` | Each chain entry has the right name; points as before | Any not met |
| T4 | Open `/ui`, enter the token and check:<br>1. the left list;<br>2. pick 702, then "Labels";<br>3. filter by `WMax`, then by `capacity`;<br>4. wait two refreshes with 702 chosen;<br>5. a 390 px wide window. | 1. Every model in the chain with its name and a count that matches the points answer; "Labels" and "Raw readings" are there; counts add up to "All points".<br>2. The table shows only that group's points, and values match `GET …/points`.<br>3. `WMax` leaves only groups with matching points; `capacity` keeps the "DER Capacity" and "DER Storage Capacity" models whole.<br>4. 702 stays chosen.<br>5. The list sits above the table; no sideways page scroll. | Any not met |
| T5 | Stop the API, emulator and browser; check ports 8120, 5122 and 9223 are free | All free | Any in use |

## 4. Not covered

1. Address, type, access and PICS columns. Each would be a separate step.
2. Editing anything.
3. A collapsible tree for repeating groups inside a model (such as 714's ports); their points are listed in the model's table by key.
4. A model the device has but our definitions lack. Test 2 in T1 covers the API side; the emulator has none.

## 5. Results

Run on 2026-11-07 with the emulator v0.2.3 (commit af7bc62), profile `agate-v12r02b60d00-candidate`, `--no-control`.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `457 passed` (2 new in `tests/test_ui.py`: names in `chain`; `name: null` for model 64999, which has no definition). The step 16 page tests pass unchanged. |
| T2 | Pass | `All checks passed!`, 82 files already formatted |
| T3 | Pass | 17 models in the chain, each with its name (1 Common, 701 DER AC Measurement, 702 DER Capacity, … 715 DERCtl, 502 Solar Module). 453 points, as before. |
| T4 | Pass | 1. The list shows "All points 453, 2 no value", the 17 models with their names, "Labels 18" and "Raw readings 16". Each count matches the points answer, and they add up to 453. "703 Enter Service" shows "2 no value".<br>2. 702: 25 rows, and all 25 values match `GET …/points` (0 mismatches). Labels: the 18 `label.*` points. 703 shows `ESDlyRemTms` and `ESRndTms` as "no value".<br>3. `WMax` leaves "All points 4/453", "702 2/25" and "704 2/18", with `702.WMax` and `702.WMaxRtg` in the table. `capacity` leaves 702 (25/25) and 713 (5/5), both whole.<br>4. After 125 s (two refreshes at the 60 s interval), 702 is still chosen.<br>5. At 390 px the list sits above the table; the page is 390 px wide (no sideways scroll), and the table scrolls inside its own box. |
| T5 | Pass | My emulator, API and browser stopped with SIGTERM; ports 5122, 8120 and 9223 free; no traceback in the API log. The owner's run on 5120 and 8080 was not touched. |

Found and fixed in T4: keys broke in the middle of a name in the narrower table (for example, `702.AbnOpCa` / `tRtg`). Keys now stay on one line, and the page is 1400 px wide at most (it was 1200).

The first browser run had a fault in my test script, not the page: two steps declared the same variable. Those two steps were run again, fixed.
