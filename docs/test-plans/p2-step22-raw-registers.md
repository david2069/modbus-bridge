# Test plan: P2 step 22, read any register on request

Status: written on 2026-11-17, before the code; run the same day, all passed. Results are in section 5.

## 1. Purpose

The owner decided that a raw value a client asks for is always returned as read, and a quirk never hides it (design 2b, S5; owner, 2026-11-17). Until now a raw register could only be read if a quirk set listed it.

1. **Route.** `GET /api/v1/devices/{id}/registers?address=N&count=C&table=holding|input` reads C registers from N and returns them as read: `{"device", "table", "address", "count", "registers": [words 0–65535]}`. No quirk, scale or type is applied. It needs the token.
2. **Limits.** `address` 0–65535; `count` 1–125 (the Modbus limit), default 1; the registers must not run past 65535; `table` holding (default) or input. Anything else is refused with 422 and nothing is read.
3. **One client (rule 7).** The read takes the same lock as a poll and a test read, so it never runs at the same time as either. It uses the bridge's own connection; no second client is opened.
4. **No silent fallbacks (rule 8).** If the device answers with a Modbus exception (for example illegal address), the answer is 502 with the exception text, never zeros. A timeout or lost link is 503. A device that is not ready, another device found at the address (refused), or a link that was lost and not yet checked again (the next poll checks it), is 503 and nothing is read: the answer must come from the device the bridge was started for.
5. **Read only.** No writes (D10). The read is not added to the audit log, as no setting changes.

## 2. Setup

1. The project `.venv`.
2. The emulator (franklinwh-gateway-emulator) on 127.0.0.1:5122 with `--no-control`. Ports 5120 and 8080 are the owner's run and are left alone.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile SM-000028.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests in `tests/test_registers.py`, on the mock unit:<br>1. holding and input reads return exactly the words stored, at the address asked;<br>2. the default is one holding register;<br>3. each bad request (address −1 or 65536, count 0 or 126, running past 65535, table `coil`, not a number) is 422 and nothing is read;<br>4. a Modbus exception is 502 with its text; a timeout is 503;<br>5. a device not ready, refused, or not checked since the link was lost is 503 and nothing is read;<br>6. the token is needed; an unknown device is 404;<br>7. the read waits while the poll lock is held.<br>To check the tests can fail: return the words shifted by one register. | All pass; the shift fails | Any fails, or the shift passes |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API. Read `40000` count 2 (`SunS`); `40002` count 68 (model 1); a register no model covers, if the emulator refuses it | 0x5375 0x6E53; model 1 words match its points (`1.Mn`, `1.SN`); the refused read is 502 with the exception, not zeros | Any not met |
| T4 | Same run: read 20 times while the poller runs; check the API log | Every read answers; no Modbus desync or overlap error in the log | Any error |
| T5 | Stop the emulator and API; check ports 5122 and 8120 | Both free | Any in use |

## 4. Not covered

1. Coils and discrete inputs (only holding and input registers).
2. A UI for it: the route is API only.
3. Decoding the words into types: the client does that.
4. A limit on how often a client may ask; reads take turns with the poll, so a busy client can slow polling.
5. A real device.

## 5. Results

Run on 2026-11-17 with the emulator v0.2.3-38 (commit 46b0605), profile `agate-v12r02b60d00-candidate`, `--no-control`.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `494 passed` (18 new in `tests/test_registers.py`). Checked they can fail: holding reads shifted by one register gave 5 failures; put back. |
| T2 | Pass | `All checks passed!`, 87 files already formatted |
| T3 | Pass | `40000` count 2: `[21365, 28243]` (0x5375 0x6E53). `40002` count 68: starts `[1, 66]`; the words decode to `1.Mn` "FranklinWH" and to `1.SN`, both equal to the points answer. `30000`, `39999` and `65000`: 502, `IllegalDataAddressError … Modbus Exception 0x02`, no registers. |
| T4 | Pass | 20 reads of model 1 over 12 s while the poller ran every 5 s: all 20 answered with the right words. No desync, overlap or traceback in the API log; the one warning is the existing `Status: value 0 is not named`. |
| T5 | Pass | My emulator and API stopped with SIGTERM; ports 5122 and 8120 free. The owner's run on 5120 and 8080 was not touched. |

Seen, not acted on: the emulator also answers at address 0 (`0` gave 21365, the first word of `SunS`) and at 1000 (65535). They are returned as read, as the route should.
