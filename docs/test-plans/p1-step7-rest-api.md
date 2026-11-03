# Test plan: P1 step 7, the REST API (D7, D9, D12)

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that the device model is served over a REST API that:

1. puts every path under `/api/v1` (D12.1),
2. needs an API token for everything except `/api/v1/health` (D12.2),
3. lists the device, its identity, its model chain, where its implemented points came from and the not-implemented list (diagnostics, D6.1),
4. gives a full snapshot of the implemented points only, with an unavailable value shown as `null` and `"available": false`,
5. streams changes as server-sent events: one `snapshot` event first, then a `change` event per changed point (D9),
6. holds the only Modbus connection to the device (rule 7). There are no writes (D10).

## 2. Setup

1. The project `.venv` with `fastapi>=0.115,<1` and `uvicorn>=0.30,<1` (runtime) and `httpx` (dev, for the test client).
2. The emulator at tag v0.2.3 (commit af7bc62), one instance on 127.0.0.1:5120, as in step 6.
3. A token file in the scratch folder, outside the repo, holding a random token.
4. The API on 127.0.0.1:8120 only:
   `.venv/bin/python -m modbus_bridge.serve --device-host 127.0.0.1 --device-port 5120 --unit 1 --pics src/modbus_bridge/pics_profiles/SM-000028.json --interval 2 --listen-port 8120 --token-file <scratch>/token`

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests against the mock: (a) no token or a wrong token gives 401; (b) health needs no token; (c) the device list and device detail; (d) the points snapshot has only implemented points, and enums carry number and name; (e) an unavailable point is `null` with `"available": false`; (f) the event stream starts with a snapshot, then gives one change event after a value changes. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator, then the API (setup 4) | Both listen | Either does not start |
| T4 | `curl` health without a token; `/api/v1/devices` without and with the token | 200; 401; 200 with one device | Any other status |
| T5 | `curl` `/api/v1/devices/{id}/points` with the token | 422 points, 502.Stat is `{"value": 0, "name": "UNKNOWN"}` | Wrong count or shape |
| T6 | `curl -N --max-time 7` on `/api/v1/devices/{id}/events` with the token | First a `snapshot` event, then at least one `change` event | No snapshot, or no changes in 7 s |
| T7 | Stop the API and the emulator; check ports 8120 and 5120 are free | Both free | Either still in use |

## 4. Not covered

1. The MQTT publisher (step 8).
2. Writes (D10, phase P2W).
3. Several devices. The API has a device list, but this step serves one.
4. TLS. The API listens on 127.0.0.1 only in this test.
5. Users and browser sessions (D12.2: those are for people, later with the UI).

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, fastapi 0.162.0, starlette 1.10.0, uvicorn 0.54.0, httpx 0.28.1, pytest 9.2.0 and ruff 0.17.3. Emulator v0.2.3 (commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `148 passed`, including 6 new API tests covering (a)–(f) |
| T2 | Pass | `All checks passed!`, no files to reformat |
| T3 | Pass | Emulator on 127.0.0.1:5120, API on 127.0.0.1:8120 |
| T4 | Pass | Health 200 without a token; devices 401 without and 200 with the token, one device `unit1`, 422 implemented points |
| T5 | Pass | 422 points; `502.Stat` `{"value": 0, "name": "UNKNOWN"}`; `713.SoC` 40.0 Pct; unavailable: 703.ESDlyRemTms and 703.ESRndTms only |
| T6 | Pass | In 7 s: 1 `snapshot` event, then 6 `change` events (e.g. 713.WHAvail, 714.DCW). curl ended by its time limit (exit 28), as intended. |
| T7 | Pass | Ports 8120 and 5120 free; no errors in the API log |

Note: the test run warns that using `httpx` with Starlette's test client is deprecated in favour of `httpx2`. It does not affect the results.
