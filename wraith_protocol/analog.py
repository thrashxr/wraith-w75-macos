"""Analog / Hall-effect configuration — pending reverse engineering (not exported from package)."""


def build_actuation_packet(
    key_index: int,
    actuation_um: int,
) -> bytes:
    """Build HID packet to set actuation point (depth) for a key.

    Raises:
        NotImplementedError: Command bytes and offsets are not verified in ``witmodSdk.dll.c`` yet.
    """
    raise NotImplementedError("Pending RE: command bytes unverified")


def build_rapid_trigger_packet(
    key_index: int,
    enabled: bool,
    press_um: int,
    release_um: int,
) -> bytes:
    """Build HID packet to configure rapid trigger for a key.

    Raises:
        NotImplementedError: Command bytes and offsets are not verified in ``witmodSdk.dll.c`` yet.
    """
    raise NotImplementedError("Pending RE: command bytes unverified")
