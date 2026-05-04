"""Edit Claude Desktop's MCP server configuration safely.

We always create a `.bak` of the existing config before mutating it. JSON parse
errors raise `ConfigCorruptedError` so the caller can offer the user a recovery
path (restore from .bak or write a fresh config).
"""
import json
import os
import shutil
from pathlib import Path
from typing import Optional


class ConfigCorruptedError(Exception):
    """Raised when the existing claude_desktop_config.json is not valid JSON."""


def _default_appdata() -> Path:
    return Path(os.environ.get("APPDATA", ""))


def find_config_path(appdata: Optional[Path] = None) -> Path:
    """Return the canonical location of Claude Desktop's config file."""
    base = appdata if appdata is not None else _default_appdata()
    return base / "Claude" / "claude_desktop_config.json"


def backup_config(config_path: Path) -> Optional[Path]:
    """Copy the config to `<name>.json.bak`. Returns the backup path, or None
    if the source did not exist (no backup needed).
    """
    if not config_path.exists():
        return None
    backup_path = config_path.with_suffix(".json.bak")
    shutil.copy2(config_path, backup_path)
    return backup_path


def register_mcp_server(
    config_path: Path,
    name: str,
    command: str,
    args: list[str],
) -> None:
    """Idempotently add (or overwrite) an MCP server entry in the config.

    Existing servers under different names are preserved. If the file does not
    exist, it is created with just this one server. The file is always written
    back with 2-space indentation for human readability.

    Raises ConfigCorruptedError if the existing file is not valid JSON.
    """
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
        except json.JSONDecodeError as exc:
            raise ConfigCorruptedError(
                f"{config_path.name} is not valid JSON: {exc.msg}"
            ) from exc
    else:
        data = {}

    servers = data.setdefault("mcpServers", {})
    servers[name] = {"command": command, "args": args}

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, indent=2))
