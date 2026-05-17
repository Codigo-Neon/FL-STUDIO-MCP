"""Install the FL MCP `device_test.py` script into FL Studio's Hardware folder.

FL Studio reads MIDI controller scripts from
`<Settings>/Hardware/<DeviceName>/device_*.py`. We create that directory if
needed and write both the script and a small `.nfo` companion that FL Studio
uses to display the device's friendly name in its MIDI Settings panel.
"""
import shutil
from pathlib import Path

HARDWARE_SUBDIR = "Hardware"


def find_hardware_dir(fl_studio_settings_dir: Path) -> Path:
    """Return the Hardware/ directory under FL Studio's Settings, creating it
    if it does not yet exist (FL Studio creates it on first scripted-controller
    install, so missing-on-fresh-install is normal)."""
    hardware = fl_studio_settings_dir / HARDWARE_SUBDIR
    hardware.mkdir(parents=True, exist_ok=True)
    return hardware


def install_device_script(
    source_script: Path,
    fl_studio_settings_dir: Path,
    device_name: str,
) -> Path:
    """Copy `source_script` to `<Settings>/Hardware/<device_name>/device_test.py`
    and write a companion `device_<name>.nfo` metadata file. Returns the path to
    the installed script.

    Overwrites any existing files at the target location (the GUI presents this
    as "reinstall" rather than "fresh install" when re-run).
    """
    if not source_script.exists():
        raise FileNotFoundError(f"Source script not found: {source_script}")

    hardware = find_hardware_dir(fl_studio_settings_dir)
    device_dir = hardware / device_name
    device_dir.mkdir(parents=True, exist_ok=True)

    target_script = device_dir / "device_test.py"
    shutil.copyfile(source_script, target_script)

    nfo = device_dir / f"device_{device_name}.nfo"
    nfo.write_text(
        f"name={device_name}\n"
        f"script=device_test.py\n"
        "vendor=FL MCP Studio\n"
    )

    return target_script


def install_bridge_package(
    source_root: Path,
    fl_studio_settings_dir: Path,
    device_name: str,
) -> Path:
    """Copy the `bridge/` package next to the installed device_test.py so the
    FL-side script can `from bridge import ...`.

    `source_root` must be the staging/build directory that contains a
    `bridge/` subdirectory. Raises FileNotFoundError if it's missing.
    Returns the path to the installed bridge directory.
    """
    bridge_src = source_root / "bridge"
    if not bridge_src.exists():
        raise FileNotFoundError(f"bridge package not found at source: {bridge_src}")

    hardware = find_hardware_dir(fl_studio_settings_dir)
    device_dir = hardware / device_name
    device_dir.mkdir(parents=True, exist_ok=True)

    bridge_dst = device_dir / "bridge"
    if bridge_dst.exists():
        shutil.rmtree(bridge_dst)
    shutil.copytree(
        bridge_src,
        bridge_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    return bridge_dst
