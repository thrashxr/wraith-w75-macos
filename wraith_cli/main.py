"""Console entrypoint: ``wraith``. Uses **wraith_core** only (no direct protocol imports)."""

from __future__ import annotations

import argparse
import json
import sys

from wraith_core import ConnectionManager, DeviceNotFound, HidApiNotAvailable, ReconnectFailed
from wraith_core import diagnostics as diag


def _mode_to_int(name: str) -> int:
    mapping = {"static": 0, "breathe": 1}
    try:
        return mapping[name.lower()]
    except KeyError as exc:
        raise argparse.ArgumentTypeError(f"unknown mode {name!r}; expected static|breathe") from exc


def _uint8(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid integer") from exc
    if not (0 <= ivalue <= 255):
        raise argparse.ArgumentTypeError(f"{ivalue} is out of range (0-255)")
    return ivalue


def cmd_status(_ns: argparse.Namespace) -> int:
    mgr = ConnectionManager()
    try:
        mgr.ensure_connected()
        print(json.dumps(mgr.status(), indent=2))
        return 0
    except HidApiNotAvailable as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    except DeviceNotFound:
        print(
            json.dumps(
                {
                    **{k: v for k, v in mgr.status().items()},
                    "hint": "device not found or no HID path opened",
                },
                indent=2,
            )
        )
        return 1
    finally:
        mgr.close()


def cmd_set_color(ns: argparse.Namespace) -> int:
    mode = _mode_to_int(ns.mode)
    speed = ns.speed
    brightness = ns.brightness
    mgr = ConnectionManager(max_retries=ns.max_retries)
    try:
        mgr.set_rgb(mode, speed, brightness, ns.r, ns.g, ns.b, ns.direction)
    except HidApiNotAvailable as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except DeviceNotFound:
        print("Device not found: connect Wraith W75 and grant HID access.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        mgr.close()
    print("OK: RGB command sent.")
    return 0


def cmd_debug_enumerate(ns: argparse.Namespace) -> int:
    try:
        rows = diag.enumerate_wraith_interfaces()
    except HidApiNotAvailable as exc:
        if ns.json:
            print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        else:
            print(str(exc), file=sys.stderr)
        return 1
    if ns.json:
        print(
            json.dumps(
                {
                    "vendor_id": diag.DEFAULT_VENDOR_ID,
                    "product_id": diag.DEFAULT_PRODUCT_ID,
                    "interfaces": rows,
                },
                indent=2,
            )
        )
    else:
        print(
            diag.format_enumerate_human(rows, diag.DEFAULT_VENDOR_ID, diag.DEFAULT_PRODUCT_ID),
            end="",
        )
    return 0


def cmd_debug_probe(ns: argparse.Namespace) -> int:
    test_rgb = getattr(ns, "test_rgb", False)
    confirm = getattr(ns, "confirm", False)
    if test_rgb != confirm:
        msg = "error: --test-rgb and --confirm must be used together (no HID write unless both are set)."
        print(msg, file=sys.stderr)
        return 2

    try:
        pr = diag.probe_wraith_hid()
    except HidApiNotAvailable as exc:
        if ns.json:
            print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        else:
            print(str(exc), file=sys.stderr)
        return 1

    if ns.json:
        out = pr.to_json_dict()
        if test_rgb and confirm:
            out["rgb_test_requested"] = True
            try:
                diag.send_confirmed_test_rgb()
                out["rgb_test"] = {"status": "ok", "message": "one static RGB packet sent"}
            except HidApiNotAvailable as exc:
                out["rgb_test"] = {"status": "error", "message": str(exc)}
                print(json.dumps(out, indent=2))
                return 1
            except DeviceNotFound:
                out["rgb_test"] = {"status": "error", "message": "device not found or no HID path opened"}
                print(json.dumps(out, indent=2))
                return 1
            except ReconnectFailed as exc:
                out["rgb_test"] = {"status": "error", "message": str(exc)}
                print(json.dumps(out, indent=2))
                return 1
            except Exception as exc:  # noqa: BLE001
                out["rgb_test"] = {"status": "error", "message": str(exc)}
                print(json.dumps(out, indent=2))
                return 1
            print(json.dumps(out, indent=2))
        else:
            print(json.dumps(out, indent=2))
    else:
        print(
            diag.format_probe_human(pr, include_rgb_test_footer=bool(test_rgb and confirm)),
            end="",
        )

    if test_rgb and confirm and not ns.json:
        try:
            diag.send_confirmed_test_rgb()
        except HidApiNotAvailable as exc:
            print(str(exc), file=sys.stderr)
            return 1
        except DeviceNotFound:
            print("RGB test failed: device not found or no HID path opened.", file=sys.stderr)
            return 1
        except ReconnectFailed as exc:
            print(f"RGB test failed (reconnect): {exc}", file=sys.stderr)
            return 1
        except Exception as exc:  # noqa: BLE001 — CLI surface
            print(f"RGB test failed: {exc}", file=sys.stderr)
            return 1
        print("OK: one static RGB test packet sent (magenta / same vector as golden demo).")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wraith", description="Wraith W75 vendor HID CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show connection state and HID path (if connected)")
    p_status.set_defaults(func=cmd_status)

    p_rgb = sub.add_parser("set-color", help="Send RGB / lighting command via vendor HID")
    p_rgb.add_argument("--r", type=_uint8, default=255, metavar="0-255")
    p_rgb.add_argument("--g", type=_uint8, default=0, metavar="0-255")
    p_rgb.add_argument("--b", type=_uint8, default=0, metavar="0-255")
    p_rgb.add_argument("--mode", type=str, required=True, choices=["static", "breathe"])
    p_rgb.add_argument("--speed", type=_uint8, default=3, metavar="0-255")
    p_rgb.add_argument("--brightness", type=_uint8, default=5, metavar="0-255")
    p_rgb.add_argument("--direction", type=_uint8, default=0, metavar="0-255")
    p_rgb.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help="Max reconnect attempts after write failure (default: unlimited)",
    )
    p_rgb.set_defaults(func=cmd_set_color)

    p_debug = sub.add_parser("debug", help="HID diagnostics (enumerate, probe)")
    dsub = p_debug.add_subparsers(dest="debug_command", required=True)

    p_enum = dsub.add_parser("enumerate", help="List HID interfaces for default Wraith VID/PID")
    p_enum.add_argument("--json", action="store_true", help="Print JSON to stdout")
    p_enum.set_defaults(func=cmd_debug_enumerate)

    p_probe = dsub.add_parser("probe", help="Compatibility probe (no write unless --test-rgb --confirm)")
    p_probe.add_argument("--json", action="store_true", help="Print JSON to stdout")
    p_probe.add_argument(
        "--test-rgb",
        action="store_true",
        help="After probe, send one known-safe static RGB packet (requires --confirm)",
    )
    p_probe.add_argument(
        "--confirm",
        action="store_true",
        help="Acknowledge intentional HID write (only with --test-rgb)",
    )
    p_probe.set_defaults(func=cmd_debug_probe)

    ns = parser.parse_args(argv)
    return int(ns.func(ns))


if __name__ == "__main__":
    raise SystemExit(main())
