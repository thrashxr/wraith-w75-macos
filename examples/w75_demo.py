#!/usr/bin/env python3
"""Interactive demo: RGB sequence via ``ConnectionManager`` (no asserts — use ``pytest`` for checks)."""

from __future__ import annotations

import argparse
import sys
import time

from wraith_core import ConnectionManager, DeviceNotFound, HidApiNotAvailable


def demo_rgb_sequence() -> None:
    mgr = ConnectionManager()
    try:
        mgr.set_rgb(0, 3, 5, 255, 0, 255, 0)
        print("Static magenta sent.")
        time.sleep(2)
        mgr.set_rgb(1, 3, 5, 0, 255, 0, 0)
        print("Breathe green sent.")
        time.sleep(2)
        mgr.set_rgb(2, 4, 5, 255, 0, 255, 0)
        print("Wave (mode 2) sent.")
    except HidApiNotAvailable as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except DeviceNotFound:
        print("Device not found.", file=sys.stderr)
        sys.exit(1)
    finally:
        mgr.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="W75 RGB demo using wraith_core")
    parser.add_argument("cmd", nargs="?", default="demo", choices=["demo"])
    args = parser.parse_args()
    if args.cmd == "demo":
        demo_rgb_sequence()


if __name__ == "__main__":
    main()
