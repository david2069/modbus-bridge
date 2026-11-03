# CLAUDE.md — modbus-bridge

## Project

A bridge for Modbus TCP devices (batteries, solar and hybrid inverters). It reads SunSpec models and raw register maps through `modbus-connection`. Quirks for each maker, model and firmware are applied as data. Results are published for Home Assistant and other consumers.

Design: `docs/design.md` (agreed decisions D1–D5, phases P0–P5). Background: `HANDOVER.md`.

## Rules

1. **One thing at a time.** Give a one-line plan and get the owner's yes before building. Do only what was asked; no unasked extras.
2. **Short, numbered, plain-English reports.** Number every list item so the owner can answer by number.
3. **Written test plan before any test.** It covers setup, steps, pass/fail and what it does not cover. Results go back into the plan.
4. **This repo is public.** No real IPs, serials, names or email addresses. Use 192.0.2.x and placeholders.
5. **Nothing from unpublished vendor material:** no registers, ranges, names, values, presets, examples or hints. Use public documents and our own measurements only.
6. **Test against an emulator instance only** (franklinwh-gateway-emulator, own port, stopped afterwards). Never a real device unless the owner arranges it.
7. **One Modbus client per server.** Never run two clients against one device.
8. **No silent fallbacks.** A missing or failed value is shown as missing, never as 0 or a guess.
9. **Every quirk is data,** visible, logged with its source, and can be switched off.
10. **Credit imported work** (repo, path, commit, MIT lines) and list it in THIRD_PARTY_NOTICES.md.
11. **Git:** never `git add -A`; no force-push; commit and push only when asked; use `Refs #N`.

## Conventions

- Python ≥ 3.12, async throughout, type hints on public functions.
- pytest for tests; ruff for lint.
