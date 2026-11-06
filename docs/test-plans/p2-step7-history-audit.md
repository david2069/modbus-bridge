# Test plan: P2 step 7, edit history and audit log for user quirks

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Check versions of each user-quirk edit (design U5) and the audit log (U8).

1. **Audit log.** Every change through the API adds one entry to `DIR/<device-id>.audit.jsonl`, next to the user-quirks file. An entry holds:
   - `time` (UTC, ISO 8601), `who`, `device`;
   - `action`: `save`, `remove`, `off` or `on`;
   - `kind` and `id` of the item (no kind for `off` and `on`, which work on any item);
   - `version` of the item after a save;
   - `before` and `after`: the whole item for `save` and `remove` (`null` where there is none), and the off state (`true` or `false`) for `off` and `on`;
   - `reason`: the item's reason for a save, and the reason given (optional) for the rest.
2. **Who.** API tokens have no names, so `who` is `token N`, N being the token's place in the token file (blank lines are not counted). The token itself is never logged.
3. **Versions (U5).** Each save of an item id is a new version: 1, 2, 3 and so on. The previous version is kept in the log, because each `save` entry holds the old item as `before`. Version numbers carry on after a remove and a later save of the same id.
4. **Order.** The user-quirks file is saved first, then the entry is added. If the entry cannot be written, the old file is put back, the change is not used, and the API answers with an error. A refused change (422) writes no entry.
5. **Reading it back.**
   - `GET /api/v1/devices/{id}/user-quirks/audit`: all entries, oldest first. `?id=X` keeps only entries for item X. It is also the export: plain JSON.
   - `GET …/user-quirks/{kind}/{item-id}/versions`: each saved version of the item, with its number, time, who and reason, oldest first.
   - Remove, off and on take an optional `?reason=` that goes into the entry.
6. **Start-up.** The log is read when the bridge starts, to know each item's last version. A broken line stops start-up with the file name and line number, as a broken user-quirks file does.
7. **Without `--user-quirks`** the audit and versions endpoints answer 409, like the change endpoints.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 6.
3. The API on 127.0.0.1:8120 as in step 6, with `--user-quirks <scratch>/user` and a token file of two lines.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. save, replace, remove, off and on each add one entry with the right fields;<br>2. `who` is the token's place in the file, and the token is not in the file;<br>3. versions count 1, 2, 3, also across a remove and re-save;<br>4. `before` of each save is the previous version;<br>5. `?id=` filters; the versions endpoint lists each version;<br>6. `?reason=` on remove, off and on is logged;<br>7. a refused change adds no entry;<br>8. a failed log write puts the old file back and the change is not used;<br>9. versions carry on after a restart;<br>10. a broken log stops start-up;<br>11. 409 without `--user-quirks`. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and the API. Then:<br>1. with token 1, `PUT` user quirk `u-load-kw` (scale 0.001, kW);<br>2. with token 2, `PUT` it again with a new reason;<br>3. `PUT …/quirks/fwh-n7-r5/off?reason=…`, then `DELETE` the same;<br>4. `DELETE` `u-load-kw` with a reason;<br>5. `GET …/user-quirks/audit` and `GET …/user-quirks/quirk/u-load-kw/versions`;<br>6. restart the API, `PUT` `u-load-kw` once more. | 1. Five entries, in order: save, save, off, on, remove.<br>2. `who` is `token 1` for the first and `token 2` for the second.<br>3. Versions 1 and 2; the second `before` equals the first item.<br>4. The reasons are in the entries.<br>5. The versions endpoint lists 1 and 2.<br>6. After the restart the new save is version 3.<br>7. Neither token appears in the log file. | Any not met |
| T4 | Stop the API and emulator; check ports 5120 and 8120 are free | Both free | Either in use |

## 4. Not covered

1. A UI to show the log (U8). Only the REST API is used.
2. Putting an old version back with one call. A user can `PUT` the old item from the versions list.
3. Trimming or rotating the log. It grows by one line per change, which is small at home scale.
4. Changes made by editing the file by hand while the bridge is stopped. They are not in the log.
5. Support info (U8) and export as a proposal (U11).

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 6. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `374 passed` (7 new in `tests/test_audit.py`, covering items 1–11) |
| T2 | Pass | `All checks passed!`, 59 files already formatted |
| T3 | Pass | 1. Entries in order: save, save, off, on, remove. 2. `who`: `token 1`, then `token 2`, then `token 1` for the rest. 3. Versions 1 and 2; the second entry's `before` equals the first's `after`. 4. Reasons logged: "I read power in kW", "kW suits my dashboard", "testing without mode", "mode back", "back to W". 5. The versions endpoint lists 1 (token 1) and 2 (token 2). 6. After an API restart the new save answered version 3. 7. Neither token is in the log file (7 lines after the last removal). The service log has one line per change with version, who and reason. |
| T4 | Pass | Ports 5120 and 8120 free; no traceback in either log. |
