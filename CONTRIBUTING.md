# Contributing

Thank you for helping improve wraith-w75. This project is **experimental reverse-engineered software** (see the [README](README.md) warning). Contributions should match existing style, stay within documented scope, and avoid firmware or unsafe HID probing.

## Before you open an issue

Many reports are impossible to act on without hardware context. **Incomplete issues may be closed** until the checklist below is filled in.

### Required information (copy into your issue)

Paste this block and answer every line:

```
### Environment
- **Keyboard model:** (e.g. W75 Pro, W75 ANSI)
- **Firmware version:** (from vendor app if available; if unknown, write `unknown`)
- **macOS version:** (e.g. 14.6.1 — this project is primarily tested on macOS)
- **Python version:** (output of `python3 --version`)

### USB / HID identity
- **VID:PID in use:** (decimal or hex, e.g. `0x0416:0x7372`)
- **usage_page** for the path you expect the SDK to use: (e.g. `0xFF1B` or `unknown`)
- **Interface / enumeration dump:** (attach text output — see commands below)

### What happened
- **Command run:** (exact CLI or minimal Python snippet)
- **Expected vs actual:**
```

### How to collect VID, PID, usage page, and interfaces

**macOS — HID list (preferred when available):**

```bash
hidutil list
```

Copy the rows that match your Wraith keyboard (vendor name, product, VID/PID, primary/usage page if shown).

**macOS — USB tree:**

```bash
system_profiler SPUSBDataType
```

Find the Wraith entry and paste that section.

**macOS — deeper I/O Registry (optional, can be long):**

```bash
ioreg -l -w0 -p IOUSB | grep -A 40 -i wraith
```

(or search for `0x0416` / `0x7372` if the marketing name differs)

**Python — what this SDK would enumerate (requires `hidapi` / `brew install hidapi`):**

```bash
python3 -c "import hid; print(hid.enumerate(0x0416, 0x7372))"
```

Paste the full list of dicts (mask serial numbers if you prefer).

## Pull requests

- Keep changes focused; follow [docs/09-decisions-and-non-goals.md](docs/09-decisions-and-non-goals.md) (no firmware paths, no command fuzzing).
- Run **`pytest`** locally before pushing (unit tests; no device required).
- Integration tests (`pytest --override-ini "addopts=" -m integration`) require a physical W75 and are optional for most PRs.

## Evidence and protocol changes

If you change packet layout, CRC, or command bytes, update the relevant docs under `docs/` (especially [docs/11-command-map.md](docs/11-command-map.md)) and extend or add **golden tests** in `tests/`, with a clear note on evidence level (`verified` / `observed`, etc.).
