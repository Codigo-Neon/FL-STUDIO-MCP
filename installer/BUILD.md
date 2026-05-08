# FL MCP Studio — Build Instructions

## Quick start (Linux + Wine, recommended for dev)

Prerequisites:
- Wine 8+ installed (`apt install wine` on Debian/Kali)
- Inno Setup 6 installed under Wine (see "Installing Inno Setup" below)
- Python 3.11+ on the host (used to run the build helpers)

```bash
cd installer/build
./build.sh
```

The resulting `.exe` will be at `installer/build/dist/FL-MCP-Studio-Setup-v0.1.0.exe`.

## Quick start (native Windows)

Prerequisites:
- Python 3.11+
- Inno Setup 6 (`iscc.exe` on PATH)

```cmd
cd installer\build
build.bat
```

(Note: `build.bat` is a thin Windows wrapper. It calls the same Python helpers and then `iscc setup.iss`.)

## Installing Inno Setup under Wine

Inno Setup is a Windows-only freeware program. To run it on Linux, use Wine:

```bash
# Download the official installer
wget https://files.jrsoftware.org/is/6/innosetup-6.2.2.exe -O /tmp/innosetup.exe

# Install silently into Wine's Program Files
wine /tmp/innosetup.exe /SILENT

# Verify ISCC runs
wine "$HOME/.wine/drive_c/Program Files (x86)/Inno Setup 6/iscc.exe" /?
```

The `build.sh` script auto-detects this path. If you installed elsewhere, set `ISCC_PATH` env var:

```bash
ISCC_PATH="/path/to/iscc.exe" ./build.sh
```

## Build steps (what `build.sh` does)

1. `fetch_python.py` downloads Python 3.11.9 embedded distribution from python.org
2. `install_deps.py` installs Windows wheels for `requirements.txt` into the embed's `Lib/site-packages`
3. `stage.py` copies project source files (trigger.py, device_test.py, knowledge/, installer/) into `installer/build/staging/`
4. `iscc setup.iss` (via Wine if Linux) compiles the staging tree into a single `.exe`
5. The resulting `.exe` is moved to `installer/build/dist/`

## Manual QA after build

See `installer/QA_CHECKLIST.md` for the end-to-end install + run checklist on a Windows 10/11 VM.
