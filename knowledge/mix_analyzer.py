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
