# Test plan: P2 step 14, check the device again after a reconnect

Status: run on 2026-11-07, all passed. Results are in section 5.

## 1. Purpose

Fix gap G4 from the study `docs/research/fwh-bridge-modbus.md`, which can give wrong data in HA (rule 8). Model 1 is read only at start. After a reconnect the bridge goes on using the identity, model chain and quirks from start-up, so:

- after a firmware update, the firmware quirk layer (L4) is never rebuilt, contrary to design Q3, and a changed model chain is read at the old addresses;
- if another device answers at the same address (for example after a DHCP change), its values are published under the first device's serial.

`modbus-connection` does not reconnect by itself: after a drop, the next request opens a new link. It fires `on_connection_lost` when the transport drops the link, but not when it drops the link itself (for example after a reply that does not match its request).

The fix, in the service:

1. **When to check.** A check is due after `on_connection_lost` fires, and after any poll that failed. A failed poll covers the drops the callback does not report.
2. **The check.** At the next poll, before anything else is read, the service finds SunSpec and reads Model 1 and the chain again. It takes the edit lock and then the poll lock, the same order as an edit, so a quirk edit cannot run in between.
3. **Another device.** If the manufacturer, model or serial differs from start-up, the device is refused:
   - it is not read again until the bridge is restarted;
   - every point becomes unavailable;
   - an error is logged once with both identities, and the API's device answer shows `refused` with the reason.
4. **Same device, changed.** If the firmware, options or model chain changed, the device is set up again without a restart:
   - the identity is updated, so the API shows the new firmware;
   - the quirk set is rebuilt for the new identity, and each quirk set that now applies is logged (Q3);
   - if the chain changed, the implemented points are found again (with the PICS profile, if one is set) and the poller reads the new chain;
   - points that no longer exist are reported as removed.
5. **The check fails.** If SunSpec or Model 1 cannot be read, every point is unavailable for that poll and the check is tried again at the next poll. Nothing is read unchecked.
6. **Nothing changed.** The poll goes on as before.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 13.
3. The API on 127.0.0.1:8120 with the FranklinWH set and the PICS profile, as in step 13.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests, on the mock unit:<br>1. no check while the link stays up (Model 1 is not read again);<br>2. after a lost connection with nothing changed, Model 1 is read once and polling goes on;<br>3. a changed serial refuses the device: all points unavailable, `refused` in the device answer, no reads afterwards, one error logged;<br>4. a changed firmware updates the identity and rebuilds the quirks: a firmware-layer set for the new firmware applies from the next poll;<br>5. a changed chain (a model removed) is read at the new addresses and its points are reported removed;<br>6. a failed check gives all points unavailable and is tried again at the next poll;<br>7. a failed poll makes a check due. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator and API. Then:<br>1. note the device answer and a point value;<br>2. stop the emulator, wait two polls, start it again with the same serial;<br>3. read the device answer and points;<br>4. stop the emulator, start one with another serial on the same port;<br>5. read the device answer and points. | 1. While the emulator is down, the points are unavailable.<br>2. After step 3, the points are live again; the log shows the check and no refusal.<br>3. After step 5, the device answer has `refused` naming both serials, and every point is unavailable; the log has one error. | Any not met |
| T4 | Stop the API and emulator; check ports 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. A device with no serial in Model 1: only the manufacturer and model can be compared, so a swap with another device of the same model is not caught. This is logged at start-up.
2. A real firmware update. The emulator cannot change firmware in place; T1 item 4 covers it on the mock unit.
3. The MQTT publisher reads the device's firmware for HA once, at its own start. After a firmware change, HA shows the old firmware version until the publisher restarts. The values and quirks are right.
4. Taking a refused device back without a restart.

## 5. Results

Run on 2026-11-07 with the same versions as P2 step 13. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `420 passed` (7 new in `tests/test_recheck.py`, covering items 1–7). To check the refusal test can fail, the refusal branch was taken out: the test failed, then the code was put back. |
| T2 | Pass | `All checks passed!`, 74 files already formatted |
| T3 | Pass | The first two tries did not start the emulator, so they are not results: on the first the API started before the emulator was listening (the machine was heavily loaded); on the second a zsh variable holding the emulator command was not split into words, as in step 10. The third try used a shell function. 1. Start: serial `MOCK0001EFC63F0CD0E8`, 451 of 453 points available, 713.SoC 40.0. 2. Emulator stopped: 0 of 453 available; `last_error` "not checked after a reconnect: ModbusConnectionError …". 3. Same serial back: 451 of 453 available, no refusal; log `checked after a reconnect: unchanged`. 4. Another serial (`MOCKOTHER0000000002`, a placeholder): `refused` names both serials, 0 of 453 available; one ERROR in the log. |
| T4 | Pass | Ports 8120 and 5120 free; no traceback in any log of the third try; no new Python crash report. |

Change after the live run: the log showed the failed-check warning at every poll (every 2 s) while the emulator was down. It is now logged once at WARNING per outage and at DEBUG after that, and a doubled word in the message was removed. T1 and T2 were run again after this change (results above); T3 was not.
