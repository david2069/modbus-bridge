"""Tests for the read-only page at /ui (design P2U). Values are made up."""

import re

from fastapi.testclient import TestClient
from test_api import AUTH, client, service  # noqa: F401 (fixtures)

from modbus_bridge.api import model_name


def test_page_is_served_without_a_token(client: TestClient) -> None:  # noqa: F811
    res = client.get("/ui")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")
    assert "<title>modbus-bridge</title>" in res.text


def test_page_holds_no_device_data(client: TestClient) -> None:  # noqa: F811
    page = client.get("/ui").text
    for data in ("SN-PLACEHOLDER", "ExampleMaker", "ExampleModel", "87.5", "test-token-not-secret"):
        assert data not in page


def test_page_loads_nothing_from_outside(client: TestClient) -> None:  # noqa: F811
    page = client.get("/ui").text
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", page)
    assert not re.search(r"""(fetch|import)\s*\(\s*["'`](https?:)?//""", page)
    assert "@import" not in page


def test_device_answer_has_interval(client: TestClient) -> None:  # noqa: F811
    assert client.get("/api/v1/devices/unit1", headers=AUTH).json()["interval"] == 60
    assert client.get("/api/v1/devices", headers=AUTH).json()[0]["interval"] == 60


def test_data_still_needs_a_token(client: TestClient) -> None:  # noqa: F811
    for path in ("/devices", "/devices/unit1", "/devices/unit1/points", "/devices/unit1/quirks"):
        assert client.get("/api/v1" + path).status_code == 401


def test_chain_has_model_names(client: TestClient) -> None:  # noqa: F811
    chain = client.get("/api/v1/devices/unit1", headers=AUTH).json()["chain"]
    assert [(m["model_id"], m["name"]) for m in chain] == [
        (1, "Common"),
        (713, "DER Storage Capacity"),
    ]


def test_model_with_no_definition_has_no_name() -> None:
    assert model_name(1) == "Common"
    assert model_name(64999) is None
