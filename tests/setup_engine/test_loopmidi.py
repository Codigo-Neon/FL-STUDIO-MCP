"""Tests for installer.setup_engine.loopmidi."""
from pathlib import Path
from unittest.mock import MagicMock, call
import pytest

from installer.setup_engine.loopmidi import (
    port_exists,
    create_port,
    LoopMidiNotInstalledError,
)


class TestPortExists:
    def test_returns_true_when_rtmidi_lists_port(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = [
            "Microsoft GS Wavetable Synth 0",
            "FL_MCP 1",
        ]

        assert port_exists("FL_MCP") is True

    def test_returns_false_when_no_match(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["Other 0"]

        assert port_exists("FL_MCP") is False

    def test_substring_match_is_used(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP Suffix 2"]

        assert port_exists("FL_MCP") is True


class TestCreatePort:
    def test_invokes_loopmidi_with_addport_flag(self, monkeypatch, mock_rtmidi, fs):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        fs.create_file(str(loopmidi_exe))
        # First poll: port absent. After "running" loopMIDI, port present.
        mock_rtmidi.MidiOut.return_value.get_ports.side_effect = [
            [],            # before
            ["FL_MCP 0"],  # after
        ]
        fake_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", fake_run)

        create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

        fake_run.assert_called_once_with(
            [str(loopmidi_exe), "/AddPort:FL_MCP"],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_no_op_when_port_already_exists(self, monkeypatch, mock_rtmidi):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]
        fake_run = MagicMock()
        monkeypatch.setattr("subprocess.run", fake_run)

        create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

        fake_run.assert_not_called()

    def test_raises_when_loopmidi_exe_missing(self, monkeypatch, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []
        loopmidi_exe = Path("C:/missing/loopMIDI.exe")

        with pytest.raises(LoopMidiNotInstalledError):
            create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")

    def test_raises_when_loopmidi_call_fails(self, monkeypatch, fs, mock_rtmidi):
        loopmidi_exe = Path("C:/Program Files/loopMIDI/loopMIDI.exe")
        fs.create_file(str(loopmidi_exe))
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []
        fake_run = MagicMock(return_value=MagicMock(returncode=1, stderr="busy"))
        monkeypatch.setattr("subprocess.run", fake_run)

        with pytest.raises(RuntimeError, match="loopMIDI exited with code 1"):
            create_port(loopmidi_exe=loopmidi_exe, port_name="FL_MCP")


from installer.setup_engine.loopmidi import (
    download_loopmidi,
    install_loopmidi,
    LOOPMIDI_DOWNLOAD_URL,
)


class TestDownloadLoopmidi:
    def test_writes_installer_to_dest(self, monkeypatch, fs):
        dest = Path("/tmp/loopmidi_setup.exe")
        fake_response = MagicMock()
        fake_response.read.return_value = b"FAKE INSTALLER BYTES"
        fake_response.__enter__ = MagicMock(return_value=fake_response)
        fake_response.__exit__ = MagicMock(return_value=False)

        fake_urlopen = MagicMock(return_value=fake_response)
        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

        result = download_loopmidi(dest=dest)

        assert result == dest
        assert dest.read_bytes() == b"FAKE INSTALLER BYTES"
        fake_urlopen.assert_called_once_with(LOOPMIDI_DOWNLOAD_URL, timeout=60)

    def test_raises_on_network_error(self, monkeypatch, fs):
        from urllib.error import URLError
        dest = Path("/tmp/loopmidi_setup.exe")
        monkeypatch.setattr(
            "urllib.request.urlopen",
            MagicMock(side_effect=URLError("no internet")),
        )

        with pytest.raises(URLError):
            download_loopmidi(dest=dest)


class TestInstallLoopmidi:
    def test_runs_installer_silently(self, monkeypatch, fs):
        installer = Path("C:/tmp/loopmidi_setup.exe")
        fs.create_file(str(installer))
        fake_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", fake_run)

        install_loopmidi(installer=installer)

        fake_run.assert_called_once_with(
            [str(installer), "/SILENT", "/NORESTART"],
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_raises_on_installer_failure(self, monkeypatch, fs):
        installer = Path("C:/tmp/loopmidi_setup.exe")
        fs.create_file(str(installer))
        monkeypatch.setattr(
            "subprocess.run",
            MagicMock(return_value=MagicMock(returncode=2, stderr="cancelled")),
        )

        with pytest.raises(RuntimeError, match="loopMIDI installer exited with code 2"):
            install_loopmidi(installer=installer)


def test_download_url_points_to_official_site():
    assert "tobias-erichsen.de" in LOOPMIDI_DOWNLOAD_URL


import io
import zipfile as _zipfile

from installer.setup_engine.loopmidi import extract_loopmidi


class TestExtractLoopmidi:
    def _make_zip_with_exe(self, fs, zip_path: Path, inner_exe_name: str = "loopMIDISetup.exe") -> None:
        """Build a real ZIP file containing one .exe entry, using pyfakefs."""
        buf = io.BytesIO()
        with _zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(inner_exe_name, b"FAKE EXE BYTES")
        fs.create_file(str(zip_path), contents=buf.getvalue())

    def test_returns_path_to_inner_exe(self, fs):
        zip_path = Path("/fake/loopmidi.zip")
        extract_dir = Path("/fake/extracted")
        self._make_zip_with_exe(fs, zip_path)

        result = extract_loopmidi(zip_path=zip_path, extract_dir=extract_dir)

        assert result == extract_dir / "loopMIDISetup.exe"
        assert result.exists()
        assert result.read_bytes() == b"FAKE EXE BYTES"

    def test_creates_extract_dir_if_missing(self, fs):
        zip_path = Path("/fake/loopmidi.zip")
        extract_dir = Path("/fake/does_not_exist_yet")
        self._make_zip_with_exe(fs, zip_path)

        extract_loopmidi(zip_path=zip_path, extract_dir=extract_dir)

        assert extract_dir.is_dir()

    def test_raises_when_zip_has_no_exe(self, fs):
        zip_path = Path("/fake/loopmidi.zip")
        extract_dir = Path("/fake/extracted")
        buf = io.BytesIO()
        with _zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", b"no exe here")
        fs.create_file(str(zip_path), contents=buf.getvalue())

        with pytest.raises(FileNotFoundError, match="No .exe found"):
            extract_loopmidi(zip_path=zip_path, extract_dir=extract_dir)
