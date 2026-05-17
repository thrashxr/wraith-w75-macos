# wraith-w75

> **Warning — read before use**
>
> **Experimental reverse-engineered software.** Behavior depends on undocumented vendor HID traffic; it is **not supported or endorsed by the keyboard manufacturer**. There is **no firmware flashing or bootloader support** in this repository; misuse of HID tooling elsewhere can still damage devices. **Use at your own risk.** See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues with the diagnostics we need.

Open-source Python SDK and CLI for **Wraith W75 / W75 Pro** vendor HID control on **macOS** (and other platforms with `hidapi`). On **tested W75 hardware**, RGB lighting is sent over a vendor interface that enumerates with **`usage_page 0xFF1B`** (see Turkish docs for evidence levels and caveats).

Detailed design notes, troubleshooting, and rationale (Turkish): [docs/README.md](docs/README.md).

## Compatibility matrix

| Device     | Firmware | Status   |
|------------|----------|----------|
| W75 Pro    | unknown  | tested   |
| W75 ANSI   | unknown  | untested |

If you confirm behavior on another SKU or firmware, open a PR to update this table (include evidence per [CONTRIBUTING.md](CONTRIBUTING.md)).

## Supported now / Not supported yet

**Supported now (v0.1)**

- RGB / lighting commands as a **64-byte** HID output report with CRC (**verified** on tested W75; see [docs/11-command-map.md](docs/11-command-map.md)).
- **`wraith` CLI:** `set-color`, `status`, `debug enumerate`, `debug probe`.
- **`ConnectionManager`** in `wraith_core`: connect, write, reconnect, `set_rgb`.

**Not supported yet**

- Analog / actuation / rapid-trigger HID commands (`wraith_protocol.analog` is **stub only**, **not a public API** — not exported from `wraith_protocol`).
- Firmware update, bootloader, or persistent profile write paths (intentionally out of scope; **unsafe**).
- HTTP API (`wraith_api` is reserved; phase 2).

## Install (editable)

```bash
cd /path/to/wraith
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## CLI

```bash
wraith set-color --r 255 --g 0 --b 0 --mode static
wraith set-color --r 255 --g 0 --b 0 --mode breathe
wraith status
```

### Diagnostics (macOS-first)

Safe HID listing and compatibility checks (no writes unless both flags are used together):

```bash
wraith debug enumerate
wraith debug enumerate --json
wraith debug probe
wraith debug probe --json
```

Optional one-shot RGB test (same `ConnectionManager.set_rgb` path as `set-color`; requires explicit confirmation):

```bash
wraith debug probe --test-rgb --confirm
```

Details: [docs/12-hardware-compatibility.md](docs/12-hardware-compatibility.md).

## Tests

Unit tests (no USB device):

```bash
pytest
```

Hardware integration (Wraith W75 plugged in):

```bash
pytest --override-ini "addopts=" -m integration
```

Default `pytest` excludes `@pytest.mark.integration` via `addopts` in `pyproject.toml`.

## macOS notes

- Vendor HID **`0x0416:0x7372`**; enumeration prefers **`usage_page 0xFF1B`** first on **tested** W75 — not guaranteed for all revisions or clones.
- **Native hidapi:** the PyPI `hid` package loads `libhidapi` by short SONAME; Homebrew does not put that on the default dyld path. This SDK resolves `$(brew --prefix hidapi)/lib` (and Cellar) and **temporarily redirects** `ctypes.cdll.LoadLibrary` while `hid` imports so the correct `libhidapi*.dylib` is used.

  ```bash
  brew install hidapi
  ```

  If problems persist, run `brew --prefix hidapi` and `ls "$(brew --prefix hidapi)/lib"/libhidapi*.dylib` — those paths are what the loader tries first.

- If you add global input monitoring (e.g. optional tools later), grant **System Settings → Privacy & Security → Input Monitoring** and **Accessibility** to your terminal app as needed.

## Layout

| Package | Role |
|---------|------|
| `wraith_protocol` | CRC, packet layout, RGB command bytes |
| `wraith_core` | HID `ConnectionManager`, lock, reconnect, `diagnostics` (enumerate/probe) |
| `wraith_cli` | `wraith` entrypoint (calls **core only**) |
| `wraith_api` | Reserved for FastAPI (phase 2) |

## Examples

```bash
python examples/w75_demo.py
```

---

## Acknowledgements

This project was developed with research, implementation, and debugging support from Claude, Gemini, and ChatGPT.
