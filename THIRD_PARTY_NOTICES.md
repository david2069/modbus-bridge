# Third-party notices

This project is MIT-licensed (see `LICENSE`). It includes the work below, under its own licence.

## 1. SunSpec model definitions

- Repo: <https://github.com/sunspec/models>
- Path: `json/model_*.json`
- Commit: `90b4a331dcca1d6eac69c1bead952fddcc5852e0` (2026-08-20)
- Licence: Apache License 2.0. The full text is in `src/modbus_bridge/sunspec_models/LICENSE`.
- Copyright: the repo states no copyright line. The SunSpec Alliance publishes it.
- Where it is used here: `src/modbus_bridge/sunspec_models/json/`, unmodified. `src/modbus_bridge/sunspec_models/generated/` is generated from those files by `scripts/generate_sunspec_models.py`, using the generator in modbus-connection (below).

## 2. modbus-connection

- Repo: <https://github.com/home-assistant-libs/modbus-connection>
- Licence: Apache License 2.0
- Where it is used here: a runtime dependency (`>=4.12.7,<5`), not copied. Its SunSpec generator produced the files in `src/modbus_bridge/sunspec_models/generated/`.

## 3. FranklinWH SunSpec PICS (certificate SM-000028)

- Source: published by the SunSpec Alliance, <https://sunspec.org/wp-content/uploads/2009/03/UPDATED_FranklinWH_Modbus_PICS_SM-000028.xlsx>. Certificate: <https://sunspec.org/wp-content/uploads/2024/04/Franklin-WH-Certificate-SM000028.pdf>.
- File checked: SHA-256 `7ee9cfd55f54121167531efc8e11ea3581449a945675c281a514427270142336`.
- Where it is used here: `src/modbus_bridge/pics_profiles/SM-000028.json`, made by `scripts/convert_pics.py`. Only the product fields and, for each point, whether it is implemented are kept. The spreadsheet itself is not included, and nothing from its "Testing Info" sheet is copied.
