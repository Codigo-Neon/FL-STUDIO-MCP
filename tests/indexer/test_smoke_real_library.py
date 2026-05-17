"""Smoke test against the user's real FL Studio sample library.

Marked `slow` — opt-in via `pytest -m slow`. Skipped if the default library
path does not exist (e.g. on CI).
"""
import os
import time
import pytest
from pathlib import Path
from indexer.paths import default_packs_root, default_manifest_path
from indexer.manifest import build_manifest, library_stats


pytestmark = pytest.mark.slow


def _real_packs_or_skip():
    root = default_packs_root()
    if not root.exists():
        pytest.skip(f"real packs root not found: {root}")
    return root


def test_indexing_completes_in_reasonable_time(tmp_path):
    packs = _real_packs_or_skip()
    manifest = tmp_path / "real.parquet"

    t0 = time.monotonic()
    stats = build_manifest(packs, manifest)
    elapsed = time.monotonic() - t0

    print(f"\nIndexed {stats['total']} samples in {elapsed:.1f}s")
    print(f"  added: {stats['added']}, updated: {stats['updated']}")
    # Reasonable upper bound: 1ms per sample on filename-only Capa 1
    # 40k samples × 1ms = 40s. Set generous threshold.
    assert elapsed < max(10, stats["total"] * 0.005)


def test_coverage_above_50_percent(tmp_path):
    """Most samples should get a recognized sample_type."""
    packs = _real_packs_or_skip()
    manifest = tmp_path / "real.parquet"

    build_manifest(packs, manifest)
    stats = library_stats(manifest)
    if stats["total"] == 0:
        pytest.skip("empty library")
    typed_fraction = (stats["total"] - stats["untyped"]) / stats["total"]
    print(f"\nTyped coverage: {typed_fraction*100:.1f}%")
    print(f"By type: {dict(sorted(stats['by_type'].items(), key=lambda kv: -kv[1])[:10])}")
    assert typed_fraction >= 0.5
