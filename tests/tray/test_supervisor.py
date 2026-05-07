"""Tests for installer.tray.supervisor."""
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from installer.tray.supervisor import (
    ServerStatus,
    Supervisor,
)


class TestServerStatus:
    def test_running_means_pid_present(self):
        status = ServerStatus(pid=4823, midi_port_present=True)
        assert status.is_running() is True

    def test_no_pid_means_not_running(self):
        status = ServerStatus(pid=None, midi_port_present=True)
        assert status.is_running() is False

    def test_color_green_when_all_ok(self):
        assert ServerStatus(pid=4823, midi_port_present=True).color() == "green"

    def test_color_yellow_when_running_but_midi_missing(self):
        assert ServerStatus(pid=4823, midi_port_present=False).color() == "yellow"

    def test_color_red_when_not_running(self):
        assert ServerStatus(pid=None, midi_port_present=False).color() == "red"


class TestSupervisorFindServerPid:
    def test_returns_pid_when_trigger_py_process_found(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 4823, "name": "python.exe", "cmdline": ["python.exe", "trigger.py"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() == 4823

    def test_returns_none_when_no_trigger_py_running(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 100, "name": "explorer.exe", "cmdline": ["explorer.exe"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() is None

    def test_handles_missing_cmdline_gracefully(self, monkeypatch):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 100, "name": "kernel", "cmdline": None}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )

        sup = Supervisor()
        assert sup.find_server_pid() is None


class TestSupervisorCheckStatus:
    def test_combines_pid_and_port_check(self, monkeypatch, mock_rtmidi):
        fake_proc = MagicMock()
        fake_proc.info = {"pid": 4823, "name": "python.exe", "cmdline": ["python", "trigger.py"]}
        monkeypatch.setattr(
            "installer.tray.supervisor.psutil.process_iter",
            MagicMock(return_value=[fake_proc]),
        )
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]

        status = Supervisor().check_status()

        assert status.pid == 4823
        assert status.midi_port_present is True
        assert status.color() == "green"


class TestSupervisorTestMidi:
    def test_sends_c5_note_via_transport(self, monkeypatch, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = ["FL_MCP 0"]
        sent_messages = []
        mock_rtmidi.MidiOut.return_value.send_message.side_effect = lambda msg: sent_messages.append(msg)

        result = Supervisor().test_midi()

        assert result is True
        assert [0x90, 0x3C, 0x64] in sent_messages  # note on
        assert [0x80, 0x3C, 0x00] in sent_messages  # note off

    def test_returns_false_when_port_missing(self, mock_rtmidi):
        mock_rtmidi.MidiOut.return_value.get_ports.return_value = []

        result = Supervisor().test_midi()

        assert result is False
