"""Diagnostics: pure logic and mocked hid (no USB device)."""

from __future__ import annotations

import json
from typing import Any

import pytest

import wraith_core.connection_manager as cm
from wraith_core.connection_manager import ordered_hid_candidates
from wraith_core.diagnostics import (
    ProbeResult,
    classify_candidate_role,
    enumerate_wraith_interfaces,
    probe_wraith_hid,
)


def _dev(
    path: str,
    *,
    usage_page: int,
    usage: int = 0,
    interface_number: int = 1,
) -> dict[str, Any]:
    return {
        "vendor_id": 0x0416,
        "product_id": 0x7372,
        "path": path,
        "interface_number": interface_number,
        "usage_page": usage_page,
        "usage": usage,
        "manufacturer_string": "M",
        "product_string": "P",
        "serial_number": "S",
        "release_number": 1,
    }


class _FakeDevice:
    def __init__(self, path: Any, fail_paths: set[str]) -> None:
        key = path.decode("utf-8") if isinstance(path, bytes) else str(path)
        if key in fail_paths:
            raise OSError("mock open failed")

    def close(self) -> None:
        pass


class _FakeHid:
    def __init__(self, devices: list[dict[str, Any]], fail_paths: set[str]) -> None:
        self._devices = devices
        self._fail_paths = fail_paths

    def enumerate(self, vendor_id: int, product_id: int) -> list[dict[str, Any]]:
        return [d for d in self._devices if d.get("vendor_id") == vendor_id and d.get("product_id") == product_id]

    def Device(self, path: Any = None, **kwargs: Any) -> _FakeDevice:
        p = path if path is not None else kwargs.get("path")
        return _FakeDevice(p, self._fail_paths)


@pytest.fixture
def fake_hid(monkeypatch: pytest.MonkeyPatch) -> _FakeHid:
    fake = _FakeHid([], set())
    monkeypatch.setattr(cm, "_hid", lambda: fake)
    return fake


def test_classify_vendor_control() -> None:
    assert classify_candidate_role(_dev("/v", usage_page=0xFF1B)) == "vendor_control_candidate"


def test_classify_keyboard() -> None:
    assert classify_candidate_role(_dev("/k", usage_page=0x0001, usage=0x0006)) == "keyboard_candidate"


def test_classify_other() -> None:
    assert classify_candidate_role(_dev("/o", usage_page=0x0001, usage=0x0007)) == "other_candidate"


def test_ordered_prefers_ff1b_over_keyboard() -> None:
    kb = _dev("/kb", usage_page=0x0001, usage=0x0006, interface_number=2)
    vendor = _dev("/v", usage_page=0xFF1B, interface_number=2)
    ordered = ordered_hid_candidates([kb, vendor])
    assert ordered[0]["path"] == "/v"
    assert ordered[1]["path"] == "/kb"


def test_keyboard_not_before_vendor_when_vendor_listed_second() -> None:
    kb = _dev("/kb", usage_page=0x0001, usage=0x0006, interface_number=1)
    vendor = _dev("/v", usage_page=0xFF1B, interface_number=2)
    ordered = ordered_hid_candidates([kb, vendor])
    assert [d["path"] for d in ordered] == ["/v", "/kb"]


def test_probe_json_serializable_no_devices(fake_hid: _FakeHid) -> None:
    fake_hid._devices = []
    pr = probe_wraith_hid()
    raw = json.dumps(pr.to_json_dict())
    data = json.loads(raw)
    assert data["device_count"] == 0
    assert data["candidate_count"] == 0
    assert data["vendor_usage_page_found"] is False
    assert data["selected_candidate"] is None


def test_probe_vendor_candidate_openable(fake_hid: _FakeHid) -> None:
    fake_hid._devices = [
        _dev("/vendor", usage_page=0xFF1B, interface_number=2),
        _dev("/kbd", usage_page=0x0001, usage=0x0006, interface_number=0),
    ]
    fake_hid._fail_paths = set()
    pr = probe_wraith_hid()
    assert pr.device_count == 2
    assert pr.vendor_usage_page_found is True
    assert pr.candidate_count == 1
    assert pr.selected_candidate is not None
    assert pr.selected_candidate["path"] == "/vendor"
    assert pr.any_openable is True
    assert "compatible" in pr.recommendation.lower()


def test_enumerate_includes_roles_and_json_roundtrip(fake_hid: _FakeHid) -> None:
    fake_hid._devices = [_dev("/v", usage_page=0xFF1B)]
    rows = enumerate_wraith_interfaces()
    assert rows[0]["candidate_role"] == "vendor_control_candidate"
    assert rows[0]["openable"] is True
    blob = json.dumps({"interfaces": rows})
    assert "vendor_control_candidate" in blob


def test_probe_vendor_found_but_unopenable(fake_hid: _FakeHid) -> None:
    fake_hid._devices = [_dev("/v", usage_page=0xFF1B, interface_number=2)]
    fake_hid._fail_paths = {"/v"}
    pr = probe_wraith_hid()
    assert pr.vendor_usage_page_found is True
    assert pr.selected_candidate is None
    assert pr.any_openable is False
    assert "could not be opened" in pr.recommendation.lower() or "opened" in pr.recommendation.lower()


def test_probe_result_dataclass_to_dict() -> None:
    pr = ProbeResult(
        device_count=0,
        candidate_count=0,
        vendor_usage_page_found=False,
        any_openable=False,
        selected_candidate=None,
        selected_reason="x",
        recommendation="y",
        rgb_ordered_candidates=[],
    )
    assert pr.to_json_dict()["recommendation"] == "y"
