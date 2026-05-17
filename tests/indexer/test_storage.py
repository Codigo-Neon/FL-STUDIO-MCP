import pytest
from indexer.storage import (
    MANIFEST_SCHEMA,
    save_manifest,
    load_manifest,
    empty_manifest,
)


def make_row(**overrides):
    base = {
        "path": "/packs/kick.wav",
        "filename": "kick.wav",
        "relative_folder": "",
        "extension": ".wav",
        "size_bytes": 1000,
        "mtime": 1700000000,
        "content_hash": "abc123",
        "sample_type": "kick",
        "subtype": None,
        "genres": ["trap"],
        "moods": ["punchy"],
        "key": None,
        "bpm": None,
        "is_loop": False,
        "is_oneshot": True,
        "raw_tags": ["kick", "trap", "punchy"],
        "indexed_at": 1700000100,
    }
    base.update(overrides)
    return base


class TestManifestRoundTrip:
    def test_save_and_load_single_row(self, tmp_path):
        path = tmp_path / "m.parquet"
        rows = [make_row()]
        save_manifest(path, rows)
        loaded = load_manifest(path)
        assert len(loaded) == 1
        assert loaded[0]["sample_type"] == "kick"
        assert loaded[0]["genres"] == ["trap"]

    def test_save_and_load_many_rows(self, tmp_path):
        path = tmp_path / "m.parquet"
        rows = [make_row(path=f"/packs/{i}.wav", content_hash=str(i)) for i in range(100)]
        save_manifest(path, rows)
        loaded = load_manifest(path)
        assert len(loaded) == 100

    def test_load_missing_file_returns_empty(self, tmp_path):
        path = tmp_path / "missing.parquet"
        loaded = load_manifest(path)
        assert loaded == []

    def test_save_creates_parent_dir(self, tmp_path):
        path = tmp_path / "deeply" / "nested" / "m.parquet"
        save_manifest(path, [make_row()])
        assert path.exists()

    def test_preserves_none_values(self, tmp_path):
        path = tmp_path / "m.parquet"
        rows = [make_row(sample_type=None, subtype=None, key=None, bpm=None)]
        save_manifest(path, rows)
        loaded = load_manifest(path)
        assert loaded[0]["sample_type"] is None
        assert loaded[0]["bpm"] is None

    def test_preserves_empty_lists(self, tmp_path):
        path = tmp_path / "m.parquet"
        rows = [make_row(genres=[], moods=[], raw_tags=[])]
        save_manifest(path, rows)
        loaded = load_manifest(path)
        assert loaded[0]["genres"] == []
        assert loaded[0]["moods"] == []


class TestEmptyManifest:
    def test_empty_manifest_is_list(self):
        assert empty_manifest() == []
