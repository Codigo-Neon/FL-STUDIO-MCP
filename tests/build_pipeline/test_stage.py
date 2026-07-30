"""Tests for installer.build.stage."""
from pathlib import Path
import pytest

from installer.build.stage import (
    copy_source_to_staging,
    write_launcher_bat,
    SOURCE_FILES,
    SOURCE_DIRS,
)


def test_source_dirs_covers_every_package_trigger_imports():
    """trigger.py imports bridge/ and indexer/ at module level. If they are not
    staged, the shipped MCP server dies on startup with ImportError and the
    wizard cannot copy bridge/ into FL Studio. Guard against silent regression.
    """
    for required in ("knowledge", "bridge", "indexer", "installer"):
        assert required in SOURCE_DIRS, f"{required}/ must ship in the installer bundle"


class TestCopySourceToStaging:
    def test_copies_top_level_source_files(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        for f in SOURCE_FILES:
            file_path = repo_root / f
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"# {f}\n")
        for d in SOURCE_DIRS:
            stub = repo_root / d / "stub.py"
            stub.parent.mkdir(parents=True, exist_ok=True)
            stub.write_text(f"# in {d}\n")

        staging = tmp_path / "staging"
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        for f in SOURCE_FILES:
            assert (staging / f).read_text() == f"# {f}\n"
        for d in SOURCE_DIRS:
            assert (staging / d / "stub.py").read_text() == f"# in {d}\n"

    def test_skips_pycache_dirs(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "trigger.py").write_text("x")
        knowledge = repo_root / "knowledge"
        knowledge.mkdir()
        (knowledge / "scales.py").write_text("x")
        pycache = knowledge / "__pycache__"
        pycache.mkdir()
        (pycache / "scales.cpython-311.pyc").write_text("bin")

        staging = tmp_path / "staging"
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert (staging / "knowledge" / "scales.py").exists()
        assert not (staging / "knowledge" / "__pycache__").exists()

    def test_skips_test_dirs(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "trigger.py").write_text("x")
        installer_dir = repo_root / "installer"
        installer_dir.mkdir()
        (installer_dir / "main.py").write_text("x")
        tests_dir = repo_root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_foo.py").write_text("x")

        staging = tmp_path / "staging"
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert not (staging / "tests").exists()

    def test_creates_staging_dir(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "trigger.py").write_text("x")

        staging = tmp_path / "does/not/exist/yet/staging"
        copy_source_to_staging(repo_root=repo_root, staging=staging)

        assert staging.is_dir()


class TestWriteLauncherBat:
    def test_writes_bat_with_python_invocation(self, tmp_path):
        staging = tmp_path / "staging"
        staging.mkdir()

        bat_path = write_launcher_bat(staging)

        assert bat_path == staging / "flmcp.bat"
        text = bat_path.read_text()
        assert "python-embed" in text
        assert "installer.main" in text
        assert "@echo off" in text
