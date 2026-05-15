"""High-level indexer API: build, search, stats."""
from __future__ import annotations
import time
from pathlib import Path
from typing import Callable

from indexer.walker import walk_audio_files
from indexer.parser import parse_path
from indexer.fileinfo import compute_content_hash, stat_file
from indexer.storage import save_manifest, load_manifest

__all__ = ["build_manifest", "search_samples", "library_stats"]


def build_manifest(
    packs_root: Path | str,
    manifest_path: Path | str,
    on_progress: Callable[[int, int], None] | None = None,
) -> dict:
    """Walk the packs root and build/update the manifest incrementally.

    Returns stats dict: {added, updated, unchanged, removed, total}.
    """
    packs_root = Path(packs_root)
    manifest_path = Path(manifest_path)

    existing = load_manifest(manifest_path)
    existing_by_path: dict[str, dict] = {r["path"]: r for r in existing}

    new_rows: list[dict] = []
    seen_paths: set[str] = set()
    added = 0
    updated = 0
    unchanged = 0

    all_files = list(walk_audio_files(packs_root))
    total_files = len(all_files)

    for idx, file_path in enumerate(all_files):
        path_str = str(file_path)
        seen_paths.add(path_str)
        try:
            stat = stat_file(file_path)
        except OSError:
            continue

        prior = existing_by_path.get(path_str)
        if prior is not None and prior.get("mtime") == stat["mtime"] and prior.get("size_bytes") == stat["size_bytes"]:
            new_rows.append(prior)
            unchanged += 1
        else:
            try:
                content_hash = compute_content_hash(file_path)
            except OSError:
                continue

            tags = parse_path(path_str, str(packs_root))
            row = {
                "path": path_str,
                "filename": file_path.name,
                "relative_folder": tags["relative_folder"],
                "extension": file_path.suffix.lower(),
                "size_bytes": stat["size_bytes"],
                "mtime": stat["mtime"],
                "content_hash": content_hash,
                "sample_type": tags["sample_type"],
                "subtype": tags["subtype"],
                "genres": tags["genres"],
                "moods": tags["moods"],
                "key": tags["key"],
                "bpm": tags["bpm"],
                "is_loop": tags["is_loop"],
                "is_oneshot": tags["is_oneshot"],
                "raw_tags": tags["raw_tags"],
                "indexed_at": int(time.time()),
            }
            new_rows.append(row)
            if prior is None:
                added += 1
            else:
                updated += 1

        if on_progress is not None and (idx + 1) % 200 == 0:
            on_progress(idx + 1, total_files)

    if on_progress is not None:
        on_progress(total_files, total_files)

    removed = sum(1 for path in existing_by_path if path not in seen_paths)

    save_manifest(manifest_path, new_rows)

    return {
        "added": added,
        "updated": updated,
        "unchanged": unchanged,
        "removed": removed,
        "total": len(new_rows),
    }


def search_samples(
    manifest_path: Path | str,
    sample_type: str | None = None,
    subtype: str | None = None,
    genre: str | None = None,
    mood: str | None = None,
    key: str | None = None,
    bpm: int | None = None,
    bpm_tolerance: int = 5,
    is_loop: bool | None = None,
    is_oneshot: bool | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search the manifest with AND-combined filters."""
    rows = load_manifest(manifest_path)
    results: list[dict] = []
    for row in rows:
        if sample_type is not None and row["sample_type"] != sample_type:
            continue
        if subtype is not None and row["subtype"] != subtype:
            continue
        if genre is not None and genre not in (row["genres"] or []):
            continue
        if mood is not None and mood not in (row["moods"] or []):
            continue
        if key is not None and row["key"] != key:
            continue
        if bpm is not None:
            row_bpm = row["bpm"]
            if row_bpm is None or abs(row_bpm - bpm) > bpm_tolerance:
                continue
        if is_loop is not None and row["is_loop"] != is_loop:
            continue
        if is_oneshot is not None and row["is_oneshot"] != is_oneshot:
            continue
        results.append(row)
        if len(results) >= limit:
            break
    return results


def library_stats(manifest_path: Path | str) -> dict:
    """Compute aggregate statistics over the manifest."""
    rows = load_manifest(manifest_path)
    by_type: dict[str, int] = {}
    by_genre: dict[str, int] = {}
    untyped = 0
    with_bpm = 0
    with_key = 0
    for row in rows:
        t = row["sample_type"]
        if t is None:
            untyped += 1
        else:
            by_type[t] = by_type.get(t, 0) + 1
        for g in (row["genres"] or []):
            by_genre[g] = by_genre.get(g, 0) + 1
        if row["bpm"] is not None:
            with_bpm += 1
        if row["key"] is not None:
            with_key += 1

    return {
        "total": len(rows),
        "by_type": by_type,
        "by_genre": by_genre,
        "untyped": untyped,
        "with_bpm": with_bpm,
        "with_key": with_key,
    }
