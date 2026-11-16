# Test plan: P2U step 21, the points table fits its page

Status: written on 2026-11-16, before the change; run the same day. T4 fails at 1400 px on "All points" (see section 5); everything else passed. Items 1 and 2 and T3 were amended during the run, after the first T3 (see section 5): breaks after a hyphen are allowed, and Access was renamed.

## 1. Purpose

The owner's screenshot of step 20 (about 1000 px wide) showed the full view of the points table cut off on the right (Max and Quirks out of sight) and text broken mid-word: "uin / t16", "Frankl / inWH" (owner, 2026-11-16). The cause: table cells may break a line at any character, so the browser squeezes 12 columns until words break.

1. **No word broken mid-word.** Table text wraps only at spaces and after a hyphen ("Var-" / "Hours"), as ordinary text does. A point key may also break before a dot (`707.Crv[1].MustTrip[1]` / `.Pt[1].Tms`), never inside a name. An address range ("40020–40035") stays on one line. A word that cannot fit makes its column wider; it is never split.
2. **Fewer and narrower columns.** Min and Max become one column, Range ("0 – 10000", or "≥ 5" / "≤ 10" with only one end), so the full view has 11 columns. Access is headed "R/W", as in the PICS. Cells have less padding at the sides.
3. **Fits where it can.** At 1400 px and wider, the full view shows every column with no sideways scroll. Narrower, the table scrolls inside its own box (never the page), and the Key column stays in sight while it scrolls.
4. Nothing else changes: the same values, the simple view, the address switch and the API.

## 2. Setup

1. The project `.venv`.
2. The emulator (v0.2.3-34, commit c034ef6) on 127.0.0.1:5122 with `--no-control`. Ports 5120 and 8080 are the owner's run and are left alone.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile SM-000028.
4. Headless Google Chrome on DevTools port 9223, driven by a scratch script outside the repo.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest` | All pass (the page tests check no device data and nothing loaded from outside) | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Full view, "All points", at 1920, 1400, 1000 and 390 px wide. For every table cell, check each word (text between spaces and hyphens) renders on one line; a key's parts are checked the same way | No word split over two lines at any width | Any split word |
| T4 | Same widths: compare the table's scroll width with its box, and the page's with the window | At 1920 and 1400: no sideways scroll in the table. At all widths: the page itself never scrolls sideways | Any not met |
| T5 | At 1000 px, scroll the table box to the far right | The Key column is still in sight; the Range and Quirks columns are reachable | Any not met |
| T6 | Full view: 702 `WMax` and `VAMax`; a point with no Range | Range reads "0 – 10000" and "0 – 11000"; empty where the PICS gives none; Certified, Address and PICS unchanged from `point-info` | Any not met |
| T7 | Simple view at 1000 and 390 px | Four columns, no split words, no page scroll | Any not met |
| T8 | Stop the emulator, API and browser; check ports 5122, 8120 and 9223 | All free | Any in use |

## 4. Not covered

1. Screens other than headless Chrome (Safari, which the owner uses, is checked by the owner's eye only).
2. Very long values, such as a long bitfield name list: they wrap at spaces, so a row can grow tall.

## 5. Results

Run on 2026-11-16 with the emulator v0.2.3-34 (commit c034ef6), profile `agate-v12r02b60d00-candidate`, `--no-control`, and headless Chrome.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `476 passed` |
| T2 | Pass | `All checks passed!`, 85 files already formatted |
| T3 | Pass | No split word in the full view at 1920, 1400, 1000 or 390 px. |
| T4 | **Fail at 1400 px** | 1920 px: the table is 1504 px in a 1504 px box, so no scroll. **1400 px, "All points": 1133 px in a 1104 px box, 29 px too wide**, so it scrolls inside its box. The 702 group fits at 1400 px. The page never scrolls sideways at any width (1920, 1400, 1000, 390). |
| T5 | Pass | At 1000 px, scrolled to the far right: Key still in sight; Range and Quirks inside the box. |
| T6 | Pass | 702: `WMax` "0 – 10000", `VAMax` "0 – 11000", `WMaxRtg` empty; Range, Certified, Address and PICS agree with `point-info` on all 25 rows. |
| T7 | Pass | Simple view: four columns, no split word, and the table fits its box at 1000 and 390 px. |
| T8 | Pass | My emulator, API and browser stopped with SIGTERM; ports 5122, 8120 and 9223 free; no traceback in the API log. The owner's run on 5120 and 8080 was not touched. |

Why T4 fails at 1400 px: every column is already as narrow as its longest word that may not break. The widest are Value (the serial number, one word), Key, Address ranges and Range. Together they need 1133 px. Fitting would mean narrowing the model list on the left or the cell padding further; that was not done without the owner's say. The owner accepted the 29 px at 1400 px as it stands (2026-11-16): the table scrolls inside its box there, with the Key column frozen.

Changed during the run, after the first T3:

1. Breaks after a hyphen ("Var-" / "Hours") are allowed, as in ordinary text; the plan said spaces only.
2. Address ranges broke after their dash ("40020–" / "40035"); they now stay on one line.
3. Keys may break before a dot and after an underscore (`label.solar_` / `remote_installed`), never inside a name.
4. Access is headed "R/W"; side padding in table cells is 7 px (was 10).
5. The page may be up to 1800 px wide (was 1400), so wide screens give the table more room.
6. The frozen Key column has a line on its right edge. Without it, the end of a half-hidden cell beside it (for example "ld32" of "bitfield32") looked like part of the key.
