# Test plan: P1 step 9, a second SunSpec device (P1 "done when")

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

P1 is done when "an emulated aGate and one other SunSpec device publish correctly". The other device is a made-up three-phase solar inverter with two MPPT inputs, served by our own test simulator, `scripts/sunspec_sim.py`:

1. Its registers are built from the official SunSpec model files already in the repo: models 1, 103, 120 and 160 (with 2 modules), then the end marker.
2. Its identity is a placeholder: Mn `ExampleSolar`, Md `SimInverter 5000`, Vr `1.0.0`, SN `SIM-0000-0001`, Opt empty. It is not any real maker's device.
3. Points with no value set give SunSpec's "not implemented" value for their type. Power and energy change every second, so polling sees changes.
4. It answers function 3 (read holding registers) only; anything else gets a Modbus exception. A read outside the map gets "illegal data address".

This checks that nothing in modbus-bridge is tied to the aGate: different models, no PICS, a repeating group (MPPT modules), and a different maker.

## 2. Setup

1. The project `.venv`.
2. The simulator on 127.0.0.1:5121: `.venv/bin/python scripts/sunspec_sim.py --port 5121`
3. The API on 127.0.0.1:8121 and the test broker (amqtt, scratch) on 127.0.0.1:18830, as in step 8, with no PICS.
4. One Modbus client at a time (rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: (a) the register builder encodes each SunSpec type and its "not implemented" value; (b) end to end over real TCP on a free port: discover, Model 1, chain `[1, 103, 120, 160]`, 2 MPPT modules, only set points implemented; (c) a read outside the map gives "illegal data address". | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the simulator; run `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5121 --unit 1 --points` | Identity as in 1.2, Opt `(not set)`; chain 1, 103, 120, 160; 160 shows `module[1]` and `module[2]` points; source "discovered over 3 reads"; 103.W in W | Error or any difference |
| T4 | Start the broker, the API (`--device-port 5121 --listen-port 8121`, no `--pics`) and the publisher; dump MQTT for 8 s | Device `ExampleSolar SimInverter 5000 …-0001` online; one config per implemented point; 103.W has `power`; 103.WH has `energy` and `total_increasing`; 160 module power has `power`; live changes seen | Any of these not met |
| T5 | Stop publisher, API, broker and simulator; check ports 5121, 8121 and 18830 are free | All free | Any still in use |

## 4. Not covered

1. A real inverter. The simulator follows the SunSpec model files, not any maker's behaviour or quirks.
2. Base addresses 0 and 50000 over TCP (covered by unit tests against the mock in step 2).
3. Home Assistant itself (as in step 8).

## 5. Results

Run on 2026-11-03 with the same versions as step 8 (Python 3.12.15, modbus-connection 4.12.7, aiomqtt 2.5.1, broker amqtt 0.12.1 in scratch).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `182 passed` (18 new). First run failed: the 160 module group has count 0 in the model file ("repeat to fill the model"), which the builder did not handle; fixed. The one warning is from starlette's test client, not this step. |
| T2 | Pass | `All checks passed!`, 42 files already formatted |
| T3 | Pass | Start 40000; Mn `ExampleSolar`, Md `SimInverter 5000`, Opt `(not set)`, Vr `1.0.0`, SN `SIM-0000-0001`, DA 1. Chain 1 @40002 (66), 103 @40070 (50), 120 @40122 (26), 160 @40150 (48). `50 implemented, 26 not implemented (discovered over 3 reads)`. `160.module[1]` and `module[2]` points shown; 103.W `3252 W`; 103.St `4 (MPPT)`. One fix after this run: the simulator's power factor gave `1.0 Pct`; changed to `100 Pct` (SunSpec 103 gives PF in percent). |
| T4 | Pass | Publisher: `Snapshot: 50 points, 151 messages`. 50 config topics; device `ExampleSolar SimInverter 5000 000-0001` `online`; 103.W `power`; 103.WH `energy` + `total_increasing`; 160 module[1].DCW `power`, named `DC Power (module[1].DCW)`; 103.PF `%`; 0 points offline; 105 live state changes in 8 s. |
| T5 | Pass | Ports 5121, 8121 and 18830 free. No traceback in the simulator, API or publisher logs. |

Note: the HA device name uses the last 8 characters of the serial (`000-0001`), as designed in step 8.
