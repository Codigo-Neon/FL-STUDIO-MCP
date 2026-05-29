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
    # Mix/mastering reads
    def get_track_volume(self, index: int) -> float: ...
    def get_track_pan(self, index: int) -> float: ...
    def get_track_mute(self, index: int) -> bool: ...
    def get_track_solo(self, index: int) -> bool: ...
    def get_track_peaks(self, index: int) -> tuple: ...   # (L, R) in dB
    def get_effect_count(self, track: int) -> int: ...
    def get_effect_name(self, track: int, slot: int) -> str: ...
    def get_track_route_sends(self, index: int) -> list: ...


def _build_track_dict(api, idx: int) -> dict:
    fx = [api.get_effect_name(idx, s) for s in range(api.get_effect_count(idx))]
    return {
        "idx": idx,
        "name": api.get_mixer_track_name(idx),
        "vol": api.get_track_volume(idx),
        "pan": api.get_track_pan(idx),
        "mute": api.get_track_mute(idx),
        "solo": api.get_track_solo(idx),
        "fx": fx,
        "sends": api.get_track_route_sends(idx),
    }


def _is_empty_track(track: dict) -> bool:
    name = track["name"]
    is_default_name = name.startswith("Insert ") or name == ""
    return is_default_name and track["vol"] == 0.0 and not track["fx"]


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

    @registry.method("get_mixer_snapshot")
    def _get_mixer_snapshot(params):
        tracks = []
        for idx in range(api.get_mixer_track_count()):
            t = _build_track_dict(api, idx)
            if idx == 0 or not _is_empty_track(t):
                tracks.append(t)
        return {"tracks": tracks}

    @registry.method("get_master_snapshot")
    def _get_master_snapshot(params):
        t = _build_track_dict(api, 0)
        return {"idx": 0, "name": t["name"], "vol": t["vol"],
                "pan": t["pan"], "fx": t["fx"], "sends": t["sends"]}
