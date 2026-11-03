# Test plan: P1 step 2, find SunSpec, read Model 1, list the model chain

Status: run on 2026-11-03, all passed. Results are in section 5.

## 1. Purpose

Check that modbus-bridge can:

1. connect to a Modbus TCP server through `modbus-connection`,
2. find the SunSpec start at 40000, 0 or 50000,
3. read Model 1 (Mn, Md, Opt, Vr, SN, DA),
4. list every model in the chain with its address and length,
5. show a value the device leaves empty as missing, not as an empty string or 0 (CLAUDE.md rule 8).

## 2. Setup

1. The project `.venv` from step 1, with `modbus-connection[tmodbus]>=4.12.7,<5` installed.
2. The emulator, [david2069/franklinwh-gateway-emulator](https://github.com/david2069/franklinwh-gateway-emulator), tag v0.2.3. It is installed in its own virtual environment in a scratch folder, outside this repo.
3. One emulator instance, on 127.0.0.1 only:
   `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate --seed 1 --no-control`
4. Only one Modbus client (the probe in T4) talks to the emulator at a time (CLAUDE.md rule 7).

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest` (unit tests against `modbus-connection`'s in-memory mock, no network) | All tests pass | Any test fails |
| T2 | `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` | No problems | Any problem |
| T3 | Start the emulator (setup item 3) and check it listens on 127.0.0.1:5120 | It listens | It does not start |
| T4 | `.venv/bin/python -m modbus_bridge.probe --host 127.0.0.1 --port 5120 --unit 1` | Prints the SunSpec start address, Mn, Md, Opt, Vr, SN and DA, and the model list ending normally. Model 1 is first. Empty values print as `(missing)`. | Error, no output, or a model list that does not start with Model 1 |
| T5 | Compare T4 with the emulator's own model list for this profile (from its source at v0.2.3) | Same model ids, in the same order | Any difference |
| T6 | Probe a port with nothing listening: `--port 5121` | A clear connection error and exit code 1, with no traceback | Hangs, traceback or exit code 0 |
| T7 | Stop the emulator and check port 5120 is free | Nothing listens on 5120 | It is still running |

## 4. Not covered

1. Reading the models after Model 1 (their points). That comes later in P1.
2. A second SunSpec device (the P1 done-when needs one, later in P1).
3. Unit ids other than 1, serial (RTU) links, TLS or UDP.
4. A real device. Only the emulator is used (CLAUDE.md rule 6).
5. Recovery after a dropped connection.

## 5. Results

Run on 2026-11-03 with Python 3.12.15, modbus-connection 4.12.7, tmodbus 1.1.0, pytest 9.2.0 and ruff 0.17.3. Emulator tag v0.2.3 (checked out at commit af7bc62).

| # | Result | Output |
|---|---|---|
| T1 | Pass | `6 passed` |
| T2 | Pass | `All checks passed!`, `11 files already formatted` |
| T3 | Pass | Emulator listening on 127.0.0.1:5120, `modbus_max_connections=1` |
| T4 | Pass | See below. Model 1 is first and the chain ends normally. |
| T5 | Pass | The same 17 models, in the same order and with the same lengths as the emulator's baseline `agate_v10r01b04d00.json`. The v12 profile uses that baseline. |
| T6 | Pass | `Error: could not connect to 127.0.0.1:5121`, exit code 1, no traceback |
| T7 | Pass | Nothing listens on 5120 after the stop |

T4 output. The serial is the emulator's generated one, shown here as a placeholder.

```
SunSpec start: 40000
Model 1:
  Mn  FranklinWH
  Md  aGate X
  Opt Emulator 0.2.3
  Vr  V12R02B60D00
  SN  <emulator serial>
  DA  1
Model chain (17 models):
      1  at 40002  length 66
    701  at 40070  length 153
    702  at 40225  length 50
    703  at 40277  length 17
    704  at 40296  length 65
    705  at 40363  length 67
    706  at 40432  length 31
    707  at 40465  length 105
    708  at 40572  length 105
    709  at 40679  length 135
    710  at 40816  length 135
    711  at 40953  length 32
    712  at 40987  length 44
    713  at 41033  length 7
    714  at 41042  length 43
    715  at 41087  length 7
    502  at 41096  length 28
```

Notes:

1. The emulator's Opt was not empty, so the "(missing)" display was checked only by the unit test (T1), not against the emulator.
2. The library's string decoder drops bytes that are not ASCII without saying so. This step does not change that. It is listed for a later decision.
