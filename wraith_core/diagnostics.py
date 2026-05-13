"""Safe HID enumeration and compatibility probes (no firmware, no fuzzing, no analog)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import wraith_core.connection_manager as cm
from wraith_core.connection_manager import ConnectionManager, ordered_hid_candidates

DEFAULT_VENDOR_ID = 0x0416
DEFAULT_PRODUCT_ID = 0x7372

CandidateRole = Literal["vendor_control_candidate", "keyboard_candidate", "other_candidate"]


def classify_candidate_role(dev: dict[str, Any]) -> CandidateRole:
    """Classify an HID interface for reporting (does not imply RGB support)."""
    usage_page = dev.get("usage_page")
    usage = dev.get("usage")
    if usage_page == 0xFF1B:
        return "vendor_control_candidate"
    if usage_page == 0x0001 and usage == 0x0006:
        return "keyboard_candidate"
    return "other_candidate"


def _path_for_display(path: Any) -> str:
    if isinstance(path, bytes):
        return path.decode("utf-8", errors="replace")
    return str(path)


def try_open_hid(hm: Any, path: Any) -> tuple[bool, str | None]:
    """Try to open an HID path; return (openable, error_message)."""
    open_errors: tuple[type[BaseException], ...] = (OSError, ValueError)
    hid_exc = getattr(hm, "HIDException", None)
    if hid_exc is not None:
        open_errors = (hid_exc, OSError, ValueError)
    try:
        handle = hm.Device(path=path)
    except open_errors as exc:
        return False, str(exc)
    try:
        handle.close()
    except OSError:
        pass
    return True, None


def enumerate_wraith_interfaces(
    vendor_id: int = DEFAULT_VENDOR_ID,
    product_id: int = DEFAULT_PRODUCT_ID,
) -> list[dict[str, Any]]:
    """Enumerate all HID entries for VID/PID and add role, openable, and open_error."""
    hm = cm._hid()
    raw = list(hm.enumerate(vendor_id, product_id))
    out: list[dict[str, Any]] = []
    for dev in raw:
        role = classify_candidate_role(dev)
        openable, open_err = try_open_hid(hm, dev["path"])
        row: dict[str, Any] = {
            "vendor_id": dev.get("vendor_id"),
            "product_id": dev.get("product_id"),
            "path": _path_for_display(dev["path"]),
            "interface_number": dev.get("interface_number"),
            "usage_page": dev.get("usage_page"),
            "usage": dev.get("usage"),
            "manufacturer_string": dev.get("manufacturer_string"),
            "product_string": dev.get("product_string"),
            "serial_number": dev.get("serial_number"),
            "release_number": dev.get("release_number"),
            "openable": openable,
            "open_error": open_err,
            "candidate_role": role,
        }
        out.append(row)
    return out


@dataclass
class ProbeResult:
    device_count: int
    candidate_count: int
    vendor_usage_page_found: bool
    any_openable: bool
    selected_candidate: dict[str, Any] | None
    selected_reason: str
    recommendation: str
    rgb_ordered_candidates: list[dict[str, Any]] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def probe_wraith_hid(
    vendor_id: int = DEFAULT_VENDOR_ID,
    product_id: int = DEFAULT_PRODUCT_ID,
) -> ProbeResult:
    """Compatibility probe: enumerate, openability, ConnectionManager-style selection. No HID writes."""
    hm = cm._hid()
    raw = list(hm.enumerate(vendor_id, product_id))
    device_count = len(raw)
    vendor_usage_page_found = any(d.get("usage_page") == 0xFF1B for d in raw)

    enriched_by_path: dict[str, dict[str, Any]] = {}
    for dev in raw:
        role = classify_candidate_role(dev)
        openable, open_err = try_open_hid(hm, dev["path"])
        path_key = _path_for_display(dev["path"])
        enriched_by_path[path_key] = {
            "vendor_id": dev.get("vendor_id"),
            "product_id": dev.get("product_id"),
            "path": path_key,
            "interface_number": dev.get("interface_number"),
            "usage_page": dev.get("usage_page"),
            "usage": dev.get("usage"),
            "manufacturer_string": dev.get("manufacturer_string"),
            "product_string": dev.get("product_string"),
            "serial_number": dev.get("serial_number"),
            "release_number": dev.get("release_number"),
            "openable": openable,
            "open_error": open_err,
            "candidate_role": role,
        }

    ordered = ordered_hid_candidates(raw)
    candidate_count = len(ordered)
    rgb_ordered: list[dict[str, Any]] = []
    for dev in ordered:
        path_key = _path_for_display(dev["path"])
        rgb_ordered.append(enriched_by_path[path_key])

    any_openable = any(e["openable"] for e in rgb_ordered) if rgb_ordered else False

    selected: dict[str, Any] | None = None
    selected_reason = ""
    for i, entry in enumerate(rgb_ordered):
        if entry["openable"]:
            selected = entry
            role = entry["candidate_role"]
            selected_reason = (
                f"First openable interface in ConnectionManager order (index {i}); "
                f"candidate_role={role}."
            )
            break

    if device_count == 0:
        recommendation = (
            f"No Wraith device found for VID/PID {vendor_id:04x}:{product_id:04x}. "
            "Connect the keyboard and check USB; then run this command again."
        )
        selected_reason = "No enumerated HID entries for this VID/PID."
    elif not vendor_usage_page_found:
        recommendation = (
            "Device (or matching VID/PID) was found, but known vendor usage page "
            "0xFF1B was not seen on any interface. Please open an issue with "
            "`wraith debug enumerate --json` output attached."
        )
        if not selected_reason:
            selected_reason = "No entry with usage_page 0xFF1B in enumeration."
    elif selected is not None:
        recommendation = (
            "Device looks compatible with the RGB path this project uses. "
            "You may run `wraith debug probe --test-rgb --confirm` to send one "
            "static lighting packet (same path as normal `set-color`)."
        )
        if not selected_reason:
            selected_reason = "Openable vendor-ordered path available."
    else:
        recommendation = (
            "Vendor usage page was found, but no interface in the RGB candidate "
            "order could be opened (permissions or another app may hold the device). "
            "Try closing vendor software and re-running `wraith debug probe`."
        )
        if not selected_reason:
            selected_reason = "RGB-ordered candidates exist but none are openable."

    return ProbeResult(
        device_count=device_count,
        candidate_count=candidate_count,
        vendor_usage_page_found=vendor_usage_page_found,
        any_openable=any_openable,
        selected_candidate=selected,
        selected_reason=selected_reason,
        recommendation=recommendation,
        rgb_ordered_candidates=rgb_ordered,
    )


def send_confirmed_test_rgb(
    vendor_id: int = DEFAULT_VENDOR_ID,
    product_id: int = DEFAULT_PRODUCT_ID,
) -> None:
    """Send one known-safe static RGB packet via ``ConnectionManager`` (vendor cmd 0x07 only)."""
    mgr = ConnectionManager(vendor_id, product_id)
    try:
        mgr.set_rgb(0, 3, 5, 255, 0, 255, 0)
    finally:
        mgr.close()


def format_enumerate_human(rows: list[dict[str, Any]], vendor_id: int, product_id: int) -> str:
    lines: list[str] = []
    lines.append(f"HID interfaces for VID/PID {vendor_id:04x}:{product_id:04x} (count={len(rows)})")
    lines.append("")
    for i, r in enumerate(rows):
        lines.append(f"--- Interface #{i} ---")
        for k in (
            "vendor_id",
            "product_id",
            "path",
            "interface_number",
            "usage_page",
            "usage",
            "manufacturer_string",
            "product_string",
            "serial_number",
            "release_number",
            "candidate_role",
            "openable",
            "open_error",
        ):
            lines.append(f"  {k}: {r.get(k)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_probe_human(pr: ProbeResult, *, include_rgb_test_footer: bool = False) -> str:
    lines: list[str] = []
    if include_rgb_test_footer:
        lines.append("Wraith HID probe (RGB test section follows)")
    else:
        lines.append("Wraith HID compatibility probe (read-only; no packet sent in this mode)")
    lines.append("")
    lines.append(f"  device_count: {pr.device_count}")
    lines.append(f"  candidate_count (ConnectionManager order): {pr.candidate_count}")
    lines.append(f"  vendor_usage_page_0xFF1B_found: {pr.vendor_usage_page_found}")
    lines.append(f"  any_rgb_candidate_openable: {pr.any_openable}")
    lines.append(f"  selected_reason: {pr.selected_reason}")
    lines.append("")
    if pr.selected_candidate:
        lines.append("  selected_candidate (first openable in CM order):")
        for k, v in pr.selected_candidate.items():
            lines.append(f"    {k}: {v}")
    else:
        lines.append("  selected_candidate: (none)")
    lines.append("")
    lines.append("  recommendation:")
    lines.append(f"    {pr.recommendation}")
    lines.append("")
    return "\n".join(lines)
