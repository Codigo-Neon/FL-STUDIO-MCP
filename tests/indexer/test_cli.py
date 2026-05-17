"""Tests for the indexer CLI."""
import subprocess
import sys


def _make_packs(tmp_path):
    packs = tmp_path / "Packs"
    (packs / "kicks").mkdir(parents=True)
    (packs / "kicks" / "Kick_Trap_01.wav").write_bytes(b"RIFF" + b"\x00" * 100)
    (packs / "kicks" / "Kick_BoomBap_01.wav").write_bytes(b"RIFF" + b"\x00" * 100)
    return packs


class TestCliIndex:
    def test_index_subcommand_runs(self, tmp_path):
        packs = _make_packs(tmp_path)
        manifest = tmp_path / "manifest.parquet"

        result = subprocess.run(
            [sys.executable, "-m", "indexer", "index",
             "--packs", str(packs), "--manifest", str(manifest)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert manifest.exists()
        assert "added" in result.stdout.lower()

    def test_stats_subcommand_runs(self, tmp_path):
        packs = _make_packs(tmp_path)
        manifest = tmp_path / "manifest.parquet"
        setup = subprocess.run(
            [sys.executable, "-m", "indexer", "index",
             "--packs", str(packs), "--manifest", str(manifest)],
            capture_output=True, text=True,
        )
        assert setup.returncode == 0, f"index setup failed:\n{setup.stderr}"

        result = subprocess.run(
            [sys.executable, "-m", "indexer", "stats",
             "--manifest", str(manifest)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "total" in result.stdout.lower()


class TestCliSearch:
    def test_search_filters_by_type(self, tmp_path):
        packs = _make_packs(tmp_path)
        manifest = tmp_path / "manifest.parquet"
        setup = subprocess.run(
            [sys.executable, "-m", "indexer", "index",
             "--packs", str(packs), "--manifest", str(manifest)],
            capture_output=True, text=True,
        )
        assert setup.returncode == 0, f"index setup failed:\n{setup.stderr}"

        result = subprocess.run(
            [sys.executable, "-m", "indexer", "search",
             "--manifest", str(manifest),
             "--type", "kick", "--genre", "trap"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "Kick_Trap_01.wav" in result.stdout
        assert "Kick_BoomBap_01.wav" not in result.stdout

    def test_loops_and_oneshots_mutually_exclusive(self, tmp_path):
        packs = _make_packs(tmp_path)
        manifest = tmp_path / "manifest.parquet"
        setup = subprocess.run(
            [sys.executable, "-m", "indexer", "index",
             "--packs", str(packs), "--manifest", str(manifest)],
            capture_output=True, text=True,
        )
        assert setup.returncode == 0, setup.stderr

        result = subprocess.run(
            [sys.executable, "-m", "indexer", "search",
             "--manifest", str(manifest),
             "--loops-only", "--oneshots-only"],
            capture_output=True, text=True,
        )
        # argparse exits with code 2 on argument errors
        assert result.returncode != 0
        assert "not allowed with" in result.stderr.lower() or "argument" in result.stderr.lower()
