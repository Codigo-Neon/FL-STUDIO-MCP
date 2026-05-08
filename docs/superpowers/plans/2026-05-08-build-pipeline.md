# Build Pipeline + Inno Setup Implementation Plan (Sub-project D)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a single Windows `.exe` installer (`FL-MCP-Studio-Setup-v0.1.0.exe`) that bundles Python 3.11 embedded distribution + all wheels + the project source code (`trigger.py`, `device_test.py`, `knowledge/`, `installer/`). The user double-clicks the `.exe`, Inno Setup runs the standard "Next > Next > Finish" install flow, and on completion launches the wizard from sub-project C. Cross-buildable from Linux dev (Kali) using Wine + Inno Setup ISCC.

**Architecture:** Three Python build helpers under `installer/build/` orchestrate fetching, dep-staging, and source-staging; one Inno Setup script (`installer/setup.iss`) declares the file inclusion + install flow; one shell script (`installer/build/build.sh`) ties everything together with a Wine-aware ISCC invocation. The bundle uses **embedded Python (no PyInstaller)** — same `python-embed/python.exe` path the wizard's `wizard.js` already hardcodes, so no Plan C refactor needed.

**Tech Stack:** Python 3.11.9 embedded distribution (downloaded fresh each build), pip with `--platform win_amd64 --only-binary=:all:` for cross-arch wheel install, Inno Setup 6 (run via Wine on Linux), bash for orchestration, stdlib `urllib.request`/`zipfile`/`shutil` for fetch/extract.

**Spec reference:** `docs/superpowers/specs/2026-05-03-windows-installer-design.md` section 8 ("Build & distribución"). NOTE: spec called for PyInstaller; we deviate to embedded Python for simplicity, smaller bundle, fewer AV false positives, and zero Plan C refactor needed.

**Test strategy:** Unit tests for the build helpers' pure functions (URL construction, file enumeration, manifest validation). Build-time verification: `iscc` exits 0, the produced `.exe` exists with expected size (>30 MB), `7z l` lists the expected entries. End-to-end install verification is manual on Windows VM via the QA checklist from sub-project C plus a new `installer/BUILD.md`.

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `installer/build/__init__.py` | Create | Empty package marker |
| `installer/build/fetch_python.py` | Create | Download Python 3.11 embedded ZIP, extract, patch `_pth` |
| `installer/build/install_deps.py` | Create | Cross-install Windows wheels into the embed's `Lib/site-packages` |
| `installer/build/stage.py` | Create | Copy source + assets into a clean staging tree for ISCC |
| `installer/build/build.sh` | Create | Orchestrator: fetch → install_deps → stage → iscc → verify |
| `installer/setup.iss` | Create | Inno Setup script: metadata, [Files], [Icons], [Run], [UninstallDelete] |
| `installer/flmcp.bat` | Create | Tiny launcher: `python-embed\python.exe -m installer.main` |
| `installer/BUILD.md` | Create | Step-by-step build instructions for Linux+Wine and native Windows |
| `tests/build/__init__.py` | Create | Empty package marker |
| `tests/build/test_fetch_python.py` | Create | Unit tests for the URL/version helpers |
| `tests/build/test_stage.py` | Create | Unit tests for the staging logic |
| `.gitignore` | Modify | Ignore `installer/build/.cache/`, `installer/build/staging/`, `installer/build/dist/` |
| `CLAUDE.md` | Modify | Add Build pipeline section under "Sistema de Instalación (Windows)" |

---

## Task 1: Scaffold + .gitignore + BUILD.md skeleton

**Files:**
- Create: `installer/build/__init__.py`
- Create: `installer/build/.gitkeep` (only if no other files yet — removed at end of Task 2)
- Create: `tests/build/__init__.py`
- Create: `installer/BUILD.md`
- Modify: `.gitignore`

- [ ] **Step 1: Create the build package directory**

```bash
cd "/home/roska/Documentos/FL MCP"
mkdir -p installer/build tests/build
```

- [ ] **Step 2: Create empty `__init__.py` files**

Create as zero-byte files:
- `installer/build/__init__.py`
- `tests/build/__init__.py`

- [ ] **Step 3: Update `.gitignore`**

Use the Edit tool. Find this block in `.gitignore`:

```
# Git worktrees
.worktrees/
```

Append after it:

