"""RGB / lighting command (cmd type 0x07) — byte layout aligned with legacy ``w75.py``."""

from __future__ import annotations

import struct

from wraith_protocol.packet import REPORT_ID, REPORT_SIZE, make_packet


def build_rgb_command(
    mode: int,
    speed: int,
    brightness: int,
    r: int,
    g: int,
    b: int,
    direction: int = 0,
) -> bytes:
    """Build a full 64-byte HID report for RGB/lighting (cmd ``0x07``).

    Indices (0-based), same as ``w75.py``:

    - ``0``: Report ID ``0x01``
    - ``1``: Command type ``0x07``
    - ``2..5``: ``0x00, 0x00, 0x00, 0x0e``
    - ``6``: mode
    - ``7``: speed
    - ``8``: brightness
    - ``9``: R
    - ``10``: G
    - ``11``: B
    - ``12``: direction
    - ``13..59``: zero padding
    - ``60..61``: CRC-16/XMODEM big-endian over bytes ``1..60`` inclusive (61 bytes)
    """
    payload = bytearray(REPORT_SIZE - 2)
    payload[0] = REPORT_ID
    payload[1] = 0x07
    payload[2:6] = struct.pack("<BBBB", 0x00, 0x00, 0x00, 0x0E)
    payload[6] = mode & 0xFF
    payload[7] = speed & 0xFF
    payload[8] = brightness & 0xFF
    payload[9] = r & 0xFF
    payload[10] = g & 0xFF
    payload[11] = b & 0xFF
    payload[12] = direction & 0xFF
    # 13..59 already zero from bytearray init
    return make_packet(payload)
