"""Core exceptions for HID transport and device discovery."""


class DeviceNotFound(Exception):
    """No compatible HID interface could be opened for the configured VID/PID."""


class HidOpenError(Exception):
    """A specific HID path refused to open (``OSError`` from hidapi)."""


class TransportError(Exception):
    """Write/read failed on an open handle (unexpected I/O error)."""


class ReconnectFailed(Exception):
    """Exceeded ``max_retries`` while attempting to reconnect after a transport failure."""


class HidApiNotAvailable(RuntimeError):
    """The ``hid`` Python module could not load the native ``hidapi`` shared library."""
