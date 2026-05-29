"""Pure mix/mastering analysis. Takes plain dicts (mixer snapshots, peak
reports) and returns structured reports. No FL Studio dependency — fully
testable with mock data."""

GENRE_TARGETS = {
    "boom_bap": {"lufs": -9, "true_peak": -1.0, "headroom_db": 6, "dynamics": "wide"},
    "trap":     {"lufs": -7, "true_peak": -1.0, "headroom_db": 5, "dynamics": "medium"},
    "phonk":    {"lufs": -6, "true_peak": -0.3, "headroom_db": 4, "dynamics": "tight"},
    "neutral":  {"lufs": -9, "true_peak": -1.0, "headroom_db": 6, "dynamics": "medium"},
}


def get_genre_target(genre: str) -> dict:
    """Return a copy of the target for `genre`, or neutral if unknown."""
    return dict(GENRE_TARGETS.get(genre, GENRE_TARGETS["neutral"]))


_FX_HEAVY_THRESHOLD = 4   # strictly more than this many FX
_UNITY_VOL = 1.0          # FL fader: 1.0 == 0dB


def analyze_static(snapshot: dict) -> dict:
    """Evaluate a mixer snapshot without peak data. Returns a report dict."""
    tracks_in = snapshot.get("tracks", [])
    flagged_tracks = []
    global_flags = []

    for t in tracks_in:
        idx = t.get("idx", -1)
        name = t.get("name", f"Track {idx}")
        vol = t.get("vol", 0.0)
        mute = t.get("mute", False)
        fx = t.get("fx", [])
        flags = []

        if idx == 0:  # master
            if vol > _UNITY_VOL:
                global_flags.append("master-clipping-risk")
            continue  # master not evaluated for per-track flags below

        if len(fx) > _FX_HEAVY_THRESHOLD:
            flags.append("fx-heavy")
        if vol == 0.0 and not mute:
            flags.append("silent-active")

        if flags:
            flagged_tracks.append({"idx": idx, "name": name, "flags": flags})

    return {
        "kind": "static",
        "track_count": len(tracks_in),
        "tracks": flagged_tracks,
        "global_flags": global_flags,
    }
