# Test plan: P1 step 8, the MQTT Discovery publisher (D8)

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that a publisher, running as a client of the REST API (D7), puts the device into Home Assistant through MQTT Discovery:

1. one HA device per unit (D5), identified by its Model 1 serial. With no serial, the publisher refuses to start and says why; it never makes one up.
2. one entity per implemented point, named with its SunSpec label and point name. Not-implemented points get no entity (D6.1).
3. units as the device reports them (D2), mapped to HA's spelling (Pct to %, Var to var). Power, energy, voltage, current, frequency and temperature get HA device classes. Lifetime energy counters are `total_increasing`; energy ratings and stored energy are not.
4. an unavailable point shows as unavailable in HA through its own availability topic, never as 0 or an old value (rule 8). If the API or the device is lost, the device shows offline.
5. enums are published by name; an enum value SunSpec does not name shows as `UNKNOWN (n)`.
6. measurement models (inverter, meter, storage, battery and DER measurement models) are enabled by default. Settings and curve models are created but disabled by default, so HA is not flooded.

Topics, with `<p>` the prefix (`modbus_bridge`), `<d>` the device id (from the serial) and `<s>` the point slug:

| Topic | Retained | Payload |
|---|---|---|
| `homeassistant/sensor/<p>_<d>_<s>/config` | yes | discovery JSON |
| `<p>/<d>/<s>/state` | yes | the value as text |
| `<p>/<d>/<s>/available` | yes | `online` / `offline` |
| `<p>/<d>/availability` | yes | `online` / `offline` (also the MQTT last will) |

## 2. Setup

1. The project `.venv` with `aiomqtt>=2.3,<3` and `httpx` (now runtime, for the event stream).
2. A test MQTT broker: amqtt 0.12.1 in its own scratch virtual environment, on 127.0.0.1:18830 only, anonymous, stopped afterwards. Home Assistant is not used in this step.
3. The emulator (v0.2.3, commit af7bc62) on 127.0.0.1:5120 and the API on 127.0.0.1:8120, as in step 7, with the same scratch token file.
4. The publisher: `.venv/bin/python -m modbus_bridge.mqtt --api-url http://127.0.0.1:8120 --token-file <scratch>/token --device-id unit1 --mqtt-host 127.0.0.1 --mqtt-port 18830`

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: slugs; HA unit, device class and state class mapping; enum and unknown enum text; unavailable gives `offline`; enabled-by-default rule; event-stream parsing; discovery payload contents; refusal without a serial. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the broker, emulator, API and publisher | All four running, publisher logs that it is publishing | Any fails to start |
| T4 | Subscribe to `homeassistant/#` and `modbus_bridge/#` for 8 s with `amqtt_sub` and count | 422 config topics; device availability `online`; 713.SoC state with `"unit_of_measurement": "%"` and `"device_class": "battery"` in its config; the two 703 points certified without a value are `offline`; at least one state message changes during the 8 s | Any of these not met |
| T5 | Stop the API. Check retained device availability | `offline` within 15 s | Still `online` |
| T6 | Stop publisher, broker and emulator; check ports 18830, 8120 and 5120 are free | All free | Any still in use |

## 4. Not covered

1. Home Assistant itself. The discovery messages are checked on the broker only. Seeing the device and entities in a real HA (on a test VM, as in the handover's takeover test) is a separate test.
2. Removing entities that stop being implemented (design 2b Q4).
3. Commands from HA (writes are phase P2W, D10).
4. Neutral labels and the old bridge's entity names, which come with P2 and P4.
5. MQTT broker login and TLS.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, fastapi 0.162.0, uvicorn 0.54.0, httpx 0.28.1, aiomqtt 2.5.1 (paho-mqtt 2.1.0), pytest 9.2.0 and ruff 0.17.3. Broker amqtt 0.12.1 (scratch only). Emulator v0.2.3 (commit af7bc62). The emulator's serial is shown as `<serial>`.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `164 passed`, including 16 new publisher tests |
| T2 | Pass | `All checks passed!`, no files to reformat |
| T3 | Pass | Broker 127.0.0.1:18830, emulator 127.0.0.1:5120, API 127.0.0.1:8120. Publisher: `Publishing unit1 to MQTT under modbus_bridge/<serial>`, `Snapshot: 422 points, 1265 messages` (422 config + 420 × state and online + 2 offline + 1 device online). |
| T4 | Pass | 422 config topics. Device availability `online`. 713.SoC config: name "State of Charge", `%`, `battery`, `measurement`, enabled. Offline points: 703.ESDlyRemTms and 703.ESRndTms only. 4 live state changes in 8 s (713.WHAvail, 714.DCWhInj). 93 entities enabled by default, 329 disabled. 502.Stat state `UNKNOWN (0)`. |
| T5 | Pass | After the API stopped: `Event stream lost: peer closed connection …`, `Device marked offline`. Retained device availability: `offline`. |
| T6 | Pass | Ports 18830, 8120 and 5120 free. No traceback in the publisher log. |

Device in the discovery payload: name `FranklinWH aGate X <last 8 of serial>`, manufacturer `FranklinWH`, model `aGate X`, sw_version `V12R02B60D00`.
