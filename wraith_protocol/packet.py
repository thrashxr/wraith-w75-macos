"""64-byte HID output report layout (Report ID 0x01)."""

from __future__ import annotations

from wraith_protocol.crc import append_crc

REPORT_SIZE = 64
REPORT_ID = 0x01


def make_packet(payload: bytearray) -> bytes:
    """Pad or trim ``payload`` to ``REPORT_SIZE - 2`` bytes, then append CRC (last 2 bytes).

    ``payload`` must be exactly ``REPORT_SIZE - 2`` bytes (62): byte 0 = report id,
    bytes 1..60 = body used in CRC input as ``payload[1:]`` (61 bytes), matching
    legacy ``w75.py`` behaviour (CRC over everything after report id through byte 60).
    """
    if len(payload) != REPORT_SIZE - 2:
        raise ValueError(
            f"payload must be {REPORT_SIZE - 2} bytes before CRC, got {len(payload)}"
        )
    if payload[0] != REPORT_ID:
        raise ValueError(f"first byte must be REPORT_ID {REPORT_ID:#04x}")
    buf = bytearray(payload)
    append_crc(buf)
    if len(buf) != REPORT_SIZE:
        raise RuntimeError("internal error: packet length after CRC")
    return bytes(buf)
