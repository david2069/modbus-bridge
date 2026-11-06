# Test plan: P2 step 12, export a user quirk as a proposal (U11)

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Design U11: "A user quirk can be exported with its reason and evidence, as a proposal for a shipped quirk."

`GET /api/v1/devices/{device}/user-quirks/{kind}/{id}/export` returns one JSON file:

1. **`format`** `modbus-bridge/quirk-proposal`, `version` 1, and `exported` (the time).
2. **`kind`, `id`, `reason`, `source`**, all taken from the item. `source` is the user's evidence: where the fix comes from.
3. **`device`**: the device's Model 1 manufacturer, model, options and firmware. The serial, device id, host and Modbus address are left out, because a proposal is meant to be shared, for example in a public issue.
4. **`switched_off`**: whether the item is switched off now.
5. **`effect`**: the item's effect on the last poll's data, as a list of points with their value, unit and label without the item and with it. The format is the same as the check preview. It is empty when the item is switched off. This is the measured evidence.
6. **`history`**: every audit entry for this item, oldest first, with time, action, version, before, after and reason. `who` and `device` are left out.
7. **`quirk_set`**: a shipped quirk-set file that holds only this item. The id is `proposal-<id>`, at the model layer, matched to the manufacturer and model, so a maintainer can review it, narrow it (for example to a firmware range) and add it. Its `source` is the item's `source` if there is one; otherwise it says it is the user's own measurement on that model and firmware. Before it is sent, the set is loaded with the same checks as a shipped file; if that fails, the answer is 422 with the reason.

Errors: 404 for an unknown user item, 422 for an unknown kind, 409 when user quirks are off, 422 for a device with no Model 1 manufacturer or model.

Nothing is written, and nothing is added to the audit log.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 11.
3. The API on 127.0.0.1:8120 with the FranklinWH set and `--user-quirks <scratch>/user12`.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. an export has every field in section 1, with the reason, source, effect and history of two saves;<br>2. it holds no serial, device id, token or `who`;<br>3. the `quirk_set` loads as a shipped set, at the model layer, and contains only this item;<br>4. a switched-off item exports with `switched_off` true and an empty effect;<br>5. an unknown item gives 404, an unknown kind 422, user quirks off 409;<br>6. without a token the answer is 401;<br>7. an export adds nothing to the audit log. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API. Then:<br>1. `PUT` the user quirk `u-load-kw` (scale 0.001, kW) with a reason and source;<br>2. `PUT` it again with a new reason;<br>3. `GET …/user-quirks/quirk/u-load-kw/export` and save it;<br>4. load its `quirk_set` with `load_sets` in a new Python process. | 1. The export shows the W → kW effect on `label.home_load_power`, two history entries (versions 1 and 2), and `device` with manufacturer, model and firmware.<br>2. The emulator's serial does not appear anywhere in the file.<br>3. The set loads without error. | Any not met |
| T4 | Stop the API and emulator; check ports 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. A rule or reading that uses another user item. Only the one item is exported, so the proposal may need the other item too; the maintainer sees this when they load it.
2. Sending the proposal anywhere. The user downloads the file and shares it as they choose.
3. Values in `effect` and `history` come from the user's own device. They are shared only if the user shares the file.
4. A UI for this; it is an API call for now.

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 11. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `400 passed` (7 new in `tests/test_export.py`, covering items 1–7). The first run failed item 3: the proposed set gave `model` as text, and the shipped-set check refused it (`model must be a non-empty list`). Fixed to a list, then all passed. |
| T2 | Pass | `All checks passed!`, 70 files already formatted |
| T3 | Pass | 1. Both saves answered (versions 1 and 2; the first warned W → kW). 2. The export: `effect` on `label.home_load_power` 711 W → 0.711 kW; `history` versions 1 and 2 with both reasons; `device` FranklinWH, aGate X, options `Emulator 0.2.3`, firmware V12R02B60D00. 3. The emulator's serial and the device id `unit1` appear 0 times in the file. 4. `load_sets` in a new process: `proposal-u-load-kw`, model layer, 1 item. |
| T4 | Pass | Ports 8120 and 5120 free; no traceback in either log; no new macOS crash report. |
