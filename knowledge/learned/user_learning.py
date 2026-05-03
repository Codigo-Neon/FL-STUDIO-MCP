"""Sistema de aprendizaje del usuario para FL MCP.

Guarda patrones exitosos, preferencias y historial para que el MCP
mejore sus sugerencias con el uso. Los datos se persisten en archivos JSON.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# Directorio de datos persistentes
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

PATTERNS_FILE = os.path.join(DATA_DIR, "user_patterns.json")
PREFERENCES_FILE = os.path.join(DATA_DIR, "user_preferences.json")
SESSION_FILE = os.path.join(DATA_DIR, "session_history.json")


# ============================================================================
# CARGA / GUARDADO
# ============================================================================

def _load_json(filepath: str) -> dict:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def _save_json(filepath: str, data: dict):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# PATRONES EXITOSOS
# ============================================================================

def save_pattern(
    pattern_type: str,
    name: str,
    data: dict,
    genre: str = "",
    key: str = "",
    bpm: float = 0,
    rating: int = 5,
    notes: str = "",
) -> str:
    """Guarda un patrón que funcionó bien.

    Args:
        pattern_type: 'bassline', 'melody', 'drums', 'chord_progression'
        name: Nombre descriptivo del patrón
        data: Datos del patrón (notas MIDI, progresión, etc.)
        genre: Género musical
        key: Tonalidad (ej: 'D#', 'A')
        bpm: Tempo
        rating: Calificación 1-5 del usuario
        notes: Notas adicionales del usuario
    """
    patterns = _load_json(PATTERNS_FILE)

    if pattern_type not in patterns:
        patterns[pattern_type] = []

    entry = {
        "name": name,
        "data": data,
        "genre": genre,
        "key": key,
        "bpm": bpm,
        "rating": rating,
        "notes": notes,
        "date": datetime.now().isoformat(),
    }

    patterns[pattern_type].append(entry)
    _save_json(PATTERNS_FILE, patterns)

    return f"Patrón '{name}' ({pattern_type}) guardado con rating {rating}/5"


def get_patterns(
    pattern_type: str = "",
    genre: str = "",
    min_rating: int = 1,
) -> List[dict]:
    """Recupera patrones guardados, filtrados opcionalmente."""
    patterns = _load_json(PATTERNS_FILE)
    results = []

    types_to_search = [pattern_type] if pattern_type else patterns.keys()

    for ptype in types_to_search:
        for entry in patterns.get(ptype, []):
            if genre and entry.get("genre") != genre:
                continue
            if entry.get("rating", 0) < min_rating:
                continue
            entry["type"] = ptype
            results.append(entry)

    results.sort(key=lambda x: x.get("rating", 0), reverse=True)
    return results


def get_best_patterns(pattern_type: str = "", genre: str = "", limit: int = 5) -> str:
    """Devuelve los mejores patrones guardados formateados."""
    patterns = get_patterns(pattern_type, genre, min_rating=4)[:limit]

    if not patterns:
        return "No hay patrones guardados todavía. Usá save_pattern() cuando algo te guste."

    lines = ["## Mejores patrones guardados\n"]
    for p in patterns:
        lines.append(f"**{p['name']}** ({p['type']}) — {p.get('genre', '?')} @ {p.get('bpm', '?')} BPM")
        lines.append(f"  Rating: {'★' * p.get('rating', 0)} | Key: {p.get('key', '?')}")
        if p.get("notes"):
            lines.append(f"  Notas: {p['notes']}")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# PREFERENCIAS DEL USUARIO
# ============================================================================

def save_preference(category: str, key: str, value) -> str:
    """Guarda una preferencia del usuario.

    Categorías: 'scales', 'progressions', 'bass_styles', 'drum_patterns',
                'plugins', 'mixing', 'bpm_ranges', 'keys', 'general'
    """
    prefs = _load_json(PREFERENCES_FILE)

    if category not in prefs:
        prefs[category] = {}

    prefs[category][key] = {
        "value": value,
        "updated": datetime.now().isoformat(),
    }

    _save_json(PREFERENCES_FILE, prefs)
    return f"Preferencia guardada: {category}/{key} = {value}"


def get_preference(category: str, key: str = "") -> Optional[dict]:
    """Recupera preferencias del usuario."""
    prefs = _load_json(PREFERENCES_FILE)

    if category not in prefs:
        return None

    if key:
        return prefs[category].get(key, {}).get("value")

    return {k: v["value"] for k, v in prefs[category].items()}


def get_all_preferences() -> str:
    """Devuelve todas las preferencias formateadas."""
    prefs = _load_json(PREFERENCES_FILE)

    if not prefs:
        return "No hay preferencias guardadas todavía."

    lines = ["## Preferencias del usuario\n"]
    for category, items in prefs.items():
        lines.append(f"### {category.replace('_', ' ').title()}")
        for key, data in items.items():
            lines.append(f"  - **{key}**: {data['value']}")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# HISTORIAL DE SESIÓN
# ============================================================================

def log_tool_use(tool_name: str, params: dict = None, liked: bool = True):
    """Registra el uso de un tool para tracking de preferencias."""
    history = _load_json(SESSION_FILE)

    if "tool_usage" not in history:
        history["tool_usage"] = {}

    if tool_name not in history["tool_usage"]:
        history["tool_usage"][tool_name] = {"count": 0, "liked": 0, "disliked": 0}

    history["tool_usage"][tool_name]["count"] += 1
    if liked:
        history["tool_usage"][tool_name]["liked"] += 1
    else:
        history["tool_usage"][tool_name]["disliked"] += 1

    # Guardar último uso
    history["tool_usage"][tool_name]["last_used"] = datetime.now().isoformat()
    if params:
        history["tool_usage"][tool_name]["last_params"] = params

    _save_json(SESSION_FILE, history)


def get_tool_stats() -> str:
    """Devuelve estadísticas de uso de tools."""
    history = _load_json(SESSION_FILE)
    usage = history.get("tool_usage", {})

    if not usage:
        return "No hay historial de uso todavía."

    lines = ["## Estadísticas de uso\n"]
    sorted_tools = sorted(usage.items(), key=lambda x: x[1]["count"], reverse=True)

    for tool, stats in sorted_tools:
        total = stats["count"]
        liked = stats.get("liked", 0)
        pct = int((liked / total) * 100) if total > 0 else 0
        lines.append(f"  - **{tool}**: {total} usos ({pct}% exitosos)")

    return "\n".join(lines)


# ============================================================================
# MIDI ANALYSIS
# ============================================================================

def analyze_midi_file(filepath: str) -> str:
    """Analiza un archivo MIDI y devuelve info musical."""
    try:
        import mido
    except ImportError:
        return "Error: mido no instalado"

    if not os.path.exists(filepath):
        return f"Archivo no encontrado: {filepath}"

    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat

    notes = []
    for track in mid.tracks:
        abs_tick = 0
        for msg in track:
            abs_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                notes.append({
                    "note": msg.note,
                    "velocity": msg.velocity,
                    "tick": abs_tick,
                    "beat": abs_tick / tpb,
                })

    if not notes:
        return "No se encontraron notas en el archivo."

    # Análisis
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    pitch_classes = [n["note"] % 12 for n in notes]
    unique_pitches = set(pitch_classes)
    pitch_counts = {pc: pitch_classes.count(pc) for pc in unique_pitches}

    # Detectar tonalidad probable (la nota más frecuente como root)
    root_pc = max(pitch_counts, key=pitch_counts.get)
    root_name = note_names[root_pc]

    # Detectar escala
    intervals = sorted([(pc - root_pc) % 12 for pc in unique_pitches])
    minor_natural = [0, 2, 3, 5, 7, 8, 10]
    major = [0, 2, 4, 5, 7, 9, 11]
    pentatonic_minor = [0, 3, 5, 7, 10]
    blues = [0, 3, 5, 6, 7, 10]

    scale_match = "desconocida"
    if set(intervals).issubset(set(minor_natural)):
        scale_match = "menor natural"
    elif set(intervals).issubset(set(major)):
        scale_match = "mayor"
    elif set(intervals).issubset(set(pentatonic_minor)):
        scale_match = "pentatónica menor"
    elif set(intervals).issubset(set(blues)):
        scale_match = "blues"

    # Rango
    min_note = min(n["note"] for n in notes)
    max_note = max(n["note"] for n in notes)
    min_name = f"{note_names[min_note % 12]}{min_note // 12 - 1}"
    max_name = f"{note_names[max_note % 12]}{max_note // 12 - 1}"

    # Duración
    total_beats = notes[-1]["beat"]
    total_bars = total_beats / 4

    # Velocidad promedio
    avg_vel = sum(n["velocity"] for n in notes) / len(notes)

    lines = [
        f"## Análisis MIDI: {os.path.basename(filepath)}\n",
        f"- **Tonalidad probable**: {root_name} {scale_match}",
        f"- **Notas usadas**: {', '.join(note_names[pc] for pc in sorted(unique_pitches))}",
        f"- **Intervalos**: {intervals}",
        f"- **Rango**: {min_name} → {max_name} (MIDI {min_note}-{max_note})",
        f"- **Total notas**: {len(notes)}",
        f"- **Duración**: {total_beats:.1f} beats ({total_bars:.1f} compases)",
        f"- **Velocidad promedio**: {avg_vel:.0f}",
        f"- **Ticks per beat**: {tpb}",
    ]

    return "\n".join(lines)


def format_learned_context(genre: str = "") -> str:
    """Genera un resumen del contexto aprendido para informar decisiones."""
    parts = []

    # Mejores patrones
    best = get_best_patterns(genre=genre, limit=3)
    if "No hay" not in best:
        parts.append(best)

    # Preferencias
    prefs = get_all_preferences()
    if "No hay" not in prefs:
        parts.append(prefs)

    # Stats
    stats = get_tool_stats()
    if "No hay" not in stats:
        parts.append(stats)

    if not parts:
        return "Sin datos de aprendizaje todavía. El sistema aprende con el uso."

    return "\n\n".join(parts)
