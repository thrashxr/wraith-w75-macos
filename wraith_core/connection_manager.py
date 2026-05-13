"""HID connection management: vendor path selection, single-writer lock, auto-reconnect."""

from __future__ import annotations

import ctypes
import glob
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from typing import Any, Literal

from wraith_core.exceptions import DeviceNotFound, HidApiNotAvailable, ReconnectFailed, TransportError
from wraith_protocol.lighting import build_rgb_command

State = Literal["disconnected", "connecting", "connected"]

_BACKOFF_S = (0.25, 0.5, 1.0, 2.0, 4.0)

# Fallback paths if ``brew --prefix`` / Cellar discovery finds nothing.
_DARWIN_HIDAPI_FIXED = (
    "/opt/homebrew/opt/hidapi/lib/libhidapi.0.dylib",
    "/opt/homebrew/opt/hidapi/lib/libhidapi.dylib",
    "/opt/homebrew/lib/libhidapi.0.dylib",
    "/opt/homebrew/lib/libhidapi.dylib",
    "/usr/local/opt/hidapi/lib/libhidapi.0.dylib",
    "/usr/local/opt/hidapi/lib/libhidapi.dylib",
    "/usr/local/lib/libhidapi.0.dylib",
    "/usr/local/lib/libhidapi.dylib",
)

_HID_MODULE: Any | None = None
_LAST_DARWIN_HIDAPI_TRIED: list[str] = []
_ctypes_orig_load_library = ctypes.cdll.LoadLibrary


