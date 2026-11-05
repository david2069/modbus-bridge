# Test plan: P2 step 6, user quirks (L5) through the REST API

Status: run on 2026-11-05, all passed. Results are in section 5.

## 1. Purpose

Check user quirks (design 2b, U1–U4, U6, U7, U9, U10) through the REST API. Each change takes effect from the next reading, with no restart (Q2).

1. **Layer.** `user` is a fifth layer, above firmware, so a user item wins over any shipped one (U10). Shipped quirk-set files may not use it.
2. **Storage.** `serve --user-quirks DIR` keeps one file per device, `DIR/<device-id>.json`. It holds the user's items (point quirks, readings, constants and rules, in the quirk-set format) and the ids the user has switched off. It is written whole to a new file and then renamed over the old one, so a crash leaves the old file intact. Without `--user-quirks`, the read endpoint says user quirks are off and the write endpoints answer 409.
3. **Endpoints** (all need the API token):
   - `GET /api/v1/devices/{id}/user-quirks`: the items and the off list.
   - `POST …/user-quirks/check` with `{"kind", "item"}`: checks the item and returns a preview without saving.
   - `PUT …/user-quirks/{kind}/{item-id}`: checks, saves and activates an item (create or replace). Returns the preview.
   - `DELETE …/user-quirks/{kind}/{item-id}`: removes it; the point falls back to the layer below (U7).
   - `PUT` and `DELETE /api/v1/devices/{id}/quirks/{item-id}/off`: switch any item, shipped or user, off or back on (U6). An id switched off with `--quirk-off` cannot be switched on here.
   - `kind` is `quirk`, `reading`, `constant` or `rule`.
4. **Checks before saving (U1, U2).**
   - A reason is required.
   - Only the fields and values each kind already allows are accepted.
   - Ids must be unique across shipped and user items.
   - An item that would clash with another user item (same change on the same point, or the same reading name, constant name or rule output) is refused.
   - Rules must not loop.
   - A new or changed reading gets a test read. If the device refuses it, the item is refused with the Modbus error.
   - Any failed check answers 422 with the reason, and nothing changes.
5. **Preview (U3).** For each point the item changes, the preview shows the current state next to the new one: value, units, label, whether the point is added or removed, and any rule error. It is worked out from the last poll's data, plus the test read.
6. **Activate (U4).** After a save the device's quirks are rebuilt and used from the next poll. The quirks endpoint lists the item at layer `user` with its reason. Points carry its id.
7. **Errors while running (U9)** work as for shipped items: no value, and the item shows as `failing`. A rebuild keeps each rule's remembered flag (latch).
8. **One Modbus client.** The test read uses the device's own connection and takes turns with polling, so two reads never overlap.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 4.
3. The API on 127.0.0.1:8120 as in step 4, with `--quirks src/modbus_bridge/quirk_sets/franklinwh.json` and `--user-quirks <scratch>/user`.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. the file is saved, reloaded and survives a restart;<br>2. a bad file stops start-up with a clear error;<br>3. each kind can be created, replaced and removed;<br>4. refusals: missing reason, unknown field, duplicate id (user or shipped), clash, loop, test read refused by the device, id in the URL not matching the body, unknown kind;<br>5. the preview shows before and after;<br>6. the change shows at the next poll without a restart;<br>7. a user quirk overrides a shipped one, and removing it falls back;<br>8. switching off and on, kept in the file; a `--quirk-off` id cannot be switched on;<br>9. 409 without `--user-quirks`;<br>10. a shipped file with layer `user` is refused. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and the API. Then:<br>1. `check` a user quirk `u-load-kw` on `label.home_load_power` with scale 0.001, units kW and a reason;<br>2. `PUT` it;<br>3. after the next poll, `GET …/points` and `GET …/quirks`;<br>4. `PUT` a user reading `u-r-15000` (15000, uint16) and a rule `u-n-15000` on it;<br>5. `PUT …/quirks/fwh-n7-r5/off`;<br>6. restart the API;<br>7. `DELETE` the user quirk and `DELETE …/quirks/fwh-n7-r5/off`. | 1. The preview shows W → kW with the value / 1000.<br>2. The save answers 200.<br>3. The point shows kW with `u-load-kw` in its quirks; the quirks endpoint shows it at layer `user`, `active`, with its reason.<br>4. `raw.u15000` and `label.u15000` appear at the next poll with the emulator's value.<br>5. `label.battery_operating_mode` is gone; `fwh-n7-r5` is `off`.<br>6. After the restart, the user items and the off state are back.<br>7. Home load is back in W and `battery_operating_mode` is back.<br>No restart is needed for 2–5 and 7. | Any not met |
| T4 | Refusals live: `PUT` a quirk with no reason, and a reading at an address the emulator refuses | 422 for each, with the reason, and nothing changes | Otherwise |
| T5 | Stop the API and emulator; check ports 5120 and 8120 are free | Both free | Either in use |

## 4. Not covered

1. Versions of each edit and the audit log (U5, U8): the next step.
2. Telling HA to remove an entity that a removed or hiding quirk took away (Q4, U7). The point leaves the API snapshot, but no "removed" event is sent yet, so the MQTT entity stays until restart.
3. A UI. Only the REST API is used.
4. Export as a proposal (U11), and warnings before a unit or scale change (Q4).

## 5. Results

Run on 2026-11-05 with the same versions as P2 step 5. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `367 passed` (17 new in `tests/test_user_quirks.py`) |
| T2 | Pass | `All checks passed!`, 57 files already formatted |
| T3 | Pass | 1. Preview: `label.home_load_power` 2056 W → 2.056 kW, label unchanged. 2. `PUT` 200. 3. Next poll: 2.057 kW, quirks `fwh-n1-r2`, `u-load-kw`; quirks endpoint `u-load-kw` at layer `user`, `active`, reason "I read power in kW". 4. Test read 0; `raw.u15000` and `label.u15000` 0 at the next poll (the emulator holds 15000 at 0). 5. `label.battery_operating_mode` absent; `fwh-n7-r5` `off`. 6. After an API restart: kW, both user items and the off state back. 7. Home load back to 2054 W with `fwh-n1-r2` only; `battery_operating_mode` back as `self_consumption`. No restart for 2–5 and 7. The log has one line per save, removal and switch. |
| T4 | Pass | No reason: 422 `quirk is missing reason`. Address 30000: 422 `test read of u-r-bad failed: … Modbus Exception 0x02`; 15600 the same. Nothing saved for either. Two other addresses tried while looking for a refused one (40000 and 15100) read fine and were saved, as designed; that reading was then removed with `DELETE`. |
| T5 | Pass | Ports 5120 and 8120 free; no traceback in either log. |
