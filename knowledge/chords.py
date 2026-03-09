"""Chord progressions, voicings, and generation helpers for FL Studio MCP."""

from typing import List, Dict, Tuple, Optional
from .constants import NOTE_NAMES, note_to_midi


# Chord quality intervals (semitones from root)
CHORD_TYPES = {
    "major":  [0, 4, 7],
    "minor":  [0, 3, 7],
    "dim":    [0, 3, 6],
    "aug":    [0, 4, 8],
    "maj7":   [0, 4, 7, 11],
    "min7":   [0, 3, 7, 10],
    "dom7":   [0, 4, 7, 10],
    "dim7":   [0, 3, 6, 9],
    "min9":   [0, 3, 7, 10, 14],
    "maj9":   [0, 4, 7, 11, 14],
    "sus2":   [0, 2, 7],
    "sus4":   [0, 5, 7],
}


def build_chord(root: str, quality: str, octave: int = 3) -> List[int]:
    """Build a chord from root note, quality and octave.

    Args:
        root: Root note name (e.g. "A", "C#", "Bb")
        quality: Chord quality from CHORD_TYPES
        octave: Base octave

    Returns:
        List of MIDI note numbers
    """
    root_midi = note_to_midi(root, octave)
    intervals = CHORD_TYPES.get(quality, CHORD_TYPES["major"])
    return [root_midi + i for i in intervals]


# ============================================================================
# CHORD PROGRESSIONS - From GUIA_BOOM_BAP_90s_COMPLETA.txt
# ============================================================================
# Each progression stores interval patterns from the root of the key
# so it can be transposed to ANY key.

# Progression definition: list of (root_interval_from_key, chord_quality)
# Root intervals are relative to the key's root note
PROGRESSION_DEFINITIONS = {
    "classic_dark": {
        "name": "Clasica Oscura",
        "numerals": "i - bVII - bVI - V",
        "description": "Dark, dramatica. LA clasica del boom bap. Tension constante.",
        "genre_tags": ["boom_bap", "trap"],
        "mood": "dark",
        "reference_tracks": ["Shook Ones Pt. II (Mobb Deep)", "NY State of Mind (Nas)"],
        "chords": [
            (0, "minor"),   # i
            (10, "major"),  # bVII
            (8, "major"),   # bVI
            (7, "major"),   # V (con 3ra mayor para dominante)
        ],
    },
    "jazz_hiphop": {
        "name": "Jazz Hip-Hop",
        "numerals": "i - iv - i - v",
        "description": "Movimiento jazz. Ida y vuelta entre tonica y subdominante.",
        "genre_tags": ["boom_bap", "jazz_hiphop"],
        "mood": "jazzy",
        "reference_tracks": ["Pete Rock (T.R.O.Y.)", "A Tribe Called Quest"],
        "chords": [
            (0, "minor"),  # i
            (5, "minor"),  # iv
            (0, "minor"),  # i
            (7, "minor"),  # v
        ],
    },
    "soul_feel": {
        "name": "Soul Sample Feel",
        "numerals": "i - bVI - bIII - bVII",
        "description": "Sensacion de sample de soul. Movimiento circular descendente.",
        "genre_tags": ["boom_bap", "lofi"],
        "mood": "soulful",
        "reference_tracks": ["9th Wonder", "J Dilla"],
        "chords": [
            (0, "minor"),   # i
            (8, "major"),   # bVI
            (3, "major"),   # bIII
            (10, "major"),  # bVII
        ],
    },
    "melancholic": {
        "name": "Melancolica",
        "numerals": "i - bVII - iv - bVI",
        "description": "Melancolica profunda. Descenso emocional constante.",
        "genre_tags": ["boom_bap", "trap", "lofi"],
        "mood": "melancholic",
        "reference_tracks": ["Nas 'One Mic'", "Eminem 'Lose Yourself'"],
        "chords": [
            (0, "minor"),   # i
            (10, "major"),  # bVII
            (5, "minor"),   # iv
            (8, "major"),   # bVI
        ],
    },
    "minimal_jazz": {
        "name": "Loop Minimo Jazz",
        "numerals": "im7 - iv7",
        "description": "Solo 2 acordes con 7mas. Loop hipnotico estilo Dilla/Madlib.",
        "genre_tags": ["boom_bap", "jazz_hiphop", "lofi"],
        "mood": "jazzy",
        "reference_tracks": ["J Dilla 'Donuts'", "Madlib 'Madvillainy'"],
        "chords": [
            (0, "min7"),  # im7
            (5, "min7"),  # iv7
        ],
    },
    "phrygian_dark": {
        "name": "Frigia / Oscura",
        "numerals": "i - bII - i - bII",
        "description": "Movimiento de semitono = tension constante. La mas oscura.",
        "genre_tags": ["boom_bap", "trap", "phonk"],
        "mood": "aggressive",
        "reference_tracks": ["Wu-Tang 'C.R.E.A.M.'", "Cypress Hill"],
        "chords": [
            (0, "minor"),  # i
            (1, "major"),  # bII
            (0, "minor"),  # i
            (1, "major"),  # bII
        ],
    },
    "neo_soul": {
        "name": "Jazzy Neo Soul",
        "numerals": "im9 - IVmaj7",
        "description": "Voicings abiertos, sofisticado. Sonido Nujabes/Robert Glasper.",
        "genre_tags": ["jazz_hiphop", "lofi"],
        "mood": "hopeful",
        "reference_tracks": ["Nujabes", "Robert Glasper"],
        "chords": [
            (0, "min9"),   # im9
            (5, "maj7"),   # IVmaj7
        ],
    },
}


