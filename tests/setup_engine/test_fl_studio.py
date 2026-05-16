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


def test_install_bridge_package_copies_all_modules(tmp_path):
    """install_bridge_package copies bridge/ into the device directory."""
    from installer.setup_engine.fl_studio import install_bridge_package

    src_root = tmp_path / "src"
    (src_root / "bridge").mkdir(parents=True)
    for name in ("__init__.py", "protocol.py", "server.py",
                 "client.py", "handlers.py", "fl_handlers.py", "fl_adapter.py"):
        (src_root / "bridge" / name).write_text(f"# {name}\n")

    fl_settings = tmp_path / "fl_settings"
    install_bridge_package(
        source_root=src_root,
        fl_studio_settings_dir=fl_settings,
        device_name="FL_MCP",
    )

    bridge_dst = fl_settings / "Hardware" / "FL_MCP" / "bridge"
    assert (bridge_dst / "__init__.py").exists()
    assert (bridge_dst / "protocol.py").exists()
    assert (bridge_dst / "server.py").exists()
    assert (bridge_dst / "handlers.py").exists()
    assert (bridge_dst / "fl_handlers.py").exists()
    assert (bridge_dst / "fl_adapter.py").exists()


def test_install_bridge_package_overwrites_existing(tmp_path):
    """Re-running install replaces the previous bridge dir cleanly."""
    from installer.setup_engine.fl_studio import install_bridge_package

    src_root = tmp_path / "src"
    (src_root / "bridge").mkdir(parents=True)
    (src_root / "bridge" / "__init__.py").write_text("# new\n")

    fl_settings = tmp_path / "fl_settings"
    bridge_dst = fl_settings / "Hardware" / "FL_MCP" / "bridge"
    bridge_dst.mkdir(parents=True)
    (bridge_dst / "stale.py").write_text("# old, should be removed\n")

    install_bridge_package(
        source_root=src_root,
        fl_studio_settings_dir=fl_settings,
        device_name="FL_MCP",
    )

    assert not (bridge_dst / "stale.py").exists()
    assert (bridge_dst / "__init__.py").read_text() == "# new\n"


def test_install_bridge_package_raises_if_source_missing(tmp_path):
    """If source bridge/ doesn't exist (broken build), fail loudly."""
    import pytest as _pytest
    from installer.setup_engine.fl_studio import install_bridge_package

    with _pytest.raises(FileNotFoundError, match="bridge"):
        install_bridge_package(
            source_root=tmp_path / "no_such_dir",
            fl_studio_settings_dir=tmp_path / "fl_settings",
            device_name="FL_MCP",
        )
