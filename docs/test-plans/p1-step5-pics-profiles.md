# Test plan: P1 step 5, implemented points from a PICS (D6.3)

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that modbus-bridge can:

1. convert a published SunSpec PICS spreadsheet into a profile file (data) with a script,
2. keep personal data out of the profile: nothing from the "Testing Info" sheet, and only the product fields of "Certification Info",
3. use the profile to sort points into implemented or not implemented for the models it covers,
4. sort models the PICS does not cover by discovery (D6.5),
5. report where the PICS and the device disagree:
   1. "certified, no value": the PICS says implemented, but the device gave no value on every read. The point stays implemented and shows as unavailable (D6.2).
   2. "value, not certified": the PICS says unimplemented, but the device gave a value. The point becomes implemented, and this is logged (D6.4).

## 2. Setup

1. The project `.venv` with the dev extras, which now include `openpyxl` for the converter script only.
2. The PICS: FranklinWH SM-000028, published at <https://sunspec.org/wp-content/uploads/2009/03/UPDATED_FranklinWH_Modbus_PICS_SM-000028.xlsx>. The owner's downloaded copy is used, because the site refuses automated downloads. The spreadsheet itself is not committed.
3. The emulator at tag v0.2.3 (commit af7bc62), one instance:
   `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`
4. Only one Modbus client at a time (rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: (a) PICS point names convert to our keys, e.g. `Crv.1.MustTrip.Pt.1.V` to `Crv[1].MustTrip[1].Pt[1].V`; (b) the converter, run on a small made-up spreadsheet, keeps only the allowed certification fields and ignores "Testing Info"; (c) a PICS-covered point follows the PICS; (d) an uncovered model follows discovery; (e) both kinds of disagreement are reported and handled as in 1.5. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Convert the FranklinWH PICS: `.venv/bin/python scripts/convert_pics.py <xlsx> --source-url <url above>` | Writes `src/modbus_bridge/pics_profiles/SM-000028.json` with models 1 and 701–715. The file has no `@` character and no field other than those listed in the converter. | Error, missing models, or any personal data |
| T4 | Start the emulator (setup 3) | Listens on 127.0.0.1:5120 | Does not start |
| T5 | `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5120 --unit 1 --points --pics src/modbus_bridge/pics_profiles/SM-000028.json` | Exit code 0. The summary names PICS SM-000028 as the source for models 1 and 701–715, and discovery for 502. Disagreements are listed by kind. The counts add up to 642. | Error, wrong sources, or counts that do not add up |
| T6 | Stop the emulator and check port 5120 is free | Free | Still running |

## 4. Not covered

1. Choosing a profile automatically from Model 1 (Mn, Md). That is the catalogue (design 2a), a later step. Here the profile is given on the command line.
2. Whether the emulator or the PICS is right when they disagree. The disagreements are reported, not judged.
3. The Sigenergy PICS. It uses the same layout and is converted later, when Sigenergy is worked on.
4. A real device.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, openpyxl (dev only), pytest 9.2.0 and ruff 0.17.3. Emulator v0.2.3 (commit af7bc62). PICS file SHA-256 `7ee9cfd5…2336`, the same for the owner's Downloads copy and the copy in franklinwh-modbus-bridge.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `135 passed`, including 9 new PICS tests |
| T2 | Pass | `All checks passed!`, no files to reformat |
| T3 | Pass | `SM-000028.json` with models 1 and 701–715: 455 implemented and 222 unimplemented entries. No `@`. Fields: certificate, issued, certificate_url, manufacturer, product_name, product_models, source_url, source_sha256, models. |
| T4 | Pass | Listening on 127.0.0.1:5120 |
| T5 | Pass | Exit code 0. `Points: 421 implemented, 221 not implemented (PICS SM-000028; discovered for model 502 (discovered over 3 reads))`. 421 + 221 = 642. |
| T6 | Pass | Port 5120 free after the stop |

PICS comparison from T5:

1. Certified, no value (2): 703.ESDlyRemTms, 703.ESRndTms. They stay implemented and show as unavailable.
2. Value, not certified (5): 701.DERMode, 704.WSetEnaRvrt, 704.WSetRvrt, 704.WSetRvrtRem, 704.WSetRvrtTms. They become implemented.
3. Not listed in the PICS: 0. Every point we read for models 1 and 701–715 matched a PICS entry, so the name conversion works.
4. In the PICS, no point read: 52. That is 51 scale factors (applied to other points, not shown) and 1.Pad.

These are differences between the emulator and the published PICS. This test does not judge which is right (section 4.2).
