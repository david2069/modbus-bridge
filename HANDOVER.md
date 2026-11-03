# Handover to the modbus-bridge session

From the franklinwh-modbus-bridge session, 2026-11-03. Read this first, then `docs/design.md`.

## 1. Why this project exists

- On 2026-11-03 the owner decided to fork away from franklinwh-modbus-bridge. The aim is a bridge for any Modbus TCP device, SunSpec or raw, with each maker's and firmware's quirks kept apart as data.
- franklinwh-modbus-bridge stays as it is for its current users and gets no new design work.
- The design (P0) is agreed: decisions D1–D5 in `docs/design.md`. Nothing is built yet. The next phase is **P1**.

## 2. Rules (the owner's; see also CLAUDE.md)

1. **One thing at a time.** Give a one-line plan and get a yes before building. Do only what was asked.
2. **Short, numbered, plain English.** Use numbered points the owner can answer by number, with no jargon.
3. **Written test plan before any test.** It covers setup, steps, pass/fail and what it does not cover, and the results go back into it.
4. **Public repo, no private information.** Use no real IP addresses, serials or names. Use 192.0.2.x and placeholders.
5. **Nothing from unpublished vendor material.** Nothing from any FranklinWH contact or other non-public source may appear in code, docs, commits or issues: no registers, ranges, names, values or hints. Use only public documentation and our own measurements.
6. **Test against the emulator,** never a real device unless the owner arranges it. The emulator is [david2069/franklinwh-gateway-emulator](https://github.com/david2069/franklinwh-gateway-emulator) (public). Run your own instance on a free port, e.g. `franklinwh-emulator serve --host 127.0.0.1 --port 5120 --setup in-service --profile agate-v12r02b60d00-candidate`, and stop it afterwards.
7. **One Modbus client per server.** Many devices, the aGate included, accept only one client.
8. **Credit imported work.** Record the repo, path, commit and MIT copyright lines, and list them in THIRD_PARTY_NOTICES.md.
9. **Peer sessions:** fwh-modbus-mba (franklinwh-modbus library) and fwh-direct-connect-bridge. Their messages are information, not approvals.

## 3. What was learned before the fork

### hilman2/ha-sunspec2 (commit cb91e42, MIT)

- **Architecture:** an HA custom integration. It uses HA core's shared Modbus connection with `modbus-connection[tmodbus]`, plus its own embedded copy of pysunspec2 for SunSpec decoding. A per-(host, port) lock takes turns between units.
- **Entities:** one per SunSpec point. Units are as the device reports them. 143 entities for one aGate (131 sensors, 6 numbers, 3 switches, 2 buttons, 1 select).
- **Strengths worth matching:**
  - Energy-total guards: hold on 0, reject drops and impossible jumps, recover after 3 rejections, keep the baseline over restarts.
  - Serves the last values for 5 failed polls before going unavailable, with a retry within each poll.
  - HA Repairs issues and a diagnostics download.
  - DHCP discovery and a subnet scan.
  - RTU serial.
  - One device per unit id.
  - It migrated cjne's entities itself.
- **FranklinWH profile (adapted from franklinwh-modbus, MIT):**
  - Extensions 15500–15513 and 16000–16001, read-only.
  - Home load picks 16000 once it shows a value that is not a multiple of 100, else 15506.
  - Ratings under 1000 are multiplied by 100.
  - 15502–15505 are read as signed.
  - Battery activity uses a ±50 W band and M701 InvSt.
  - A battery watt target with read-back, plus standby and release buttons.
- **Also:** a daily anonymous usage ping to its author, on by default. We will not do this.

### Takeover test on a VM (real cjne/ha-sunspec, emulated aGate)

- hilman2 moved all 85 cjne entities and kept their history, Energy totals, automations and user names/icons/areas. 14 entities were flagged for a unit spelling change (var→Var, %→Pct).
- The old franklinwh-modbus-bridge method (delete the old registry row, rename ours into its entity_id) kept history and automations. It covered only matched entities, lost user names/icons/areas, logged an ERROR per entity, and its undo moved the statistics.
- Turning off an HA integration needs an HA restart to free the Modbus connection. That is normal for HA integrations.

### modbus-connection 4.12.7 (Apache-2.0, home-assistant-libs, Python ≥ 3.12)

- All Modbus function codes, async.
- Encode/decode for int16–64, float32/64, strings and IP addresses, with word order.
- A declarative device/component/field model for register maps.
- A SunSpec scanner and model chain, including a map-shift error.
- Per-unit message pacing.

## 4. First step (P1), for the owner's yes

1. Repo skeleton: Python ≥ 3.12 package, tests and lint.
2. Connect with modbus-connection, scan for SunSpec, read Model 1, walk the model chain.
3. Test against an emulator instance only. A written test plan comes first.