def _brew_prefix_hidapi() -> str | None:
    try:
        r = subprocess.run(
            ["brew", "--prefix", "hidapi"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    p = (r.stdout or "").strip()
    return p or None


def _darwin_hidapi_library_paths() -> list[str]:
    """Resolve Homebrew keg + Cellar layouts (hidapi is not always linked into ``/opt/homebrew/lib``).

    Prefer loading the **symlink** ``libhidapi.dylib`` by absolute path: the PyPI ``hid`` module
    later calls ``LoadLibrary("libhidapi.dylib")``, which matches that install name.
    """
    ordered: list[str] = []
    seen_real: set[str] = set()

    def add(path: str) -> None:
        if not os.path.isfile(path):
            return
        key = os.path.realpath(path)
        if key in seen_real:
            return
        seen_real.add(key)
        ordered.append(path)

    bp = _brew_prefix_hidapi()
    if bp:
        lib = os.path.join(bp, "lib")
        if os.path.isdir(lib):
            for name in ("libhidapi.dylib", "libhidapi.0.dylib"):
                add(os.path.join(lib, name))
            for p in sorted(glob.glob(os.path.join(lib, "libhidapi*.dylib"))):
                add(p)
    for prefix in ("/opt/homebrew", "/usr/local"):
        for p in sorted(glob.glob(os.path.join(prefix, "Cellar", "hidapi", "*", "lib", "libhidapi*.dylib"))):
            add(p)
    for p in _DARWIN_HIDAPI_FIXED:
        add(p)
    return ordered


def _darwin_patched_load_library(name: str | bytes, *args: Any, **kwargs: Any) -> Any:
    """Redirect short ``libhidapi*`` names to Homebrew absolute paths (PyPI ``hid`` uses bare SONAMEs)."""
    global _LAST_DARWIN_HIDAPI_TRIED
    if not isinstance(name, (str, bytes)):
        return _ctypes_orig_load_library(name, *args, **kwargs)
    name_s = name.decode("utf-8", errors="replace") if isinstance(name, bytes) else name
    if os.path.isabs(name_s) or "hidapi" not in name_s:
        return _ctypes_orig_load_library(name, *args, **kwargs)
    candidates = _darwin_hidapi_library_paths()
    _LAST_DARWIN_HIDAPI_TRIED = list(candidates)
    for path in candidates:
        try:
            return _ctypes_orig_load_library(path, *args, **kwargs)
        except OSError:
            continue
    return _ctypes_orig_load_library(name, *args, **kwargs)


def _hid() -> Any:
    """Return the ``hid`` module (cached). On macOS, patches ``ctypes.cdll.LoadLibrary`` while ``hid`` imports."""
    global _HID_MODULE
    if _HID_MODULE is not None:
        return _HID_MODULE
    darwin = sys.platform == "darwin"
    if darwin:
        ctypes.cdll.LoadLibrary = _darwin_patched_load_library  # type: ignore[method-assign]
    try:
        import hid
    except ImportError as exc:
        tried = _LAST_DARWIN_HIDAPI_TRIED or _darwin_hidapi_library_paths()
        tail = ", ".join(tried[:8]) + (" …" if len(tried) > 8 else "")
        raise HidApiNotAvailable(
            "Could not load native hidapi (libhidapi) for the Python ``hid`` package.\n"
            "Install with: brew install hidapi\n"
            "If it is already installed, run: ls \"$(brew --prefix hidapi)/lib\"/libhidapi*.dylib\n"
            f"Resolved library candidates ({len(tried)}): {tail or 'none'}"
        ) from exc
    finally:
        if darwin:
            ctypes.cdll.LoadLibrary = _ctypes_orig_load_library  # type: ignore[method-assign]
    _HID_MODULE = hid
    return hid


def ordered_hid_candidates(candidates: list[dict]) -> list[dict]:
    """Prefer ``usage_page == 0xFF1B``, then other ``interface_number > 0`` (legacy ``w75.py`` order).

    ``candidates`` is the raw list from ``hid.enumerate`` for one VID/PID. Shared with diagnostics.
    """
    preferred = [d for d in candidates if d.get("usage_page") == 0xFF1B]
    fallback = [d for d in candidates if d.get("interface_number", 0) > 0 and d not in preferred]
    return preferred + fallback


def _ordered_hid_candidates(vendor_id: int, product_id: int) -> list[dict]:
    return ordered_hid_candidates(list(_hid().enumerate(vendor_id, product_id)))


class ConnectionManager:
    """Single owner of the vendor ``hid.device`` handle: ``set_rgb`` builds packets inside core."""

    DEFAULT_VENDOR_ID = 0x0416
    DEFAULT_PRODUCT_ID = 0x7372

    def __init__(
        self,
        vendor_id: int | None = None,
        product_id: int | None = None,
        *,
        max_retries: int | None = None,
        on_state_change: Callable[[State], None] | None = None,
    ) -> None:
        self.vendor_id = int(vendor_id or self.DEFAULT_VENDOR_ID)
        self.product_id = int(product_id or self.DEFAULT_PRODUCT_ID)
        self.max_retries = max_retries
        self.on_state_change = on_state_change
        self._lock = threading.RLock()
        self._device: Any = None
        self._state: State = "disconnected"
        self._open_path_repr: str | None = None
        self._backoff_index = 0

    @property
    def state(self) -> State:
        return self._state

    def _emit_state(self, new_state: State) -> None:
        self._state = new_state
        if self.on_state_change is not None:
            self.on_state_change(new_state)

    def connect(self) -> bool:
        """Enumerate and open the first compatible path. Returns ``False`` if none open."""
        with self._lock:
            self._emit_state("connecting")
            self._close_nolock()
            try:
                ordered = _ordered_hid_candidates(self.vendor_id, self.product_id)
            except HidApiNotAvailable:
                self._emit_state("disconnected")
                raise
            hm = _hid()
            open_errors: tuple[type[BaseException], ...] = (OSError, ValueError)
            hid_exc = getattr(hm, "HIDException", None)
            if hid_exc is not None:
                open_errors = (hid_exc, OSError, ValueError)
            for dev in ordered:
                path = dev["path"]
                try:
                    handle = hm.Device(path=path)
                except open_errors:
                    continue
                self._device = handle
                self._open_path_repr = repr(path)
                self._backoff_index = 0
                self._emit_state("connected")
                return True
            self._emit_state("disconnected")
            return False

    def _close_nolock(self) -> None:
        if self._device is not None:
            try:
                self._device.close()
            except OSError:
                pass
            self._device = None
            self._open_path_repr = None

    def close(self) -> None:
        with self._lock:
            self._close_nolock()
            self._emit_state("disconnected")

    def ensure_connected(self) -> None:
        """Raise ``DeviceNotFound`` if the keyboard is not attached or no path opens."""
        with self._lock:
            if self._device is not None:
                return
        if not self.connect():
            raise DeviceNotFound(
                f"No HID path opened for {self.vendor_id:#06x}:{self.product_id:#06x} "
                "(vendor 0xFF1B preferred)"
            )

    def status(self) -> dict[str, object]:
        """Snapshot for CLI / API (no I/O)."""
        with self._lock:
            return {
                "state": self._state,
                "vendor_id": self.vendor_id,
                "product_id": self.product_id,
                "connected": self._device is not None,
                "open_path": self._open_path_repr,
            }

    def _sleep_backoff(self) -> None:
        idx = min(self._backoff_index, len(_BACKOFF_S) - 1)
        time.sleep(_BACKOFF_S[idx])
        if self._backoff_index < len(_BACKOFF_S) - 1:
            self._backoff_index += 1

    def set_rgb(
        self,
        mode: int,
        speed: int,
        brightness: int,
        r: int,
        g: int,
        b: int,
        direction: int = 0,
    ) -> None:
        """Build the RGB packet inside core and write it (exclusive access + reconnect)."""
        payload = build_rgb_command(mode, speed, brightness, r, g, b, direction)
        self._write_with_reconnect(payload)

    def _write_with_reconnect(self, payload: bytes) -> None:
        hm = _hid()
        write_errors: tuple[type[BaseException], ...] = (OSError, ValueError)
        hid_exc = getattr(hm, "HIDException", None)
        if hid_exc is not None:
            write_errors = (hid_exc, OSError, ValueError)
        attempt = 0
        while True:
            self.ensure_connected()
            try:
                with self._lock:
                    if self._device is None:
                        raise TransportError("HID device became None after connect")
                    self._device.write(bytes(payload))
                with self._lock:
                    self._backoff_index = 0
                return
            except write_errors as exc:
                with self._lock:
                    self._close_nolock()
                    self._emit_state("disconnected")
                if self.max_retries is not None and attempt >= self.max_retries:
                    raise ReconnectFailed(
                        f"write failed after {self.max_retries} reconnect attempts"
                    ) from exc
                attempt += 1
                self._sleep_backoff()
