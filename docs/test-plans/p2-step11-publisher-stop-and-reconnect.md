# Test plan: P2 step 11, publisher marks offline on any stop and survives a lost broker

Status: run on 2026-11-06, all passed. Results are in section 5.

## 1. Purpose

Fix two gaps found in step 10 that give wrong data in HA today (rule 8):

- **A clean stop leaves the device `online`.** Ctrl-C ends the publisher with a clean MQTT disconnect, so the broker does not send the last-will `offline`. HA shows every last value as live.
- **A lost broker ends the publisher.** Only API errors are retried. After a broker restart nothing publishes again, and a broker that keeps retained messages still shows the device `online` with frozen values.

The fix, in the publisher only:

1. **Any stop marks the device offline.** On Ctrl-C (SIGINT) and SIGTERM the publisher publishes `offline` to the device availability topic, then disconnects. SIGTERM is turned into the same orderly stop as Ctrl-C. If the broker cannot be reached at that moment, the stop goes ahead, and the broker's last will covers the dropped connection. A crash or SIGKILL is covered by the last will, as now.
2. **Broker loss is retried.** If the broker cannot be reached at start, or the connection is lost while running, the publisher logs a warning, waits 5 s and connects again, as it already does for the API. On reconnect it starts again from a fresh snapshot, so every entity, state and `online` is published again.

## 2. Setup

1. The project `.venv`.
2. The emulator v0.2.3 (commit af7bc62) on 127.0.0.1:5120, as in step 10.
3. The API on 127.0.0.1:8120 with the FranklinWH set.
4. The scratch broker (amqtt 0.12.1) on 127.0.0.1:18830, and the publisher.
5. `scripts/launch_int.py` in the scratchpad, to start the publisher with Ctrl-C handling restored and send it a signal (a background job from a script ignores Ctrl-C otherwise).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests:<br>1. on cancel (the path of Ctrl-C and SIGTERM) the publisher publishes `offline`, then leaves;<br>2. if that publish fails, the stop still goes ahead with no error;<br>3. a broker error while running leads to a new connection and a new snapshot;<br>4. a broker that cannot be reached at start is retried;<br>5. SIGTERM is handled as an orderly stop. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher. Then:<br>1. stop the publisher with Ctrl-C (SIGINT) and read the device availability;<br>2. start it again, stop it with SIGTERM, read the availability;<br>3. start it again; stop the broker for 15 s, then start it again;<br>4. read the retained messages. | 1. After step 1: `offline`; exit code 0.<br>2. After step 2: `offline`; exit code 0.<br>3. During step 3 the publisher logs the lost broker and its retries, and does not exit.<br>4. After step 3: the device is `online` and all 456 configs are retained again; the publisher logs a new snapshot. | Any not met |
| T4 | Stop the publisher, broker, API and emulator; check ports 18830, 8120 and 5120 are free | All free | Any in use |

## 4. Not covered

1. A broker that keeps retained messages across its restart (the scratch broker does not). The publisher sends a full snapshot on reconnect either way, so the result in HA is the same.
2. A real HA instance and a real Mosquitto broker.

## 5. Results

Run on 2026-11-06 with the same versions as P2 step 10. Emulator v0.2.3 (commit af7bc62), broker amqtt 0.12.1 (scratch only).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `393 passed` (5 new in `tests/test_publisher_lifecycle.py`, covering items 1–5) |
| T2 | Pass | `All checks passed!`, 68 files already formatted |
| T3 | Pass | 1. SIGINT: exit code 0, log `Device marked offline`, `Stopped`; availability `offline`. 2. SIGTERM: the same. 3. Broker stopped for 15 s: the publisher logged `Could not mark the device offline (… not currently connected); the last will covers it`, then `MQTT broker lost or not reachable` four times (one lost connection, three refused), and kept running. 4. After the broker restarted: `Publishing unit1 …`, `Snapshot: 456 points, 1367 messages`; availability `online` and 456 configs retained. |
| T4 | Pass | Ports 18830, 8120 and 5120 free; no traceback in any log; no new macOS crash report. |
