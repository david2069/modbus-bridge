# modbus-bridge

A bridge for Modbus TCP energy devices: batteries, and solar and hybrid inverters.

- It reads **SunSpec** models and **raw register maps** through [modbus-connection](https://pypi.org/project/modbus-connection/).
- It applies each maker's, model's and firmware's **quirks as data**.
- It publishes the results for Home Assistant and other consumers.

**Status:** design agreed, no code yet. See [docs/design.md](docs/design.md).

**Scope:** the simple, common site. That means one battery system, perhaps with AC or DC solar.

## Credits

- FranklinWH register knowledge: [david2069/franklinwh-modbus](https://github.com/david2069/franklinwh-modbus) (MIT).
- Vendor quirks will be imported from [hilman2/ha-sunspec2](https://github.com/hilman2/ha-sunspec2) (MIT), credited per file.

## Licence

MIT. See [LICENSE](LICENSE).
