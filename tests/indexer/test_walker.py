"""Tests for the filesystem walker."""
import pytest
from indexer.walker import walk_audio_files


class TestWalker:
    def test_finds_wav_files(self, tmp_path):
        (tmp_path / "kick.wav").write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
        (tmp_path / "snare.wav").write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 2
        names = sorted(r.name for r in results)
        assert names == ["kick.wav", "snare.wav"]

    def test_recurses_subdirs(self, tmp_path):
        (tmp_path / "pack1").mkdir()
        (tmp_path / "pack1" / "kick.wav").write_bytes(b"x")
        (tmp_path / "pack1" / "sub").mkdir()
        (tmp_path / "pack1" / "sub" / "snare.wav").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 2

    def test_skips_non_audio(self, tmp_path):
        (tmp_path / "kick.wav").write_bytes(b"x")
        (tmp_path / "preset.fst").write_bytes(b"x")
        (tmp_path / "readme.txt").write_text("hi")
        (tmp_path / "art.png").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 1
        assert results[0].name == "kick.wav"

    def test_accepts_all_audio_extensions(self, tmp_path):
        for ext in (".wav", ".mp3", ".flac", ".ogg", ".aiff"):
            (tmp_path / f"sample{ext}").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 5

    def test_case_insensitive_extension(self, tmp_path):
        (tmp_path / "kick.WAV").write_bytes(b"x")
        (tmp_path / "snare.Mp3").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 2

    def test_skips_hidden_dirs(self, tmp_path):
        (tmp_path / ".hidden").mkdir()
        (tmp_path / ".hidden" / "kick.wav").write_bytes(b"x")
        (tmp_path / "visible.wav").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        assert len(results) == 1
        assert results[0].name == "visible.wav"

    def test_empty_dir_yields_nothing(self, tmp_path):
        assert list(walk_audio_files(tmp_path)) == []

    def test_missing_root_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            list(walk_audio_files(tmp_path / "nonexistent"))


class TestWalkerYieldsPath:
    def test_returns_pathlib_path(self, tmp_path):
        (tmp_path / "kick.wav").write_bytes(b"x")
        results = list(walk_audio_files(tmp_path))
        from pathlib import Path
        assert isinstance(results[0], Path)
