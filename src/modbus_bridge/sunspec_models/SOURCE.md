# SunSpec model definitions

- Source: <https://github.com/sunspec/models>, commit `90b4a331dcca1d6eac69c1bead952fddcc5852e0`, folder `json/`.
- Licence: Apache License 2.0, copied in `LICENSE` here.
- `json/` holds the unmodified model files.
- `generated/` is produced from them by `scripts/generate_sunspec_models.py`,
  using modbus-connection's generator. Do not edit it by hand.

Generated: 111 models.

Left out, because the generator cannot express them:

- Model 63001: model 63001: group repeating mixes in-block and fixed-block scale factors, which one class cannot express
