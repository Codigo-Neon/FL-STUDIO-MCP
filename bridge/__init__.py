"""Bidirectional bridge between Linux MCP and FL Studio script.

Exports:
    BridgeClient    — Linux side
    BridgeServer    — FL side
    HandlerRegistry — method dispatch
    BridgeError     — client-side errors
    HandlerError    — server-side errors
"""
from bridge.client import BridgeClient, BridgeError
from bridge.server import BridgeServer
from bridge.handlers import HandlerRegistry, HandlerError
from bridge.protocol import DEFAULT_HOST, DEFAULT_PORT

__all__ = [
    "BridgeClient", "BridgeError",
    "BridgeServer",
    "HandlerRegistry", "HandlerError",
    "DEFAULT_HOST", "DEFAULT_PORT",
]
