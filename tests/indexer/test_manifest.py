import time
import pytest
from indexer.manifest import build_manifest, search_samples, library_stats


def make_wav(path, content=b"RIFF\x00\x00\x00\x00WAVE"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content + b"\x00" * 100)


class TestBuildManifest:
    def test_first_run_indexes_all(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "kicks" / "Kick_BoomBap_01.wav")
        make_wav(packs / "snares" / "Snare_Punchy.wav")
        manifest = tmp_path / "manifest.parquet"

        stats = build_manifest(packs, manifest)

        assert stats["added"] == 2
        assert stats["unchanged"] == 0
        assert stats["total"] == 2

    def test_second_run_no_changes_all_unchanged(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "kick.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        stats = build_manifest(packs, manifest)
        assert stats["added"] == 0
        assert stats["unchanged"] == 1

    def test_modified_file_is_updated(self, tmp_path):
        packs = tmp_path / "Packs"
        sample = packs / "kick.wav"
        make_wav(sample, content=b"RIFFold")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        time.sleep(0.01)
        make_wav(sample, content=b"RIFFNEWcontent")
        stats = build_manifest(packs, manifest)
        assert stats["updated"] == 1

    def test_removed_file_is_dropped(self, tmp_path):
        packs = tmp_path / "Packs"
        a = packs / "a.wav"
        b = packs / "b.wav"
        make_wav(a)
        make_wav(b)
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        b.unlink()
        stats = build_manifest(packs, manifest)
        assert stats["removed"] == 1
        assert stats["total"] == 1

    def test_progress_callback(self, tmp_path):
        packs = tmp_path / "Packs"
        for i in range(5):
            make_wav(packs / f"kick_{i}.wav")
        manifest = tmp_path / "manifest.parquet"

        seen = []
        build_manifest(packs, manifest, on_progress=lambda done, total: seen.append((done, total)))
        # Should report at least the final state
        assert any(d == 5 for d, t in seen)


class TestSearchSamples:
    def test_search_by_type(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "Kick_01.wav")
        make_wav(packs / "Snare_01.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, sample_type="kick")
        assert len(results) == 1
        assert results[0]["filename"] == "Kick_01.wav"

    def test_search_by_genre(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "Kick_Trap_01.wav")
        make_wav(packs / "Kick_BoomBap_01.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, genre="trap")
        assert len(results) == 1
        assert "Trap" in results[0]["filename"]

    def test_search_by_bpm_with_tolerance(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "Loop_140bpm.wav")
        make_wav(packs / "Loop_90bpm.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, bpm=142, bpm_tolerance=5)
        assert len(results) == 1
        assert results[0]["bpm"] == 140

    def test_search_combines_filters_with_and(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "Kick_Trap_Punchy.wav")
        make_wav(packs / "Kick_Trap_Soft.wav")
        make_wav(packs / "Snare_Trap_Punchy.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, sample_type="kick", genre="trap", mood="punchy")
        assert len(results) == 1
        assert results[0]["filename"] == "Kick_Trap_Punchy.wav"

    def test_search_respects_limit(self, tmp_path):
        packs = tmp_path / "Packs"
        for i in range(50):
            make_wav(packs / f"Kick_{i:03d}.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, sample_type="kick", limit=10)
        assert len(results) == 10

    def test_search_with_no_filters_returns_all(self, tmp_path):
        packs = tmp_path / "Packs"
        for i in range(3):
            make_wav(packs / f"sample_{i}.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        results = search_samples(manifest, limit=100)
        assert len(results) == 3


class TestLibraryStats:
    def test_stats_counts_by_type(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "Kick_01.wav")
        make_wav(packs / "Kick_02.wav")
        make_wav(packs / "Snare_01.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        stats = library_stats(manifest)
        assert stats["total"] == 3
        assert stats["by_type"]["kick"] == 2
        assert stats["by_type"]["snare"] == 1

    def test_stats_includes_unknown_count(self, tmp_path):
        packs = tmp_path / "Packs"
        make_wav(packs / "xyzqqq.wav")
        manifest = tmp_path / "manifest.parquet"
        build_manifest(packs, manifest)

        stats = library_stats(manifest)
        assert stats["untyped"] == 1
