"""Provide generated SunSpec components."""
# Source: https://github.com/sunspec/models (json/model_15.json)

from __future__ import annotations

from modbus_connection.model.sunspec import (
    SunSpecComponent,
    acc32,
    uint16,
)


class Model15(SunSpecComponent):
    """SunSpec model 15: Interface Counters Model."""

    clr = uint16(2, writable=True)
    """Clear. Write a "1" to clear all counters."""

    in_cnt = acc32(3)
    """Input Count. Number of bytes received."""

    in_uc_cnt = acc32(5)
    """Input Unicast Count. Number of Unicast packets received."""

    in_n_uc_cnt = acc32(7)
    """Input Non-Unicast Count. Number of non-Unicast packets received."""

    in_dsc_cnt = acc32(9)
    """Input Discarded Count. Number of inbound packets received on the interface but
    discarded."""

    in_err_cnt = acc32(11)
    """Input Error Count. Number of inbound packets that contain errors (excluding
    discards)."""

    in_unk_cnt = acc32(13)
    """Input Unknown Count. Number of inbound packets with unknown protocol."""

    out_cnt = acc32(15)
    """Output Count. Total number of bytes transmitted on this interface."""

    out_uc_cnt = acc32(17)
    """Output Unicast Count. Number of Unicast packets transmitted."""

    out_n_uc_cnt = acc32(19)
    """Output Non-Unicast Count. Number of Non-Unicast packets transmitted."""

    out_dsc_cnt = acc32(21)
    """Output Discarded Count. Number of Discarded output packets."""

    out_err_cnt = acc32(23)
    """Output Error Count. Number of outbound error packets."""
