"""Tests for installer.setup_engine.fl_studio."""
from pathlib import Path
import pytest

from installer.setup_engine.fl_studio import (
    find_hardware_dir,
    install_device_script,
    HARDWARE_SUBDIR,
)


class TestFindHardwareDir:
    def test_returns_hardware_subdir_under_settings(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))

        result = find_hardware_dir(fl_studio_settings_dir=settings_dir)

        assert result == settings_dir / "Hardware"

    def test_creates_hardware_dir_if_missing(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))

        result = find_hardware_dir(fl_studio_settings_dir=settings_dir)

        assert result.is_dir()


class TestInstallDeviceScript:
    def test_copies_script_under_named_subdir(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="# device script body\n")

        result = install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        target = settings_dir / "Hardware" / "FL_MCP" / "device_test.py"
        assert target.exists()
        assert target.read_text() == "# device script body\n"
        assert result == target

    def test_writes_companion_metadata_file(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="x")

        install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        meta = settings_dir / "Hardware" / "FL_MCP" / "device_FL_MCP.nfo"
        assert meta.exists()
        text = meta.read_text()
        assert "FL_MCP" in text
        assert "device_test.py" in text

    def test_overwrites_existing_install(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        target_dir = settings_dir / "Hardware" / "FL_MCP"
        fs.create_file(str(target_dir / "device_test.py"), contents="OLD")
        source_script = Path("/install/device_test.py")
        fs.create_file(str(source_script), contents="NEW")

        install_device_script(
            source_script=source_script,
            fl_studio_settings_dir=settings_dir,
            device_name="FL_MCP",
        )

        assert (target_dir / "device_test.py").read_text() == "NEW"

    def test_raises_when_source_missing(self, fs):
        settings_dir = Path("C:/Users/u/Documents/Image-Line/FL Studio/Settings")
        fs.create_dir(str(settings_dir))
        source_script = Path("/install/missing.py")

        with pytest.raises(FileNotFoundError):
            install_device_script(
                source_script=source_script,
                fl_studio_settings_dir=settings_dir,
                device_name="FL_MCP",
            )


def test_hardware_subdir_constant_value():
    assert HARDWARE_SUBDIR == "Hardware"
