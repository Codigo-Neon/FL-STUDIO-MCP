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

# ---- version ----
# setup.iss is the single source of truth: it defines MyAppVersion and derives
# OutputBaseFilename from it. Parse it here instead of duplicating the literal,
# so bumping the version means editing exactly one line.
VERSION="$(sed -n 's/^#define MyAppVersion "\(.*\)"$/\1/p' "$INSTALLER_DIR/setup.iss")"
if [ -z "$VERSION" ]; then
    echo "ERROR: could not parse MyAppVersion from $INSTALLER_DIR/setup.iss" >&2
    exit 1
fi
EXE_NAME="FL-MCP-Studio-Setup-v${VERSION}.exe"

# Make `python -m installer.build.<module>` work regardless of CWD: prepend
# the repo root to PYTHONPATH so the `installer` package is importable.
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

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
    # Wine default install path on Linux. Inno Setup 6.x ships ISCC.exe
    # (uppercase). Linux filesystems are case-sensitive so we check both.
    local wine_dir="$HOME/.wine/drive_c/Program Files (x86)/Inno Setup 6"
    for candidate in "$wine_dir/ISCC.exe" "$wine_dir/iscc.exe"; do
        if [ -e "$candidate" ]; then
            echo "$candidate"
            return
        fi
    done
    echo ""
}

run_iscc() {
    local iscc="$1"
    local script="$2"
    if [[ "$iscc" == *.exe ]] && [[ "$(uname)" != MINGW* ]] && [[ "$(uname)" != CYGWIN* ]]; then
        # Linux/macOS: run via Wine
        wine "$iscc" "$script"
    else
        "$iscc" "$script"
    fi
}

# ---- main ----
echo "=== FL MCP Studio build ==="
echo "Version:       $VERSION"
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
EXPECTED_EXE="$INSTALLER_DIR/dist/$EXE_NAME"
if [ ! -f "$EXPECTED_EXE" ]; then
    echo "ERROR: expected $EXPECTED_EXE not found after iscc compile." >&2
    exit 1
fi

# Move to the build dir's dist/ for consistency with .gitignore
mv "$EXPECTED_EXE" "$DIST_DIR/"
FINAL_EXE="$DIST_DIR/$EXE_NAME"

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
