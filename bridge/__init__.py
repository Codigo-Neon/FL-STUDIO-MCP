"""Bidirectional bridge between Linux MCP and FL Studio script.

Two transport variants:

    TCP (bridge.client/bridge.server) — original, BLOCKED by FL Studio
        sandbox. Kept as code reference / fallback if Image-Line relaxes
        the sandbox in the future.
    SysEx (bridge.sysex_client/bridge.sysex_server) — operational, uses
        python-rtmidi on Linux and device.midiOutSysex on FL.

Production code should import the SysEx variant.
"""
from bridge.handlers import HandlerRegistry, HandlerError
from bridge.protocol import DEFAULT_HOST, DEFAULT_PORT
from bridge.sysex_server import SysExServer

# Legacy TCP and SysEx Linux client depend on stdlib socket/threading and
# python-rtmidi respectively, both of which are blocked or unavailable inside
# FL Studio's embedded Python sub-interpreter. We import them defensively so
# `from bridge import ...` works on both sides without the FL side crashing.
try:
    from bridge.client import BridgeClient, BridgeError
    from bridge.server import BridgeServer
    _TCP_AVAILABLE = True
except BaseException:
    BridgeClient = None  # type: ignore
    BridgeError = None  # type: ignore
    BridgeServer = None  # type: ignore
    _TCP_AVAILABLE = False

try:
    from bridge.sysex_client import SysExClient, SysExBridgeError
    _SYSEX_CLIENT_AVAILABLE = True
except BaseException:
    SysExClient = None  # type: ignore
    SysExBridgeError = None  # type: ignore
    _SYSEX_CLIENT_AVAILABLE = False

__all__ = [
    # TCP variant (legacy, blocked by FL sandbox)
    "BridgeClient", "BridgeError",
    "BridgeServer",
    # Shared
    "HandlerRegistry", "HandlerError",
    "DEFAULT_HOST", "DEFAULT_PORT",
    # SysEx variant (operational)
    "SysExClient", "SysExBridgeError",
    "SysExServer",
]
