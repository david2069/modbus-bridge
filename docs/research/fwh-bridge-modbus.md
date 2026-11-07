# Study: Modbus and register extensions in franklinwh-modbus-bridge

Status: read on 2026-11-07. Code read, not run.

Source: [franklinwh-modbus-bridge](https://github.com/david2069/franklinwh-modbus-bridge) at commit f560db9 (0.2.56), with its library franklinwh-modbus 0.10.1. Files read in full: `gateway/instance.py`, `modbus/poller.py`, `modbus/home_load.py`, `modbus/reserves.py`, `modbus/register_watch.py`, `modbus/sunspec_enums.py`, `docs/vendor-issues.md`, and the library's `connect`, `read_solar_status`, `_read_extension_solar` and `read_nameplate`. Read in part: `modbus/catalog.py` and the library's `discovery.py`.

Purpose: learn what that bridge found about the aGate's Modbus interface, and what modbus-bridge should take from it. Only public material is used (rule 5). Points that rest only on FranklinWH's conformance-review correspondence, as quoted in its `vendor-issues.md`, are left out.

## 1. How it works

1. **One session per aGate.** One TCP session is shared through a lock for each gateway, because the aGate serves one client at a time. Polls, commands, the catalogue capture and diagnostics all go through that lock. It patches the library to really close the socket on disconnect (#64, #288); before that fix, each reconnect left a session open on the aGate.
2. **SunSpec base address.** The scan is patched to try base 0 first, then 40000, then 50000 (#308). The reason it gives: firmware up to V10R01B04D00 refused 40000, and V12R02B60D00 mirrors the whole map at 40000. Binding to the mirror would move every model address by 40000.
3. **Device identity.** The device is identified by Model 1 (Mn, Md, Opt, Vr, SN). Each gateway is locked to the first serial it reports, and the serial is read again after every reconnect (#307). If a different serial answers, the gateway is refused and nothing more is read from or written to that device (#296).
4. **Reading.** The library reads models 1, 502, 701, 702, 704, 713, 714 and 715 through pysunspec2; 703 and the 702 ratings are read once at start. Raw SunSpec points are exposed as `<model>.<point>`. The extension registers are hard-coded in Python:
   - the library reads 15500–15513 and 16000 over a raw socket, without checking the reply's transaction id or function code;
   - the bridge reads 15000–15039, 15500–15513 and 16000–16002 again on the library's connection, as `vreg_<address>`.
5. **Vendor, model and firmware differences.** There are no tables for these. The only per-device settings are the user's `device_type` (aGate or MAC-1 meter collar) and `home_load_source`. Firmware is stored and a change is logged, but nothing changes with it.
6. **The library wrote to the device on connect.** Versions up to 0.9.5 wrote test values to 15507–15509 (operating mode and both reserves) on every connect, then wrote the old values back. The bridge disables this (#239).

## 2. What it found about the aGate (public evidence)

| # | Finding | Evidence in that repo | Already in our FranklinWH set? |
|---|---|---|---|
| F1 | Extension registers sometimes return 0xFFFF; three of them summed gave 196,605 W | `poller.py` comments, `MAX_SANE_POWER_W` | **No**: no reading has an `unavailable` value |
| F2 | 15502–15506 report a small negative power as uint16 (-5 W read as 65531) | #122 | Yes: 15502–15505 are read as int16; 15506 stays uint16 |
| F3 | 16000 is home load at about 1 W. One unverified community report says it stuck at 1000 while the load moved | `home_load.py`, franklinwh-modbus#18 | Partly: we trust 16000 for good once it shows a value that is not a multiple of 100 W; it cross-checks against 15506 on every poll |
| F4 | 16001 is the active mode's reserve, 100 in Emergency Backup (V12R02B60D00) | `reserves.py`, #311 | Yes (N8) |
| F5 | 15509 repeated 15508 on V10R01B04D00 | `vendor-issues.md` §7 | Yes (noted in the reading) |
| F6 | 15013 is signed and follows 714.DCW (negative = charging) | `SIGNED_VREGS`, from one site's readings | Yes: 15012–15013 read as int32 (N11) |
| F7 | 15016 has no confirmed meaning; values 2, 6 and others seen | `register_watch.py`, #36 | Yes (N10, values marked as seen at one site only) |
| F8 | 15020, 15025 and 15036 mirror 713.WHRtg, 701 line voltage and 713.SoH | `vendor-issues.md` §8 | Not needed: SunSpec gives these |
| F9 | 714.DCA always reads 0 on an aGate X (V10R01B04D00), although the PICS lists it as implemented | `vendor-issues.md` §3 | **No** |
| F10 | 701.DERMode is "unimplemented" in the PICS, yet the device returns values; "PV clipped" was seen at night 12 times out of 13 | `vendor-issues.md` §10, §12d | **No**: our PICS step keeps a point that gives a value, and only logs it |
| F11 | 713.Sta is a health enum (OK, WARNING, ERROR), not an activity state | `sunspec_enums.py`, #55 | Yes: we use the SunSpec model definitions |
| F12 | 701.Alrm and 714 alarm bits: the old names were wrong; the right ones are in the SunSpec model definitions, and the alarm type is in `Prt[n].DCAlrm`, not `PrtAlrms` | `vendor-issues.md` §12a–b | Yes for names: we use the SunSpec definitions |
| F13 | Model 502 is present and readable but is not in the PICS | `vendor-issues.md` §8 | Yes: a model missing from the PICS is kept from discovery |
| F14 | The aGate acknowledges a write to every address tried, including read-only mirrors, so an acknowledgement proves nothing | `docs/reference/register-writability-probe.md` | For P2W |
| F15 | Writes to 15507–15509 are acknowledged but not applied; WSetRvrtTms counts down but never reverts; WSet above the rating is accepted; ControllerHb, WMaxLimPct and VarSetEna writes have no effect | `vendor-issues.md` §1, 2, 5, 11 | For P2W |
| F16 | A second session while one is open is a known corruption trigger | `poller.py`, `vendor-issues.md` | Yes: rule 7 |

## 3. Gaps in modbus-bridge

**Wrong data in HA today:**

1. **G1: 0xFFFF from an extension register is published as a value (F1, rule 8).**
   - On the uint16 readings it shows as 65535 W of home load (15506, 16000) or a 65535 % reserve (15508, 15509, 16001).
   - Fix: list 0xFFFF as `unavailable` on the uint16 readings in the FranklinWH set; the reading format already supports this.
   - Not a gap on the int16 PV readings (15502–15505): there 0xFFFF reads as -1 W, and a small negative PV power at night is normal for many inverters (F2). No evidence shows the aGate sends 0xFFFF there as "no value", so they are left as they are unless a measurement shows otherwise. (Corrected 2026-11-07: this was first listed as wrong data without evidence.)
2. **G2: 714.DCA shows 0 A as a real current (F9).**
   - Fix: a FranklinWH quirk that hides 714.DCA and `Prt[n].DCA`, with that bridge's measurement as the source.
   - It is measured on V10R01B04D00 only, so this should be a model or firmware quirk once V12 has been checked.
3. **G3: 701.DERMode is published if the device returns a value, although the PICS says unimplemented (F10).**
   - Fix: a FranklinWH quirk that hides it, with the PICS as the source.
4. **G4: Model 1 is read only at start, not after a reconnect.**
   - Design Q3 says it is read on every connect. If the firmware changes, or another device answers at the same address, we keep the old identity and quirks, and publish its data under the old serial.
   - That bridge re-reads Model 1 after each reconnect and refuses a changed serial (section 1.3).
   - Whether `modbus-connection` reconnects on its own after a drop has to be checked first.

**To improve (not wrong today):**

5. **G5: 16000 is trusted for good once trusted (F3).** If it later sticks, as reported once, we would show a frozen load. A per-poll check against 15506, as that bridge does, would catch it.
6. **G6: SunSpec base order.** We try 40000 first, so on V12R02B60D00 we bind the 40000 mirror. Reads have matched so far. It matters for writes (P2W) and for address-based quirks, so 0 first for FranklinWH belongs in the catalogue's connection defaults (C5).

## 4. Lessons for P2W (writes)

1. Never write on connect or on discovery (section 1.6).
2. A Modbus acknowledgement is not proof: read back, and where possible check the effect (F14, F15).
3. The device's own revert timer cannot be relied on; the bridge needs its own watchdog (F15).
4. Clamp setpoints to the rating; the device does not (F15).

## 5. To measure ourselves (emulator first, the real aGate only when the owner arranges it)

1. How often 0xFFFF appears on 15506 and 16000–16001; and whether 15502–15505 ever read -1 W in a way that is not real standby draw (G1).
2. 714.DCA on V12R02B60D00 (G2).
3. What 701.DERMode returns on V12R02B60D00 (G3).
4. Whether reads at base 40000 and base 0 always agree on V12R02B60D00 (G6).
