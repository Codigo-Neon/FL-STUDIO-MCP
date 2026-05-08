"""Tests for installer.build.fetch_python."""
import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from installer.build.fetch_python import (
    PYTHON_VERSION,
    embed_zip_url,
    fetch_and_extract,
    patch_pth_to_enable_site,
)


class TestEmbedZipUrl:
    def test_default_version_url(self):
        url = embed_zip_url()
        assert url.startswith("https://www.python.org/ftp/python/")
        assert PYTHON_VERSION in url
        assert url.endswith(f"python-{PYTHON_VERSION}-embed-amd64.zip")

    def test_custom_version_url(self):
        url = embed_zip_url(version="3.12.0")
        assert "3.12.0" in url


class TestPatchPthToEnableSite:
    def test_uncomments_import_site(self, tmp_path):
        pth = tmp_path / "python311._pth"
        pth.write_text(
            "python311.zip\n.\n\n# Uncomment to run site.main() automatically\n#import site\n"
        )

        patch_pth_to_enable_site(pth)

        text = pth.read_text()
        assert "\nimport site\n" in text
        assert "#import site" not in text


class TestFetchAndExtract:
    def test_downloads_and_extracts(self, monkeypatch, tmp_path):
        # Build a fake embed zip in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("python.exe", b"FAKE EXE")
            zf.writestr("python311._pth", "python311.zip\n.\n#import site\n")

        fake_response = MagicMock()
        fake_response.read.return_value = buf.getvalue()
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr(
            "urllib.request.urlopen",
            MagicMock(return_value=fake_response),
        )

        target_dir = tmp_path / "embed"
        result = fetch_and_extract(target_dir=target_dir)

        assert result == target_dir
        assert (target_dir / "python.exe").read_bytes() == b"FAKE EXE"
        # _pth must have been patched
        pth = (target_dir / "python311._pth").read_text()
        assert "\nimport site\n" in pth

    def test_creates_target_dir_if_missing(self, monkeypatch, tmp_path):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("python311._pth", "#import site\n")

        fake_response = MagicMock()
        fake_response.read.return_value = buf.getvalue()
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=fake_response))

        target_dir = tmp_path / "does/not/exist/yet"
        fetch_and_extract(target_dir=target_dir)

        assert target_dir.is_dir()
