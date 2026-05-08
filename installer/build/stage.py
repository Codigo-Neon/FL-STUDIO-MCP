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
