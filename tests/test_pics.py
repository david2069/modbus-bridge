"""Tests for PICS profiles (design D6.3). All data here is made up for the test."""

import importlib.util
import json
from pathlib import Path

import pytest
from openpyxl import Workbook

from modbus_bridge.implemented import ImplementedPoints
from modbus_bridge.pics import PicsProfile, apply_pics, pics_details, pics_path_to_key_path

ROOT = Path(__file__).resolve().parent.parent


def _load_converter():
    spec = importlib.util.spec_from_file_location("convert_pics", ROOT / "scripts/convert_pics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("pics", "ours"),
    [
        ("W", "W"),
        ("Crv.1.ReadOnly", "Crv[1].ReadOnly"),
        ("Crv.2.Pt.3.V", "Crv[2].Pt[3].V"),
        ("Crv.1.MustTrip.Pt.1.V", "Crv[1].MustTrip[1].Pt[1].V"),
        ("Crv.1.MustTrip.ActPt", "Crv[1].MustTrip[1].ActPt"),
    ],
)
def test_pics_names_convert_to_our_paths(pics: str, ours: str) -> None:
    assert pics_path_to_key_path(pics) == ours


def test_converter_keeps_only_allowed_fields(tmp_path: Path) -> None:
    book = Workbook()
    info = book.active
    info.title = "Certification Info"
    for row in [
        ("Certificate Number", "SM-TEST"),
        ("Manufacturer Name", "ExampleMaker"),
        ("Product Description", "secret description"),
        ("Certificate Signer Name", "A Person"),
    ]:
        info.append(row)
    testing = book.create_sheet("Testing Info")
    testing.append(("Email", "tester@example.invalid"))
    model = book.create_sheet("713")
    model.append(("Address", "Point", "Subvalue", "Value", "R/W", "Min", "Max", "Notes"))
    model.append((1033, "ID", None, 713, "R"))
    model.append((1034, "L", None, 7, "R"))
    model.append((1035, "WHRtg", None, "supported", "R", 0, 20000.0))
    model.append((1038, "SoH", None, "unimplemented", "R"))
    model.append((1039, "Sta", None, "supported", "R"))
    model.append((None, "OK", None, "supported", None))  # enum symbol row
    model.append((1040, "WH_SF", None, 0, "R"))
    model.append((1041, "Mn", None, " ExampleMaker ", "R", None, 1.5))
    path = tmp_path / "pics.xlsx"
    book.save(path)

    profile = _load_converter().convert(path, "https://example.invalid/pics.xlsx")
    text = json.dumps(profile)

    assert "@" not in text
    assert "secret" not in text and "A Person" not in text
    assert set(profile) == {
        "format",
        "version",
        "certificate",
        "manufacturer",
        "source_url",
        "source_sha256",
        "models",
    }
    assert profile["models"] == {
        "713": {
            "implemented": ["WHRtg", "Sta", "WH_SF", "Mn"],
            "not_implemented": ["SoH"],
            "details": {"WHRtg": {"min": 0, "max": 20000}, "WH_SF": {"value": 0},
                        "Mn": {"value": "ExampleMaker", "max": 1.5}},
        }
    }  # fmt: skip
    assert profile["version"] == 2


def _profile() -> PicsProfile:
    return PicsProfile(
        certificate="SM-TEST",
        info={},
        models={
            713: {
                "implemented": frozenset({"WHRtg", "SoC", "WH_SF"}),
                "not_implemented": frozenset({"SoH", "Sta"}),
            }
        },
        details={713: {"WHRtg": {"value": 13600, "min": 0, "max": 20000}}},
    )


def _write(tmp_path: Path, version: int, entry: dict) -> Path:
    path = tmp_path / "profile.json"
    path.write_text(json.dumps({"format": "modbus-bridge/pics-profile", "version": version,
                                "certificate": "SM-TEST", "models": {"713": entry}}))  # fmt: skip
    return path


def test_version_1_profile_loads_without_details(tmp_path: Path) -> None:
    profile = PicsProfile.load(_write(tmp_path, 1, {"implemented": ["SoC"], "not_implemented": []}))
    assert profile.models[713]["implemented"] == {"SoC"}
    assert pics_details(profile, "713.SoC") == {"certified": None, "min": None, "max": None}


def test_version_2_profile_loads_details(tmp_path: Path) -> None:
    entry = {"implemented": ["SoC"], "not_implemented": [], "details": {"SoC": {"min": 5}}}
    profile = PicsProfile.load(_write(tmp_path, 2, entry))
    assert pics_details(profile, "713#2.SoC") == {"certified": None, "min": 5, "max": None}


def test_unknown_profile_version_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a PICS profile"):
        PicsProfile.load(_write(tmp_path, 3, {"implemented": [], "not_implemented": []}))


def test_details_need_a_pics_and_a_sunspec_key() -> None:
    none = {"certified": None, "min": None, "max": None}
    assert pics_details(_profile(), "713.WHRtg") == {"certified": 13600, "min": 0, "max": 20000}
    assert pics_details(_profile(), "713.SoC") == none
    assert pics_details(_profile(), "701.W") == none
    assert pics_details(_profile(), "label.x") == none
    assert pics_details(None, "713.WHRtg") == none


def test_shipped_sm000028_keeps_certified_values_and_ranges() -> None:
    profile = PicsProfile.load(ROOT / "src/modbus_bridge/pics_profiles/SM-000028.json")
    assert pics_details(profile, "702.WMax") == {"certified": None, "min": 0, "max": 10000}
    assert pics_details(profile, "702.WChaRteMaxRtg")["certified"] == 0
    assert pics_details(profile, "702.WMaxRtg")["certified"] == 10000


def test_pics_decides_covered_models_and_discovery_the_rest() -> None:
    discovered = ImplementedPoints(
        source="discovered over 3 reads",
        implemented=frozenset({"713.WHRtg", "713.Sta", "502.W"}),
        not_implemented=frozenset({"713.SoC", "713.SoH", "502.Ctl"}),
        unreadable_models=(),
    )
    result, report = apply_pics(discovered, _profile())

    assert result.implemented == {"713.WHRtg", "713.SoC", "713.Sta", "502.W"}
    assert result.not_implemented == {"713.SoH", "502.Ctl"}
    assert report.certified_no_value == ["713.SoC"]  # stays implemented, unavailable
    assert report.value_not_certified == ["713.Sta"]  # device wins (D6.4)
    assert report.discovered_models == [502]
    assert report.pics_only == ["713.WH_SF"]
    assert result.source == "PICS SM-TEST; discovered for model 502 (discovered over 3 reads)"


def test_point_missing_from_pics_follows_discovery() -> None:
    discovered = ImplementedPoints(
        source="d",
        implemented=frozenset({"713.WHAvail"}),
        not_implemented=frozenset(),
        unreadable_models=(),
    )
    result, report = apply_pics(discovered, _profile())
    assert "713.WHAvail" in result.implemented
    assert report.not_in_pics == ["713.WHAvail"]


def test_repeated_model_uses_same_pics_entry() -> None:
    discovered = ImplementedPoints(
        source="d",
        implemented=frozenset({"713#2.WHRtg"}),
        not_implemented=frozenset({"713#2.SoH"}),
        unreadable_models=(),
    )
    result, _ = apply_pics(discovered, _profile())
    assert result.implemented == {"713#2.WHRtg"}
    assert result.not_implemented == {"713#2.SoH"}
