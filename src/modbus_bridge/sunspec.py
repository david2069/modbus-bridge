"""Find SunSpec on a Modbus unit, read Model 1 and list the model chain."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

from modbus_connection import ModbusExceptionError, ModbusUnit
from modbus_connection.model.sunspec import (
    SunSpecComponent,
    SunSpecError,
    SunSpecModel,
    SunSpecModels,
    scan,
    string,
    uint16,
)

_LOGGER = logging.getLogger(__name__)

#: Where SunSpec devices put the "SunS" marker, tried in this order.
BASE_ADDRESSES: Final = (40000, 0, 50000)

#: The SunSpec Common model.
COMMON_MODEL_ID: Final = 1


class CommonModel(SunSpecComponent):
    """SunSpec Model 1 (Common), from the public SunSpec model definition.

    Addresses are offsets from the model header, which takes offsets 0 and 1.
    """

    mn = string(2, 16)
    md = string(18, 16)
    opt = string(34, 8)
    vr = string(42, 8)
    sn = string(50, 16)
    da = uint16(66)


@dataclass(frozen=True)
class DeviceIdentity:
    """What Model 1 says about a device. ``None`` means the device left it empty."""

    manufacturer: str | None
    model: str | None
    options: str | None
    version: str | None
    serial: str | None
    device_address: int | None


@dataclass(frozen=True)
class SunSpecDevice:
    """A SunSpec device found on one unit."""

    base_address: int
    identity: DeviceIdentity
    chain: list[SunSpecModel]


async def find_sunspec(unit: ModbusUnit) -> tuple[int, SunSpecModels]:
    """Return the SunSpec base address and the models found there.

    Tries each address in ``BASE_ADDRESSES``. Raises ``SunSpecError`` if none
    holds a valid SunSpec chain. Connection errors are not caught.
    """
    for base in BASE_ADDRESSES:
        try:
            models = await scan(unit, base)
        except (SunSpecError, ModbusExceptionError) as err:
            _LOGGER.debug("No SunSpec at %d: %s", base, err)
            continue
        _LOGGER.debug("SunSpec found at %d with %d models", base, len(models.chain))
        return base, models
    raise SunSpecError(f"No SunSpec chain found at {', '.join(map(str, BASE_ADDRESSES))}")


def _text(value: str | None) -> str | None:
    """An empty SunSpec string is missing, not an empty value."""
    if value is None:
        return None
    value = value.strip()
    return value or None


async def read_identity(unit: ModbusUnit, models: SunSpecModels) -> DeviceIdentity:
    """Read the first Model 1 in the chain.

    Raises ``SunSpecError`` if the chain has no Model 1.
    """
    found = models.first(COMMON_MODEL_ID)
    if found is None:
        raise SunSpecError("The SunSpec chain has no Model 1")
    common = CommonModel(unit, found)
    await common.async_update()
    da = common.da
    return DeviceIdentity(
        manufacturer=_text(common.mn),
        model=_text(common.md),
        options=_text(common.opt),
        version=_text(common.vr),
        serial=_text(common.sn),
        device_address=None if da is None else int(da),
    )


async def discover(unit: ModbusUnit) -> SunSpecDevice:
    """Find SunSpec, read Model 1 and return the model chain."""
    base, models = await find_sunspec(unit)
    identity = await read_identity(unit, models)
    return SunSpecDevice(base_address=base, identity=identity, chain=models.chain)
