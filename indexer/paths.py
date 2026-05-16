"""Default filesystem locations for packs root and manifest cache."""
import os
import sys
from pathlib import Path

__all__ = ["default_packs_root", "default_manifest_path"]


def default_packs_root() -> Path:
    env = os.environ.get("FL_MCP_PACKS_ROOT")
    if env:
        return Path(env)
    home = Path(os.environ.get("HOME", str(Path.home())))
    if sys.platform == "linux":
        return home / ".flstudio_prefix" / "drive_c" / "Program Files" / "Image-Line" / "FL Studio 2024" / "Data" / "Patches" / "Packs"
    # Windows: samples live in Documents/Image-Line/FL Studio/Sample Pack/Packs.
    return home / "Documents" / "Image-Line" / "FL Studio" / "Sample Pack" / "Packs"


def default_manifest_path() -> Path:
    env = os.environ.get("FL_MCP_MANIFEST_PATH")
    if env:
        return Path(env)
    home = Path(os.environ.get("HOME", str(Path.home())))
    return home / ".fl_mcp" / "library_index" / "manifest.parquet"
