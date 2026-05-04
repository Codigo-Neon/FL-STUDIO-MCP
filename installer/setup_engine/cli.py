"""Command-line interface for the Setup Engine.

Each setup step has a subcommand so the GUI (sub-project C) can shell out OR
import these functions directly. Useful standalone for QA on real Windows
machines without a GUI.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from installer.setup_engine.detect import detect_environment
from installer.setup_engine.claude_config import (
    find_config_path,
    backup_config,
    register_mcp_server,
)
from installer.setup_engine.fl_studio import install_device_script
from installer.setup_engine.loopmidi import (
    create_port,
    download_loopmidi,
    extract_loopmidi,
    install_loopmidi,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="setup_engine",
        description="FL MCP Studio installer — Setup Engine CLI (run subcommands manually for debugging).",
    )
    sub = parser.add_subparsers(dest="subcmd", required=True)

    sub.add_parser("detect", help="Print which dependencies are installed.")

    p_install_lm = sub.add_parser("install-loopmidi", help="Download + extract + silent-install loopMIDI.")
    p_install_lm.add_argument("--zip-dest", type=Path, default=Path("loopmidi_setup.zip"),
                              help="Where to save the downloaded ZIP.")
    p_install_lm.add_argument("--extract-dir", type=Path, default=Path("loopmidi_extracted"),
                              help="Where to extract the ZIP contents.")

    p_create = sub.add_parser("create-port", help="Create a loopMIDI virtual port.")
    p_create.add_argument("--loopmidi-exe", type=Path, required=True)
    p_create.add_argument("--port-name", type=str, default="FL_MCP")

    p_script = sub.add_parser("install-script", help="Copy device_test.py into FL Studio's Hardware dir.")
    p_script.add_argument("--source", type=Path, required=True)
    p_script.add_argument("--fl-settings", type=Path, required=True)
    p_script.add_argument("--device-name", type=str, default="FL_MCP")

    p_mcp = sub.add_parser("register-mcp", help="Register the FL MCP server in Claude Desktop config.")
    p_mcp.add_argument("--config", type=Path, default=None,
                       help="Path to claude_desktop_config.json (default: %APPDATA%/Claude/...)")
    p_mcp.add_argument("--name", type=str, default="flstudio")
    p_mcp.add_argument("--command", type=str, required=True,
                       help="Python interpreter path to launch the MCP server.")
    p_mcp.add_argument("--args", nargs="+", required=True,
                       help="Arguments passed to the interpreter (typically [trigger.py]).")

    return parser


def _print_detect(report) -> None:
    def status(value) -> str:
        return "OK" if value else "MISSING"

    print(f"Claude Desktop:       {status(report.claude_desktop_path)} ({report.claude_desktop_path})")
    print(f"FL Studio Settings:   {status(report.fl_studio_settings_dir)} ({report.fl_studio_settings_dir})")
    print(f"loopMIDI:             {status(report.loopmidi_path)} ({report.loopmidi_path})")
    print(f"WebView2 Runtime:     {status(report.webview2_installed)}")
    print(f"\nReady to install: {report.is_ready()}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.subcmd == "detect":
        report = detect_environment()
        _print_detect(report)
        return 0 if report.is_ready() else 1

    if args.subcmd == "install-loopmidi":
        download_loopmidi(dest=args.zip_dest)
        installer_exe = extract_loopmidi(zip_path=args.zip_dest, extract_dir=args.extract_dir)
        install_loopmidi(installer=installer_exe)
        return 0

    if args.subcmd == "create-port":
        create_port(loopmidi_exe=args.loopmidi_exe, port_name=args.port_name)
        return 0

    if args.subcmd == "install-script":
        install_device_script(
            source_script=args.source,
            fl_studio_settings_dir=args.fl_settings,
            device_name=args.device_name,
        )
        return 0

    if args.subcmd == "register-mcp":
        config = args.config or find_config_path()
        backup_config(config)
        register_mcp_server(
            config_path=config,
            name=args.name,
            command=args.command,
            args=args.args,
        )
        return 0

    parser.error(f"Unknown command: {args.subcmd}")
    return 2  # unreachable but satisfies type checkers


if __name__ == "__main__":
    sys.exit(main())
