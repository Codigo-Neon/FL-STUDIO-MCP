"""Tests for the handler registry and dispatcher."""
import pytest
from bridge.handlers import HandlerRegistry, HandlerError


class TestHandlerRegistry:
    def test_register_and_dispatch(self):
        reg = HandlerRegistry()
        reg.register("ping", lambda params: {"pong": True})
        result = reg.dispatch("ping", {})
        assert result == {"pong": True}

    def test_dispatch_passes_params(self):
        reg = HandlerRegistry()
        reg.register("echo", lambda params: {"echoed": params["msg"]})
        result = reg.dispatch("echo", {"msg": "hi"})
        assert result == {"echoed": "hi"}

    def test_unknown_method_raises(self):
        reg = HandlerRegistry()
        with pytest.raises(HandlerError, match="unknown method"):
            reg.dispatch("nope", {})

    def test_handler_exception_propagates_as_handler_error(self):
        reg = HandlerRegistry()
        def boom(params):
            raise ValueError("kaboom")
        reg.register("boom", boom)
        with pytest.raises(HandlerError, match="kaboom"):
            reg.dispatch("boom", {})

    def test_register_decorator_form(self):
        reg = HandlerRegistry()

        @reg.method("ping")
        def ping(params):
            return {"pong": True}

        assert reg.dispatch("ping", {}) == {"pong": True}

    def test_double_registration_raises(self):
        reg = HandlerRegistry()
        reg.register("ping", lambda p: {})
        with pytest.raises(HandlerError, match="already registered"):
            reg.register("ping", lambda p: {})

    def test_list_methods(self):
        reg = HandlerRegistry()
        reg.register("a", lambda p: {})
        reg.register("b", lambda p: {})
        assert sorted(reg.list_methods()) == ["a", "b"]
