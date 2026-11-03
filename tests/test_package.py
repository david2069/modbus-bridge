import modbus_bridge


def test_package_imports_and_has_version() -> None:
    assert modbus_bridge.__version__ == "0.0.1"
