"""Tests for installer.setup_engine.claude_config."""
import json
from pathlib import Path
import pytest

from installer.setup_engine.claude_config import (
    find_config_path,
    backup_config,
    register_mcp_server,
    ConfigCorruptedError,
)


class TestFindConfigPath:
    def test_returns_default_path(self):
        appdata = Path("C:/Users/u/AppData/Roaming")
        result = find_config_path(appdata=appdata)
        assert result == appdata / "Claude" / "claude_desktop_config.json"


class TestBackupConfig:
    def test_creates_bak_with_same_contents(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_file(str(config), contents='{"foo": "bar"}')

        backup_path = backup_config(config)

        assert backup_path == config.with_suffix(".json.bak")
        assert backup_path.read_text() == '{"foo": "bar"}'

    def test_no_op_when_config_missing(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        result = backup_config(config)
        assert result is None


class TestRegisterMcpServer:
    def test_creates_config_when_missing(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_dir(str(config.parent))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="C:/Program Files/FL MCP Studio/python-embed/python.exe",
            args=["C:/Program Files/FL MCP Studio/trigger.py"],
        )

        data = json.loads(config.read_text())
        assert data == {
            "mcpServers": {
                "flstudio": {
                    "command": "C:/Program Files/FL MCP Studio/python-embed/python.exe",
                    "args": ["C:/Program Files/FL MCP Studio/trigger.py"],
                }
            }
        }

    def test_preserves_existing_servers(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        existing = {
            "mcpServers": {
                "other-server": {"command": "node", "args": ["other.js"]}
            }
        }
        fs.create_file(str(config), contents=json.dumps(existing))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="python",
            args=["trigger.py"],
        )

        data = json.loads(config.read_text())
        assert "other-server" in data["mcpServers"]
        assert data["mcpServers"]["flstudio"] == {
            "command": "python",
            "args": ["trigger.py"],
        }

    def test_overwrites_same_named_server(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        existing = {
            "mcpServers": {
                "flstudio": {"command": "old", "args": ["old.py"]}
            }
        }
        fs.create_file(str(config), contents=json.dumps(existing))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="new",
            args=["new.py"],
        )

        data = json.loads(config.read_text())
        assert data["mcpServers"]["flstudio"] == {
            "command": "new",
            "args": ["new.py"],
        }

    def test_raises_on_corrupted_json(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_file(str(config), contents="this is not json {")

        with pytest.raises(ConfigCorruptedError, match="claude_desktop_config.json"):
            register_mcp_server(
                config_path=config,
                name="flstudio",
                command="python",
                args=["trigger.py"],
            )

    def test_writes_with_2_space_indent(self, fs):
        config = Path("C:/Users/u/AppData/Roaming/Claude/claude_desktop_config.json")
        fs.create_dir(str(config.parent))

        register_mcp_server(
            config_path=config,
            name="flstudio",
            command="python",
            args=["trigger.py"],
        )

        text = config.read_text()
        assert "  \"mcpServers\"" in text  # 2-space indent on top-level key
