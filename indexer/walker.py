"""Filesystem walker for sample libraries.

Yields `pathlib.Path` objects for audio files under a root. Skips:
  - Hidden directories (those whose names start with .)
  - Files with non-audio extensions
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterator

from indexer.keywords import AUDIO_EXTENSIONS

__all__ = ["walk_audio_files"]


def walk_audio_files(root: Path | str) -> Iterator[Path]:
    """Yield Path to every audio file under `root`, recursively.

    Raises FileNotFoundError if root doesn't exist.
    """
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"sample library root does not exist: {root}")

    audio_exts = {e.lower() for e in AUDIO_EXTENSIONS}

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip hidden directories in place — modifying dirnames prunes os.walk
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fname in filenames:
            if Path(fname).suffix.lower() in audio_exts:
                yield Path(dirpath) / fname
