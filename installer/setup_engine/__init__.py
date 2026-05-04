"""Setup Engine — pure-Python library that performs the install steps the
Windows wizard (sub-project C) needs to invoke. Each module is independently
testable; this package re-exports the names the wizard will import.
"""
from installer.setup_engine.detect import (
    EnvironmentReport,
    detect_environment,
)
from installer.setup_engine.claude_config import (
    ConfigCorruptedError,
    backup_config,
    find_config_path,
    register_mcp_server,
)
from installer.setup_engine.fl_studio import install_device_script
from installer.setup_engine.loopmidi import (
    LOOPMIDI_DOWNLOAD_URL,
    LoopMidiNotInstalledError,
    create_port,
    download_loopmidi,
    extract_loopmidi,
    install_loopmidi,
    port_exists,
)

__all__ = [
    "ConfigCorruptedError",
    "EnvironmentReport",
    "LOOPMIDI_DOWNLOAD_URL",
    "LoopMidiNotInstalledError",
    "backup_config",
    "create_port",
    "detect_environment",
    "download_loopmidi",
    "extract_loopmidi",
    "find_config_path",
    "install_device_script",
    "install_loopmidi",
    "port_exists",
    "register_mcp_server",
]