```
# Build artifacts (sub-project D)
installer/build/.cache/
installer/build/staging/
installer/build/dist/
```

- [ ] **Step 4: Create `installer/BUILD.md` skeleton**

```markdown
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
```

- [ ] **Step 5: Verify pytest still discovers existing tests**

```bash
source .venv/bin/activate
pytest --collect-only 2>&1 | tail -3
```

Expected: 91 tests collected. No errors about new dirs.

- [ ] **Step 6: Commit**

```bash
git add .gitignore installer/build/__init__.py tests/build/__init__.py installer/BUILD.md
git commit -m "chore(build): scaffold installer/build/ + BUILD.md skeleton"
```

---

## Task 2: `fetch_python.py` — download Python embedded distribution

**Files:**
- Create: `installer/build/fetch_python.py`
- Create: `tests/build/test_fetch_python.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/build/test_fetch_python.py`:

```python
"""Tests for installer.build.fetch_python."""
import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from installer.build.fetch_python import (
    PYTHON_VERSION,
    embed_zip_url,
    fetch_and_extract,
    patch_pth_to_enable_site,
)


class TestEmbedZipUrl:
    def test_default_version_url(self):
        url = embed_zip_url()
        assert url.startswith("https://www.python.org/ftp/python/")
        assert PYTHON_VERSION in url
        assert url.endswith(f"python-{PYTHON_VERSION}-embed-amd64.zip")

    def test_custom_version_url(self):
        url = embed_zip_url(version="3.12.0")
        assert "3.12.0" in url


class TestPatchPthToEnableSite:
    def test_uncomments_import_site(self, fs):
        pth = Path("/embed/python311._pth")
        fs.create_file(
            str(pth),
            contents="python311.zip\n.\n\n# Uncomment to run site.main() automatically\n#import site\n",
        )

        patch_pth_to_enable_site(pth)

        text = pth.read_text()
        assert "\nimport site\n" in text
        assert "#import site" not in text


class TestFetchAndExtract:
    def test_downloads_and_extracts(self, monkeypatch, fs):
        # Build a fake embed zip in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("python.exe", b"FAKE EXE")
            zf.writestr("python311._pth", "python311.zip\n.\n#import site\n")

        fake_response = MagicMock()
        fake_response.read.return_value = buf.getvalue()
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr(
            "urllib.request.urlopen",
            MagicMock(return_value=fake_response),
        )

        target_dir = Path("/embed")
        result = fetch_and_extract(target_dir=target_dir)

        assert result == target_dir
        assert (target_dir / "python.exe").read_bytes() == b"FAKE EXE"
        # _pth must have been patched
        pth = (target_dir / "python311._pth").read_text()
        assert "\nimport site\n" in pth

    def test_creates_target_dir_if_missing(self, monkeypatch, fs):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("python311._pth", "#import site\n")

        fake_response = MagicMock()
        fake_response.read.return_value = buf.getvalue()
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=fake_response))

        target_dir = Path("/does/not/exist/yet")
        fetch_and_extract(target_dir=target_dir)

        assert target_dir.is_dir()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/build/test_fetch_python.py -v
```

Expected: ImportError on `installer.build.fetch_python`.

- [ ] **Step 3: Implement `fetch_python.py`**

Create `installer/build/fetch_python.py`:

