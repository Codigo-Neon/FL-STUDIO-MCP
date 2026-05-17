"""File stat and content hashing for incremental indexing."""
import hashlib
from pathlib import Path

__all__ = ["compute_content_hash", "stat_file"]

_HASH_PREFIX_BYTES = 64 * 1024  # 64 KB


def compute_content_hash(path: Path) -> str:
    """sha1(filename + first 64KB).

    Filename is included so two byte-identical samples with different names
    don't collide in the manifest. 64KB is enough to detect content changes
    in practice without paying the cost of hashing whole large WAVs.
    """
    h = hashlib.sha1()
    h.update(path.name.encode("utf-8"))
    with open(path, "rb") as f:
        h.update(f.read(_HASH_PREFIX_BYTES))
    return h.hexdigest()


def stat_file(path: Path) -> dict:
    s = path.stat()
    return {
        "size_bytes": s.st_size,
        "mtime": int(s.st_mtime),
    }
