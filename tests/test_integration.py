"""USB integration: requires Wraith W75 attached."""

import pytest

from wraith_core import ConnectionManager, DeviceNotFound, HidApiNotAvailable


@pytest.mark.integration
def test_live_set_rgb_static() -> None:
    mgr = ConnectionManager()
    try:
        mgr.set_rgb(0, 3, 5, 255, 0, 255, 0)
    except HidApiNotAvailable as exc:
        pytest.skip(str(exc))
    except DeviceNotFound as exc:
        pytest.fail(f"Wraith W75 not available for integration test: {exc}")
    finally:
        mgr.close()
