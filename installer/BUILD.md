# FL MCP Studio — Build Instructions

## Quick start (Linux + Wine, recommended for dev on Kali)

Prerequisites:
- Wine 8+ installed (`apt install wine` on Debian/Kali)
- Inno Setup 6 installed under Wine (see "Installing Inno Setup" below)
- Python 3.11+ on the host (used to run the build helpers)

```bash
cd installer/build
./build.sh
```

The resulting `.exe` will be at `installer/build/dist/FL-MCP-Studio-Setup-v0.1.0.exe` (typically ~50-80 MB).

## Quick start (native Windows)

Prerequisites:
- Python 3.11+ on PATH
- Inno Setup 6 (`iscc.exe` on PATH or in default install location)

```bash
cd installer/build
./build.sh
```

(The same `build.sh` works on Windows via Git Bash, MSYS, or WSL.)

## Installing Inno Setup under Wine

Inno Setup is Windows-only freeware. To run it on Linux, use Wine:

```bash
# Download the official installer
wget https://files.jrsoftware.org/is/6/innosetup-6.2.2.exe -O /tmp/innosetup.exe

# Install silently into Wine's Program Files
wine /tmp/innosetup.exe /SILENT

# Verify ISCC runs
wine "$HOME/.wine/drive_c/Program Files (x86)/Inno Setup 6/iscc.exe" /?
```

The `build.sh` script auto-detects this default path. Override with `ISCC_PATH`:

```bash
ISCC_PATH="/path/to/iscc.exe" ./build.sh
```

## What `build.sh` does (5 steps)

1. **Fetch Python embedded** (`fetch_python.py`) — Downloads `python-3.11.9-embed-amd64.zip` from python.org, extracts to `installer/build/staging/python-embed/`, patches `python311._pth` to enable `site-packages`.
2. **Install wheels** (`install_deps.py`) — Runs `pip install --platform win_amd64 --python-version 311 --only-binary=:all: -r requirements.txt --target=staging/python-embed/Lib/site-packages`. All 7 deps (mido, python-rtmidi, fl-studio-api-stubs, pywebview, pystray, Pillow, psutil) have published cp311-win_amd64 wheels.
3. **Stage source** (`stage.py`) — Copies `trigger.py`, `device_test.py`, `knowledge/`, `installer/` (everything except `tests/`, `build/`, `__pycache__/`, `.pyc`). Writes `flmcp.bat` launcher.
4. **Compile installer** — Runs `iscc setup.iss` (via Wine on Linux). Inno Setup compresses the staging tree into a single `.exe`.
5. **Verify** — Confirms output exists, prints size in MB.

## Architecture of the resulting install

After the user double-clicks `FL-MCP-Studio-Setup-v0.1.0.exe` and clicks Next > Install:

```
C:\Program Files\FL MCP Studio\
├── python-embed\
│   ├── python.exe
│   ├── python311.dll
│   ├── python311._pth          (patched: import site enabled)
│   └── Lib\site-packages\      (all wheels)
├── trigger.py
├── device_test.py
├── knowledge\                  (production knowledge modules)
├── installer\
│   ├── main.py                 (entry point)
│   ├── setup_engine\
│   ├── wizard\
│   ├── tray\
│   └── assets\
└── flmcp.bat                   (launcher: python.exe -m installer.main)
```

Start Menu entry "FL MCP Studio" → `flmcp.bat` → wizard or tray (depending on `state.json`).

## Manual QA after build

Test on a Windows 10/11 VM:

1. Copy the `.exe` to the VM
2. Run it (right-click → Run as administrator)
3. Click through the Inno Setup wizard
4. After install, the FL MCP Studio wizard should auto-launch
5. Follow `installer/QA_CHECKLIST.md` for the full end-to-end checklist

## Troubleshooting

**`pip install --platform win_amd64` fails with "no matching distribution"**
- A dependency in `requirements.txt` may not have a Windows wheel. Check PyPI for the package's "Download files" page. If only sdists exist, you'll need to build the wheel separately or use a wheel from gohlke's repository.

**`wine iscc.exe` exits with "Cannot find file" for `setup.iss`**
- iscc resolves relative paths from its own cwd. Make sure `build.sh` does `cd "$INSTALLER_DIR"` before invoking iscc — the script does this, but if running iscc manually, cd into `installer/` first.

**The .exe installs but the wizard doesn't launch**
- Check that `python-embed\python311._pth` has `import site` (uncommented) — without this, site-packages isn't on sys.path and the wizard's imports fail silently.
- Check `flmcp.bat` is at the install root and is executable.
- Try running `python-embed\python.exe -m installer.main` from a `cmd.exe` started in the install dir to see real error output.

**The .exe is too small (<10 MB)**
- The wheels probably failed to download. Check `pip install` output during build for errors.
- The build.sh script aborts with a warning if size < 10 MB.

## Future improvements (not in v0.1)

- GitHub Actions release workflow on tag push (deferred)
- Code signing (Sectigo cert ~$80/year, not justified yet)
- Auto-update with delta patches (auto-update notification only is in v0.1; install is manual)
- Branded icons (current PNGs are colored placeholders)
