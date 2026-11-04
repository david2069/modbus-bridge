# Test plan: P2 step 2, raw register readings in quirk sets

Status: run on 2026-11-04, all passed. Results are in section 5.

## 1. Purpose

Check that a quirk set can add readings from registers outside SunSpec (design 1.2 and 1.4: "add a reading"), defined as data:

1. A quirk set gets an optional `readings` list. Each reading has:
   - `id` (unique across all files, like quirk ids), `name` and `reason`, and optionally `source` (the set's source by default);
   - `address`, and `table`: `holding` (default) or `input`;
   - `type`: `uint16`, `int16`, `uint32`, `int32`, `uint64`, `int64` or `float32`;
   - `word_order`: `big` (default, high word first) or `little`, for types longer than one register;
   - `scale` (a non-zero multiplier, default 1) and `invert` (default false);
   - `units` and `label` (optional);
   - `unavailable` (optional): a list of raw values that mean "no value", e.g. 65535.
2. The reading is published as point `raw.<name>`, with its type, units and label, and `quirks` lists the reading's id.
3. A raw value in `unavailable`, a failed read or a value that is not a number (NaN) gives no value, never 0 or a guess (rule 8).
4. Readings are always published, even while unavailable. There is no discovery for them: the quirk set says they exist.
5. A higher layer's reading with the same name replaces the lower one; `--quirk-off ID` switches a reading off and the lower layer's reading (if any) applies. Two readings with the same name in the same layer clash: both are marked failing and the point has no value.
6. Point quirks (step 1) can be applied to `raw.<name>` keys too.
7. Reads: registers next to each other in the same table are read together, up to 125 registers. If a block read fails with a Modbus exception, each reading in it is read alone, so one bad address does not take its neighbours with it. A connection error makes every point unavailable, as now.
8. The quirks endpoint lists readings with their address, table, type and state (`active`, `overridden`, `off` or `failing`, with the last error).

The simulator gets made-up extra registers for this test (option `--extra`): 1000 a mode (uint16, value 2), 1001–1002 a power (int32, little word order, negative and changing), 1003 a value that is always 65535, 1004–1005 an energy counter (uint32). 1010 is not served.

## 2. Setup

1. The project `.venv`.
2. The simulator on 127.0.0.1:5121 with `--extra`.
3. A made-up quirk file in the scratchpad, `raw.json` (vendor, Mn `ExampleSolar`) with readings named `mode` (1000), `batt_w` (1001, int32, little, units W, invert), `spare` (1003, `unavailable: [65535]`), `energy` (1004, uint32, scale 0.001, units kWh), and `missing` (1010).
4. The API on 127.0.0.1:8121 with the scratch token file.

## 3. Steps and pass/fail

| # | Step | Pass | Fail |
|---|---|---|---|
| T1 | `.venv/bin/pytest`. New tests: loading and refusing bad readings; decoding each type in both word orders; scale, invert and `unavailable`; NaN; block grouping and the split after a failed block; input table; layer override and switching off; point quirks on `raw.` keys; quirks endpoint. | All pass | Any fails |
| T2 | `ruff check .` and `ruff format --check .` | No problems | Any problem |
| T3 | Start the simulator with `--extra` and the API with `--quirks raw.json`; `GET …/points` and `GET …/quirks` | `raw.mode` 2; `raw.batt_w` positive (inverted from the simulator's negative value), in W; `raw.spare` unavailable; `raw.energy` in kWh; `raw.missing` unavailable and `failing` with the Modbus error; the other readings `active`; SunSpec points as in P1 step 9 | Any of these not met |
| T4 | Watch `raw.batt_w` for 5 s through `GET …/points` | It changes | It does not change |
| T5 | Stop the API and simulator; check ports 5121 and 8121 are free | Both free | Either in use |

## 4. Not covered

1. Strings, bitfields and enums with names in raw readings (later, with the neutral labels).
2. Neutral labels, constants and derived rules (the evaluator).
3. Any real maker's registers. The FranklinWH extensions come in a later step, from public sources only.
4. Writes (P2W).
5. A device that needs a different unit id for its raw registers.

## 5. Results

Run on 2026-11-04 against the simulator with `--extra`, same versions as P1 step 9.

| # | Result | Output |
|---|---|---|
| T1 | Pass | `261 passed` (36 new in `tests/test_raw.py`). The mock answers 0 for registers it does not hold, so the tests make it refuse reads with `fail_read`. |
| T2 | Pass | `All checks passed!`, 48 files already formatted |
| T3 | Pass | Log names each reading with table, type, address, reason and source. Points: 55 (50 SunSpec + 5 raw). `raw.mode` 2; `raw.batt_w` 1474 W, label `Battery power` (the simulator's value is negative; `invert` makes it positive); `raw.spare` unavailable; `raw.energy` 500.006 kWh; `raw.missing` unavailable. Quirks endpoint: four readings `active`, `r-missing` `failing` with `Modbus Exception 0x02`. 103.W 3309 W as before. Registers 1000–1005 were read as one block; 1010 alone. |
| T4 | Pass | `raw.batt_w` 1474, 1498, 1443 W over 4 s |
| T5 | Pass | Ports 5121 and 8121 free; no traceback in the logs. |
