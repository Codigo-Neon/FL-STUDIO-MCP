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


_NEAR_CLIP_DB = -3.0   # any channel peak above this is "near clipping"


def analyze_peaks(peak_report: dict, target: dict) -> dict:
    """Evaluate accumulated max-hold peaks. Returns a report dict."""
    sample_count = peak_report.get("sample_count", 0)
    tracks_in = peak_report.get("tracks", [])
    flagged_tracks = []
    global_flags = []

    if sample_count == 0:
        global_flags.append("no-peak-data")

    for t in tracks_in:
        idx = t.get("idx", -1)
        if idx == 0:
            continue  # master handled in score_master
        L = t.get("L", -90.0)
        R = t.get("R", -90.0)
        flags = []
        if max(L, R) > _NEAR_CLIP_DB:
            flags.append("near-clip")
        if flags:
            flagged_tracks.append({"idx": idx, "L": L, "R": R, "flags": flags})

    return {
        "kind": "peaks",
        "sample_count": sample_count,
        "tracks": flagged_tracks,
        "global_flags": global_flags,
    }


_STEREO_IMBALANCE_DB = 3.0


def _find_track(tracks: list, idx: int) -> dict:
    for t in tracks:
        if t.get("idx") == idx:
            return t
    return {}


def score_master(master_snap: dict, peaks: dict, target: dict) -> dict:
    """Cross-reference master peaks against the mastering target."""
    flags = []
    sample_count = peaks.get("sample_count", 0)
    master_peak = _find_track(peaks.get("tracks", []), 0)

    tp_target = target.get("true_peak", -1.0)
    L = master_peak.get("L", -90.0)
    R = master_peak.get("R", -90.0)

    report = {
        "kind": "master",
        "fx": master_snap.get("fx", []),
        "true_peak_target": tp_target,
        "master_L": L,
        "master_R": R,
        "L_excess_db": max(0.0, L - tp_target),
        "R_excess_db": max(0.0, R - tp_target),
        "lufs": "not_available",
        "headroom_db": target.get("headroom_db"),
        "flags": flags,
    }

    if sample_count == 0:
        flags.append("no-peak-data")
        return report

    if report["L_excess_db"] > 0 or report["R_excess_db"] > 0:
        flags.append("over-target")
    if abs(L - R) > _STEREO_IMBALANCE_DB:
        flags.append("stereo-imbalance")

    return report


def suggest_fixes(static_report: dict, master_report: dict, target: dict) -> list:
    """Turn flags into concrete Spanish suggestions."""
    fixes = []

    for flag in static_report.get("global_flags", []):
        if flag == "master-clipping-risk":
            fixes.append("Master fader por encima de 0dB: bajalo a unity para evitar clipping de salida.")

    for t in static_report.get("tracks", []):
        name = t.get("name", f"Track {t.get('idx')}")
        if "fx-heavy" in t.get("flags", []):
            fixes.append(f"{name}: más de 4 FX cargados. Revisá la cadena y consolidá efectos redundantes.")
        if "silent-active" in t.get("flags", []):
            fixes.append(f"{name}: volumen en 0 pero sin mutear. Muteá o subí el fader.")

    for t in static_report.get("tracks", []):
        if "near-clip" in t.get("flags", []):
            fixes.append(f"{t.get('name', t.get('idx'))}: peak por encima de -3dB, cerca de clip. Bajá ganancia.")

    if "over-target" in master_report.get("flags", []):
        lx = master_report.get("L_excess_db", 0.0)
        rx = master_report.get("R_excess_db", 0.0)
        excess = max(lx, rx)
        fixes.append(
            f"Master excede el true peak target por {excess:.1f}dB. "
            f"Bajá el output del limiter {excess:.1f}dB o ajustá el ceiling a {master_report.get('true_peak_target')}dB."
        )
    if "stereo-imbalance" in master_report.get("flags", []):
        fixes.append("Desbalance L/R en el master mayor a 3dB. Revisá paneos y mono compatibility.")

    return fixes


def format_report_es(report: dict, fixes: list = None) -> str:
    """Render a report dict as a Spanish text report."""
    fixes = fixes or []
    lines = []
    kind = report.get("kind")

    if kind == "static":
        lines.append(f"Análisis estático — {report.get('track_count', 0)} tracks.")
        for flag in report.get("global_flags", []):
            lines.append(f"  ⚠ {flag}")
        for t in report.get("tracks", []):
            lines.append(f"  • {t.get('name')}: {', '.join(t.get('flags', []))}")
        if not report.get("tracks") and not report.get("global_flags"):
            lines.append("  Sin problemas detectados.")

    elif kind == "master":
        if "no-peak-data" in report.get("flags", []):
            lines.append("⚠ Sin datos de peak. Corré start_peak_monitoring(), reproducí el track, "
                         "stop_peak_monitoring() y volvé a analizar.")
        else:
            lines.append(f"Master peak L: {report.get('master_L', -90.0):.1f}dB, "
                         f"R: {report.get('master_R', -90.0):.1f}dB "
                         f"(target true peak {report.get('true_peak_target')}dB).")
            for flag in report.get("flags", []):
                lines.append(f"  ⚠ {flag}")
        lines.append("LUFS: no disponible vía FL Script API — medición de true peak con max-hold.")

    if fixes:
        lines.append("")
        lines.append("Sugerencias:")
        for f in fixes:
            lines.append(f"  → {f}")

    return "\n".join(lines)
