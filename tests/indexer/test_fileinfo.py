import hashlib
from indexer.fileinfo import compute_content_hash, stat_file


class TestContentHash:
    def test_hash_is_deterministic(self, tmp_path):
        f = tmp_path / "a.wav"
        f.write_bytes(b"some audio data" * 100)
        h1 = compute_content_hash(f)
        h2 = compute_content_hash(f)
        assert h1 == h2
        assert len(h1) == 40  # sha1 hex

    def test_different_contents_different_hashes(self, tmp_path):
        a = tmp_path / "a.wav"
        b = tmp_path / "b.wav"
        a.write_bytes(b"abc")
        b.write_bytes(b"xyz")
        assert compute_content_hash(a) != compute_content_hash(b)

    def test_same_contents_different_names_different_hashes(self, tmp_path):
        # Filename is included in the hash to disambiguate identical samples
        a = tmp_path / "a.wav"
        b = tmp_path / "b.wav"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        assert compute_content_hash(a) != compute_content_hash(b)

    def test_handles_file_smaller_than_64kb(self, tmp_path):
        f = tmp_path / "tiny.wav"
        f.write_bytes(b"x" * 100)
        h = compute_content_hash(f)
        assert len(h) == 40

    def test_handles_empty_file(self, tmp_path):
        f = tmp_path / "empty.wav"
        f.write_bytes(b"")
        h = compute_content_hash(f)
        assert len(h) == 40


class TestStatFile:
    def test_returns_size_and_mtime(self, tmp_path):
        f = tmp_path / "a.wav"
        f.write_bytes(b"x" * 1234)
        info = stat_file(f)
        assert info["size_bytes"] == 1234
        assert info["mtime"] > 0
        assert isinstance(info["mtime"], int)
