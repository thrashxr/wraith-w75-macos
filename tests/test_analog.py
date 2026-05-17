import pytest
from wraith_protocol.analog import build_actuation_packet, build_rapid_trigger_packet

def test_build_actuation_packet_raises_not_implemented():
    """Verify that build_actuation_packet raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Pending RE: command bytes unverified"):
        build_actuation_packet(key_index=0, actuation_um=1000)

def test_build_rapid_trigger_packet_raises_not_implemented():
    """Verify that build_rapid_trigger_packet raises NotImplementedError."""
    with pytest.raises(NotImplementedError, match="Pending RE: command bytes unverified"):
        build_rapid_trigger_packet(key_index=0, enabled=True, press_um=1000, release_um=1000)
