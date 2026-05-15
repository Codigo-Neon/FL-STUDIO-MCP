"""Handler registry for bridge methods.

Decouples the bridge transport from the actual FL Studio API calls. Tests
register fake handlers; in production, `device_test.py` registers handlers
that call FL's `transport`, `patterns`, `channels`, `mixer` modules.
"""
from __future__ import annotations
from typing import Any, Callable

__all__ = ["HandlerRegistry", "HandlerError"]

Handler = Callable[[dict], Any]


class HandlerError(Exception):
    """Raised when a handler is missing, double-registered, or fails internally."""


class HandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, method: str, handler: Handler) -> None:
        if method in self._handlers:
            raise HandlerError(f"method '{method}' already registered")
        self._handlers[method] = handler

    def method(self, name: str) -> Callable[[Handler], Handler]:
        """Decorator form of register()."""
        def _decorator(fn: Handler) -> Handler:
            self.register(name, fn)
            return fn
        return _decorator

    def dispatch(self, method: str, params: dict) -> Any:
        handler = self._handlers.get(method)
        if handler is None:
            raise HandlerError(f"unknown method '{method}'")
        try:
            return handler(params)
        except Exception as exc:
            raise HandlerError(str(exc)) from exc

    def list_methods(self) -> list[str]:
        return list(self._handlers.keys())
