"""Lighting packet bytes (golden vector)."""

from wraith_protocol.lighting import build_rgb_command

_GOLDEN = bytes.fromhex(
    "01070000000e000305ff00ff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001ac1"
)


def test_build_rgb_command_default_demo_vector() -> None:
    """Same parameters as legacy ``w75.py`` first ``send_command`` demo (mode 0)."""
    assert build_rgb_command(0, 3, 5, 255, 0, 255, 0) == _GOLDEN