def get_progression_chords(progression_id: str, key: str,
                           octave: int = 3) -> List[Dict]:
    """Get chord voicings for a progression in a specific key.

    Args:
        progression_id: Key from PROGRESSION_DEFINITIONS
        key: Root note of the key (e.g. "A", "C", "D")
        octave: Base octave for voicings

    Returns:
        List of dicts with chord name, notes (MIDI), and interval info
    """
    if progression_id not in PROGRESSION_DEFINITIONS:
        raise ValueError(f"Unknown progression: {progression_id}. "
                         f"Available: {list(PROGRESSION_DEFINITIONS.keys())}")

    prog = PROGRESSION_DEFINITIONS[progression_id]
    key_root = NOTE_NAMES[key]
    result = []

    for interval, quality in prog["chords"]:
        chord_root_semitone = (key_root + interval) % 12
        # Find the note name for this semitone
        from .constants import SEMITONE_TO_NAME
        chord_root_name = SEMITONE_TO_NAME[chord_root_semitone]
        midi_notes = build_chord(chord_root_name, quality, octave)
        quality_label = quality.replace("min", "m").replace("maj", "M").replace("dom", "")
        if quality == "major":
            quality_label = ""
        elif quality == "minor":
            quality_label = "m"

        result.append({
            "name": f"{chord_root_name}{quality_label}",
            "root": chord_root_name,
            "quality": quality,
            "midi_notes": midi_notes,
            "interval_from_key": interval,
        })

    return result


def progression_to_midi_notes(progression_id: str, key: str,
                               bars: int = 4, beats_per_chord: float = 4.0,
                               velocity: int = 85, octave: int = 3) -> str:
    """Convert a chord progression to send_melody() compatible note data string.

    Args:
        progression_id: Progression key
        key: Musical key root
        bars: Total number of bars to fill
        beats_per_chord: Duration of each chord in beats
        velocity: MIDI velocity for all notes
        octave: Base octave

    Returns:
        String in format "note,velocity,length,position" per line
    """
    chords = get_progression_chords(progression_id, key, octave)
    total_beats = bars * 4  # 4/4 time
    lines = []
    position = 0.0

    while position < total_beats:
        chord_index = int(position / beats_per_chord) % len(chords)
        chord = chords[chord_index]

        for midi_note in chord["midi_notes"]:
            length = min(beats_per_chord, total_beats - position)
            lines.append(f"{midi_note},{velocity},{length},{position}")

        position += beats_per_chord

    return "\n".join(lines)


def format_progression_info(progression_id: str, key: str = "A") -> str:
    """Format progression information as a readable string."""
    if progression_id not in PROGRESSION_DEFINITIONS:
        return f"Unknown progression: {progression_id}"

    prog = PROGRESSION_DEFINITIONS[progression_id]
    chords = get_progression_chords(progression_id, key, 3)
    chord_names = [c["name"] for c in chords]

    lines = [
        f"=== {prog['name']} ({prog['numerals']}) en {key}m ===",
        f"Descripcion: {prog['description']}",
        f"Acordes: {' - '.join(chord_names)}",
        f"Generos: {', '.join(prog['genre_tags'])}",
        f"Mood: {prog['mood']}",
        f"Referencia: {', '.join(prog['reference_tracks'])}",
        "",
        "Voicings MIDI:",
    ]
    for c in chords:
        lines.append(f"  {c['name']}: {c['midi_notes']}")

    return "\n".join(lines)


def list_progressions(genre: str = "") -> str:
    """List all available progressions, optionally filtered by genre."""
    lines = ["=== PROGRESIONES DE ACORDES DISPONIBLES ===\n"]

    for prog_id, prog in PROGRESSION_DEFINITIONS.items():
        if genre and genre not in prog["genre_tags"]:
            continue
        lines.append(f"ID: {prog_id}")
        lines.append(f"  Nombre: {prog['name']}")
        lines.append(f"  Numeros: {prog['numerals']}")
        lines.append(f"  Descripcion: {prog['description']}")
        lines.append(f"  Generos: {', '.join(prog['genre_tags'])}")
        lines.append(f"  Referencia: {', '.join(prog['reference_tracks'])}")
        lines.append("")

    return "\n".join(lines)
