"""FL-Studio-specific bridge handlers.

`FLApi` is the Protocol the rest of the bridge depends on. Production code
provides an adapter that calls FL's `transport`, `patterns`, `channels`,
`mixer` modules. Tests inject a fake.
"""
from typing import Protocol, runtime_checkable

from bridge.handlers import HandlerRegistry

__all__ = ["FLApi", "register_all"]


@runtime_checkable
class FLApi(Protocol):
    def get_bpm(self) -> float: ...
    def get_current_pattern(self) -> int: ...
    def get_pattern_count(self) -> int: ...
    def get_channel_count(self) -> int: ...
    def get_channel_name(self, index: int) -> str: ...
    def get_mixer_track_count(self) -> int: ...
    def get_mixer_track_name(self, index: int) -> str: ...


def register_all(registry: HandlerRegistry, api: FLApi) -> None:
    """Register every FL handler against the given registry."""

    @registry.method("ping")
    def _ping(params):
        return {"pong": True}

    @registry.method("get_fl_state")
    def _get_fl_state(params):
        return {
            "bpm": api.get_bpm(),
            "current_pattern": api.get_current_pattern(),
            "pattern_count": api.get_pattern_count(),
            "channels": [
                {"index": i, "name": api.get_channel_name(i)}
                for i in range(api.get_channel_count())
            ],
            "mixer_tracks": [
                {"index": i, "name": api.get_mixer_track_name(i)}
                for i in range(api.get_mixer_track_count())
            ],
        }
