"""CRC matches legacy ``crcmod`` / ``w75.py`` golden RGB packet."""

from wraith_protocol.crc import append_crc, digest

# build_rgb_command(0,3,5,255,0,255,0) — 64 bytes
_GOLDEN = bytes.fromhex(
    "01070000000e000305ff00ff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001ac1"
)


def test_digest_matches_golden_crc_value() -> None:
    body_for_crc = _GOLDEN[1:62]
    assert len(body_for_crc) == 61
    assert digest(body_for_crc) == 0x1AC1


def test_append_crc_round_trip() -> None:
    buf = bytearray(_GOLDEN[:62])
    append_crc(buf)
    assert bytes(buf) == _GOLDEN