```python
"""Download Python 3.11 embedded distribution from python.org and prepare it
for use as the bundled interpreter inside the installer.

The embedded distribution is a self-contained Python: a single directory
containing python.exe, python311.dll, the standard library zipped, and a
`._pth` file that controls sys.path. By default the `_pth` excludes
site-packages; we patch it to include site-packages so pip-installed wheels
work.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

PYTHON_VERSION = "3.11.9"


def embed_zip_url(version: str = PYTHON_VERSION) -> str:
    """Return the official python.org download URL for the embedded amd64 ZIP."""
    return (
        f"https://www.python.org/ftp/python/{version}/"
        f"python-{version}-embed-amd64.zip"
    )


def patch_pth_to_enable_site(pth_path: Path) -> None:
    """Uncomment the `#import site` line in the embedded `_pth` file.

    Without this, `Lib/site-packages` is not on sys.path and pip-installed
    wheels are invisible. With it, the embedded interpreter behaves like a
    normal install for our purposes.
    """
    text = pth_path.read_text()
    text = text.replace("#import site", "import site")
    pth_path.write_text(text)


def fetch_and_extract(
    target_dir: Path,
    version: str = PYTHON_VERSION,
) -> Path:
    """Download + extract the embedded Python distribution into `target_dir`.

    Patches the `_pth` file before returning. Returns `target_dir`.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    url = embed_zip_url(version)
    with urllib.request.urlopen(url, timeout=120) as response:
        zip_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(target_dir)

    # Find and patch the _pth file (name varies by minor version: python311._pth,
    # python312._pth, etc.)
    for pth in target_dir.glob("python*._pth"):
        patch_pth_to_enable_site(pth)

    return target_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download Python embedded distribution.")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--version", type=str, default=PYTHON_VERSION)
    args = parser.parse_args()
    result = fetch_and_extract(target_dir=args.target, version=args.version)
    print(f"Python {args.version} embedded extracted to {result}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/build/test_fetch_python.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/build/fetch_python.py tests/build/test_fetch_python.py
git commit -m "feat(build): download + extract Python 3.11 embedded distribution"
```

---

## Task 3: `install_deps.py` — cross-arch wheel install

**Files:**
- Create: `installer/build/install_deps.py`

(No unit tests — this module shells out to `pip` and the only meaningful verification is "did pip succeed?", which the orchestrator checks at runtime.)

- [ ] **Step 1: Implement `install_deps.py`**

Create `installer/build/install_deps.py`:

```python
"""Cross-install Windows wheels for `requirements.txt` into the embedded
Python's `Lib/site-packages`.

Pip's `--platform win_amd64 --python-version 311 --only-binary=:all:` flags
let us download Windows wheels from any host (Linux or Windows). We then
install them with `--target` to land them inside the embed dist's
site-packages.

Limitations:
- All deps in requirements.txt MUST have a cp311-win_amd64 wheel on PyPI.
  Plan A/B/C verified this for our 7 deps. New deps must be checked.
- Pure-Python deps without published wheels will fail. If that happens,
  switch to `pip download` + manual wheel building (out of scope here).
"""
import subprocess
import sys
from pathlib import Path


def install_windows_wheels(
    requirements_file: Path,
    target_site_packages: Path,
    python_version: str = "311",
    pip_executable: str = sys.executable,
) -> None:
    """Install wheels into target_site_packages for Windows amd64.

    Uses the host's pip (cross-arch) — works equally well on Linux and Windows
    since we explicitly pin the platform.

    Raises subprocess.CalledProcessError if pip exits non-zero.
    """
    target_site_packages.mkdir(parents=True, exist_ok=True)

    cmd = [
        pip_executable,
        "-m", "pip",
        "install",
        "--target", str(target_site_packages),
        "--platform", "win_amd64",
        "--python-version", python_version,
        "--only-binary=:all:",
        "--upgrade",
        "-r", str(requirements_file),
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cross-install Windows wheels.")
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True,
                        help="Path to <embed>/Lib/site-packages")
    parser.add_argument("--python-version", default="311")
    args = parser.parse_args()
    install_windows_wheels(
        requirements_file=args.requirements,
        target_site_packages=args.target,
        python_version=args.python_version,
    )
    print(f"Wheels installed to {args.target}")
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
source .venv/bin/activate
python -c "from installer.build.install_deps import install_windows_wheels; print('OK')"
```

Expected: `OK`.

- [ ] **Step 3: Verify the CLI usage prints correctly**

```bash
python -m installer.build.install_deps --help 2>&1 | head -5
```

Expected: argparse help output mentioning `--requirements`, `--target`, `--python-version`.

- [ ] **Step 4: Commit**

```bash
git add installer/build/install_deps.py
git commit -m "feat(build): cross-arch pip install for Windows wheels"
```

---

## Task 4: `stage.py` — copy source files into staging tree

**Files:**
- Create: `installer/build/stage.py`
- Create: `tests/build/test_stage.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/build/test_stage.py`:

```python
"""Tests for installer.build.stage."""
from pathlib import Path
import pytest

from installer.build.stage import (
    copy_source_to_staging,
    write_launcher_bat,
    SOURCE_FILES,
    SOURCE_DIRS,
)


class TestCopySourceToStaging:
    def test_copies_top_level_source_files(self, fs):
        repo_root = Path("/repo")
        for f in SOURCE_FILES:
            fs.create_file(str(repo_root / f), contents=f"# {f}\n")
        for d in SOURCE_DIRS:
            fs.create_file(str(repo_root / d / "stub.py"), contents=f"# in {d}\n")

        staging = Path("/staging")
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        for f in SOURCE_FILES:
            assert (staging / f).read_text() == f"# {f}\n"
        for d in SOURCE_DIRS:
            assert (staging / d / "stub.py").read_text() == f"# in {d}\n"

    def test_skips_pycache_dirs(self, fs):
        repo_root = Path("/repo")
        fs.create_file(str(repo_root / "trigger.py"), contents="x")
        fs.create_file(str(repo_root / "knowledge" / "scales.py"), contents="x")
        fs.create_file(str(repo_root / "knowledge" / "__pycache__" / "scales.cpython-311.pyc"), contents="bin")

        staging = Path("/staging")
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert (staging / "knowledge" / "scales.py").exists()
        assert not (staging / "knowledge" / "__pycache__").exists()

    def test_skips_test_dirs(self, fs):
        repo_root = Path("/repo")
        fs.create_file(str(repo_root / "trigger.py"), contents="x")
        fs.create_file(str(repo_root / "installer" / "main.py"), contents="x")
        fs.create_file(str(repo_root / "tests" / "test_foo.py"), contents="x")

        staging = Path("/staging")
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert not (staging / "tests").exists()

    def test_creates_staging_dir(self, fs):
        repo_root = Path("/repo")
        fs.create_file(str(repo_root / "trigger.py"), contents="x")

        staging = Path("/does/not/exist/yet/staging")
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert staging.is_dir()


class TestWriteLauncherBat:
    def test_writes_bat_with_python_invocation(self, fs):
        staging = Path("/staging")
        fs.create_dir(str(staging))

        bat_path = write_launcher_bat(staging)

        assert bat_path == staging / "flmcp.bat"
        text = bat_path.read_text()
        assert "python-embed" in text
        assert "installer.main" in text
        assert "@echo off" in text
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/build/test_stage.py -v
```

Expected: ImportError on `installer.build.stage`.

- [ ] **Step 3: Implement `stage.py`**

Create `installer/build/stage.py`:

```python
"""Assemble the staging tree that Inno Setup will package.

The staging tree mirrors the layout the user will see post-install at
`C:\\Program Files\\FL MCP Studio\\`:

    staging/
        python-embed/        (filled by fetch_python.py + install_deps.py)
        installer/
            setup_engine/
            wizard/
            tray/
            assets/
            main.py
        knowledge/
        trigger.py
        device_test.py
        flmcp.bat            (launcher)

This module copies the source-tree pieces (everything except python-embed/,
which the build orchestrator stages separately) and writes the launcher .bat.
"""
import shutil
from pathlib import Path

# Files at the project root that ship in the install
SOURCE_FILES = [
    "trigger.py",
    "device_test.py",
]

# Directories that ship in the install. Excluded subdirs (__pycache__, tests)
# are filtered by `_should_skip`.
SOURCE_DIRS = [
    "knowledge",
    "installer",
]

# Directory + file patterns that should never end up in the bundle
_SKIP_DIR_NAMES = {"__pycache__", "tests", "build", ".cache", "staging", "dist", ".pytest_cache"}
_SKIP_FILE_SUFFIXES = {".pyc", ".pyo"}


def _should_skip(path: Path) -> bool:
    if path.is_dir() and path.name in _SKIP_DIR_NAMES:
        return True
    if path.is_file() and path.suffix in _SKIP_FILE_SUFFIXES:
        return True
    return False


def _copy_filtered(src: Path, dst: Path) -> None:
    """Recursively copy `src` to `dst`, skipping `_SKIP_DIR_NAMES` and
    `_SKIP_FILE_SUFFIXES`."""
    if _should_skip(src):
        return
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return
    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            _copy_filtered(child, dst / child.name)


def copy_source_to_staging(repo_root: Path, staging: Path) -> None:
    """Copy `SOURCE_FILES` + `SOURCE_DIRS` from `repo_root` into `staging`,
    filtering out caches, tests, and build artifacts."""
    staging.mkdir(parents=True, exist_ok=True)
    for f in SOURCE_FILES:
        src = repo_root / f
        dst = staging / f
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    for d in SOURCE_DIRS:
        src = repo_root / d
        dst = staging / d
        if src.exists():
            _copy_filtered(src, dst)


def write_launcher_bat(staging: Path) -> Path:
    """Write the `flmcp.bat` launcher into the staging dir. Returns its path."""
    bat = staging / "flmcp.bat"
    bat.write_text(
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "\"%~dp0python-embed\\python.exe\" -m installer.main\r\n"
    )
    return bat


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage source files for Inno Setup.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--staging", type=Path, required=True)
    args = parser.parse_args()
    copy_source_to_staging(repo_root=args.repo_root, staging=args.staging)
    write_launcher_bat(args.staging)
    print(f"Source staged to {args.staging}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/build/test_stage.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add installer/build/stage.py tests/build/test_stage.py
git commit -m "feat(build): stage source files + write flmcp.bat launcher"
```

---

## Task 5: `installer/setup.iss` — Inno Setup script

**Files:**
- Create: `installer/setup.iss`

- [ ] **Step 1: Create `setup.iss`**

```pascal
; FL MCP Studio — Inno Setup script
; Builds a single .exe installer that drops the staged tree into
; "Program Files\FL MCP Studio" and creates a Start Menu shortcut.
; The build orchestrator (build.sh) populates ./build/staging/ before
; calling iscc on this file.

#define MyAppName "FL MCP Studio"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "FL MCP"
#define MyAppExeName "flmcp.bat"

[Setup]
AppId={{8B4F8A2D-1234-4567-89AB-FL_MCP_STUDIO_01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=FL-MCP-Studio-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; The python-embed/ directory is staged by build.sh before iscc runs
Source: "build\staging\python-embed\*"; DestDir: "{app}\python-embed"; Flags: recursesubdirs createallsubdirs ignoreversion
; Project source files
Source: "build\staging\trigger.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\staging\device_test.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\staging\knowledge\*"; DestDir: "{app}\knowledge"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "build\staging\installer\*"; DestDir: "{app}\installer"; Flags: recursesubdirs createallsubdirs ignoreversion
; Launcher
Source: "build\staging\flmcp.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "Configurar FL MCP Studio"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar configuración ahora"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; Clean up runtime state. Do NOT delete user's claude_desktop_config.json — it
; was modified by us (with .bak) but is owned by Claude Desktop.
Type: filesandordirs; Name: "{userappdata}\FL MCP Studio"
Type: filesandordirs; Name: "{app}\python-embed\Lib\site-packages\__pycache__"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
```

- [ ] **Step 2: Verify the file is syntactically plausible**

```bash
python -c "
content = open('installer/setup.iss').read()
required_sections = ['[Setup]', '[Files]', '[Icons]', '[Run]', '[UninstallDelete]']
for s in required_sections:
    assert s in content, f'Missing section: {s}'
assert 'FL MCP Studio' in content
assert 'python-embed' in content
print('setup.iss OK,', len(content), 'bytes')
"
```

Expected: `setup.iss OK, NNNN bytes`.

- [ ] **Step 3: Commit**

```bash
git add installer/setup.iss
git commit -m "feat(build): Inno Setup script for the .exe installer"
```

---

## Task 6: `build.sh` — orchestrator with Wine support

**Files:**
- Create: `installer/build/build.sh`
- Make executable: `chmod +x`

- [ ] **Step 1: Create `build.sh`**

```bash
#!/usr/bin/env bash
# FL MCP Studio — build orchestrator
# Cross-builds the .exe installer from Linux+Wine or natively from Windows.
#
# Steps:
#   1. fetch_python.py  → download Python embedded
#   2. install_deps.py  → install Windows wheels
#   3. stage.py         → copy source files
#   4. iscc setup.iss   → compile installer
#   5. verify           → sanity-check the resulting .exe
#
# Required on PATH: python3, iscc.exe (native or via Wine).
# Set ISCC_PATH env var to override iscc detection.

set -euo pipefail

# ---- paths ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$INSTALLER_DIR")"
CACHE_DIR="$SCRIPT_DIR/.cache"
STAGING_DIR="$SCRIPT_DIR/staging"
DIST_DIR="$SCRIPT_DIR/dist"
EMBED_DIR="$STAGING_DIR/python-embed"
SITE_PACKAGES="$EMBED_DIR/Lib/site-packages"

# ---- python on host ----
PYTHON="${PYTHON:-python3}"

# ---- iscc detection ----
detect_iscc() {
    if [ -n "${ISCC_PATH:-}" ] && [ -e "$ISCC_PATH" ]; then
        echo "$ISCC_PATH"
        return
    fi
    # Native iscc on PATH (Windows / Cygwin)
    if command -v iscc >/dev/null 2>&1; then
        command -v iscc
        return
    fi
    # Wine default install path on Linux
    local wine_iscc="$HOME/.wine/drive_c/Program Files (x86)/Inno Setup 6/iscc.exe"
    if [ -e "$wine_iscc" ]; then
        echo "$wine_iscc"
        return
    fi
    echo ""
}

run_iscc() {
    local iscc="$1"
    local script="$2"
    if [[ "$iscc" == *.exe ]] && [ "$(uname)" != "MINGW"* ] && [ "$(uname)" != "CYGWIN"* ]; then
        # Linux/macOS: run via Wine
        wine "$iscc" "$script"
    else
        "$iscc" "$script"
    fi
}

# ---- main ----
echo "=== FL MCP Studio build ==="
echo "Repo root:     $REPO_ROOT"
echo "Cache:         $CACHE_DIR"
echo "Staging:       $STAGING_DIR"
echo "Dist:          $DIST_DIR"
echo

# Clean staging from previous runs
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR" "$DIST_DIR" "$CACHE_DIR"

echo "[1/5] Fetching Python embedded distribution..."
"$PYTHON" -m installer.build.fetch_python --target "$EMBED_DIR"

echo "[2/5] Installing Windows wheels..."
"$PYTHON" -m installer.build.install_deps \
    --requirements "$REPO_ROOT/requirements.txt" \
    --target "$SITE_PACKAGES"

echo "[3/5] Staging source files..."
"$PYTHON" -m installer.build.stage \
    --repo-root "$REPO_ROOT" \
    --staging "$STAGING_DIR"

echo "[4/5] Compiling installer with Inno Setup..."
ISCC=$(detect_iscc)
if [ -z "$ISCC" ]; then
    echo "ERROR: iscc.exe not found." >&2
    echo "       Install Inno Setup (Windows) or Inno Setup under Wine (Linux)." >&2
    echo "       See installer/BUILD.md for instructions." >&2
    exit 1
fi
echo "       Using iscc: $ISCC"
cd "$INSTALLER_DIR"
run_iscc "$ISCC" "setup.iss"

echo "[5/5] Verifying output..."
EXPECTED_EXE="$INSTALLER_DIR/dist/FL-MCP-Studio-Setup-v0.1.0.exe"
if [ ! -f "$EXPECTED_EXE" ]; then
    echo "ERROR: expected $EXPECTED_EXE not found after iscc compile." >&2
    exit 1
fi

# Move to the build dir's dist/ for consistency with .gitignore
mv "$EXPECTED_EXE" "$DIST_DIR/"
FINAL_EXE="$DIST_DIR/FL-MCP-Studio-Setup-v0.1.0.exe"

SIZE_MB=$(du -m "$FINAL_EXE" | cut -f1)
echo
echo "=== Build complete ==="
echo "Output: $FINAL_EXE"
echo "Size:   ${SIZE_MB} MB"
echo

if [ "$SIZE_MB" -lt 10 ]; then
    echo "WARNING: .exe is unusually small (${SIZE_MB} MB)." >&2
    echo "         Expected ~50-80 MB. The bundle may be missing files." >&2
    exit 1
fi
```

- [ ] **Step 2: Make `build.sh` executable**

```bash
chmod +x installer/build/build.sh
```

- [ ] **Step 3: Verify the script parses (no syntax errors)**

```bash
bash -n installer/build/build.sh && echo "build.sh syntax OK"
```

Expected: `build.sh syntax OK`.

- [ ] **Step 4: Commit**

```bash
git add installer/build/build.sh
git commit -m "feat(build): build.sh orchestrator with Wine fallback for iscc"
```

---

## Task 7: Documentation update

**Files:**
- Modify: `CLAUDE.md`
- Modify: `installer/BUILD.md` (replace skeleton with full content)

- [ ] **Step 1: Update `CLAUDE.md`**

Use the Edit tool. Find the existing "Sistema de Instalación (Windows)" section and append the following at its end (right before the closing `---`):

```markdown
### `installer/build/` — Build pipeline

| Archivo | Responsabilidad |
|---|---|
| `fetch_python.py` | Descarga Python 3.11 embedded de python.org, parchea `_pth` para habilitar site-packages |
| `install_deps.py` | `pip install --platform win_amd64 --only-binary=:all:` — wheels Windows desde Linux dev |
| `stage.py` | Copia trigger.py, device_test.py, knowledge/, installer/ a `build/staging/`. Filtra `__pycache__`, `tests/`, `.pyc`. Escribe `flmcp.bat` |
| `setup.iss` | Inno Setup script: metadata, [Files], [Icons], [Run], [UninstallDelete] |
| `build.sh` | Orquestador: fetch → install_deps → stage → iscc (via Wine en Linux). Output: `installer/build/dist/FL-MCP-Studio-Setup-vX.Y.Z.exe` |

Build local desde Linux: `cd installer/build && ./build.sh` (requiere Wine + Inno Setup 6 instalado bajo Wine — ver `installer/BUILD.md`).

**No usamos PyInstaller** (deviation del spec original). Embedded Python directo es más liviano, más AV-friendly, y mantiene las paths que `wizard.js` hardcodea.
```

- [ ] **Step 2: Replace `installer/BUILD.md` with the full version**

Replace the entire file content with:

```markdown
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
```

- [ ] **Step 3: Run the full test suite**

```bash
source .venv/bin/activate
pytest
```

Expected: 91 (from A+B+C) + 5 (fetch_python) + 5 (stage) = **101 tests PASS**.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md installer/BUILD.md
git commit -m "docs(build): document build pipeline in CLAUDE.md + BUILD.md"
```

---

## Done — what you should have at the end

- 6 files in `installer/build/`: `__init__.py`, `fetch_python.py`, `install_deps.py`, `stage.py`, `build.sh`, plus the test counterparts in `tests/build/`
- 1 Inno Setup script: `installer/setup.iss`
- 1 launcher: `installer/flmcp.bat` (written by stage.py at build time, NOT committed — staging output)
- 1 build doc: `installer/BUILD.md`
- 10 unit tests added (5 fetch_python + 5 stage; install_deps and build.sh are integration-only)
- 7 atomic commits

## Verification checklist before declaring done

- [ ] `pytest` reports 101 PASS, 0 FAIL
- [ ] `python -c "from installer.build.fetch_python import fetch_and_extract; print('OK')"` succeeds
- [ ] `python -c "from installer.build.install_deps import install_windows_wheels; print('OK')"` succeeds
- [ ] `python -c "from installer.build.stage import copy_source_to_staging; print('OK')"` succeeds
- [ ] `bash -n installer/build/build.sh` exits 0 (syntax check)
- [ ] `installer/setup.iss` contains all 5 required sections
- [ ] `installer/BUILD.md` is comprehensive (>2000 chars) covering Linux+Wine and native Windows paths
- [ ] `git log --oneline | head -7` shows 7 atomic commits with conventional-commit format

## Verification checklist for a real build (after merge — out of plan scope)

- [ ] `cd installer/build && ./build.sh` produces `dist/FL-MCP-Studio-Setup-v0.1.0.exe`
- [ ] The `.exe` is between 30 MB and 100 MB
- [ ] `7z l installer/build/dist/FL-MCP-Studio-Setup-v0.1.0.exe | head -50` shows expected files (python.exe, trigger.py, installer/main.py, etc.)
- [ ] On a Windows VM, the `.exe` installs without error, the wizard launches, and the QA_CHECKLIST.md flow passes

## Out of scope (future sub-projects)

- GitHub Actions release pipeline (`.github/workflows/release.yml`) — deferred per user request; build.sh is the local-build path that CI would call once added.
- Code signing — Sectigo cert ~$80/year. SmartScreen will show "Editor desconocido" on first run; users click "Run anyway".
- Auto-update implementation — the tray menu has the entry but it currently only shows a placeholder notification. A real implementation would check GitHub Releases API.
- Branded icons — `installer/assets/icon_*.png` are colored placeholder dots. A real designer should produce branded versions.
