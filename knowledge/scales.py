"""Scale definitions, descriptions, and helper functions for FL Studio MCP."""

from typing import List, Dict
from .constants import NOTE_NAMES, note_to_midi, SEMITONE_TO_NAME

# Intervals in semitones from root
SCALE_INTERVALS = {
    "minor_natural": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "pentatonic_major": [0, 2, 4, 7, 9],
}

SCALE_DESCRIPTIONS = {
    "minor_natural": {
        "name": "Menor Natural (Eolica)",
        "description": "La REINA del boom bap. Melancolica, oscura. La base de todo el hip-hop de los 90s.",
        "formula": "T-S-T-T-S-T-T",
        "mood": "dark, melancholic",
        "reference_tracks": ["Illmatic (Nas)", "The Infamous (Mobb Deep)", "Liquid Swords (GZA)"],
        "example_in_A": "A - B - C - D - E - F - G (teclas blancas)",
    },
    "pentatonic_minor": {
        "name": "Pentatonica Menor",
        "description": "5 notas, simple pero poderosa. Imposible que suene mal. Ideal para empezar.",
        "formula": "T+S-T-T-T+S-T",
        "mood": "dark, simple, powerful",
        "reference_tracks": ["DJ Premier (Gang Starr)", "Pete Rock classics"],
        "example_in_A": "A - C - D - E - G",
    },
    "blues": {
        "name": "Blues",
        "description": "Pentatonica menor + blue note (b5). Tension especial. El alma del hip-hop.",
        "formula": "T+S-T-S-S-T+S-T",
        "mood": "soulful, gritty, tension",
        "reference_tracks": ["Gang Starr", "Wu-Tang Clan"],
        "example_in_A": "A - C - D - D#/Eb - E - G",
    },
    "dorian": {
        "name": "Dorica",
        "description": "Menor con 6ta mayor. Toque jazz sofisticado. Esperanza dentro de la melancolia.",
        "formula": "T-S-T-T-T-S-T",
        "mood": "jazzy, hopeful, sophisticated",
        "reference_tracks": ["A Tribe Called Quest", "Pete Rock", "J Dilla"],
        "example_in_A": "A - B - C - D - E - F# - G",
    },
    "harmonic_minor": {
        "name": "Menor Armonica",
        "description": "Dramatica, cinematica. El intervalo de tono y medio crea tension unica.",
        "formula": "T-S-T-T-S-T+S-S",
        "mood": "dramatic, cinematic, dark",
        "reference_tracks": ["RZA (Wu-Tang)", "Havoc 'Shook Ones Pt. II'"],
        "example_in_A": "A - B - C - D - E - F - G#",
    },
    "phrygian": {
        "name": "Frigia",
        "description": "La MAS oscura y agresiva. El semitono inicial crea tension inmediata.",
        "formula": "S-T-T-T-S-T-T",
        "mood": "aggressive, darkest, tension",
        "reference_tracks": ["DJ Muggs (Cypress Hill)", "Alchemist"],
        "example_in_A": "A - Bb - C - D - E - F - G",
    },
    "major": {
        "name": "Mayor",
        "description": "Brillante, alegre. Poco comun en boom bap pero usada en neo-soul y jazz hip-hop.",
        "formula": "T-T-S-T-T-T-S",
        "mood": "bright, happy, uplifting",
        "reference_tracks": ["Nujabes", "Robert Glasper"],
        "example_in_A": "A - B - C# - D - E - F# - G#",
    },
    "pentatonic_major": {
        "name": "Pentatonica Mayor",
        "description": "5 notas brillantes. Usada en samples de soul y gospel.",
        "formula": "T-T-T+S-T-T+S",
        "mood": "bright, soulful",
        "reference_tracks": ["9th Wonder (soul samples)", "Kanye (soul era)"],
        "example_in_A": "A - B - C# - E - F#",
    },
}

# Which scales work best for each genre
GENRE_SCALE_RECOMMENDATIONS = {
    "boom_bap": ["minor_natural", "pentatonic_minor", "blues", "dorian"],
    "trap": ["minor_natural", "phrygian", "harmonic_minor", "pentatonic_minor"],
    "jazz_hiphop": ["dorian", "minor_natural", "pentatonic_minor", "major"],
    "phonk": ["phrygian", "harmonic_minor", "minor_natural"],
    "lofi": ["dorian", "pentatonic_minor", "minor_natural", "pentatonic_major"],
    "reggaeton": ["minor_natural", "major", "pentatonic_minor"],
    "uk_drill": ["minor_natural", "phrygian", "harmonic_minor"],
}

# Mood to scale mapping
MOOD_SCALE_MAP = {
    "dark": ["minor_natural", "phrygian", "harmonic_minor"],
    "melancholic": ["minor_natural", "dorian", "pentatonic_minor"],
    "aggressive": ["phrygian", "harmonic_minor", "blues"],
    "jazzy": ["dorian", "pentatonic_minor", "blues"],
    "hopeful": ["dorian", "major", "pentatonic_major"],
    "cinematic": ["harmonic_minor", "phrygian", "minor_natural"],
    "soulful": ["pentatonic_minor", "blues", "dorian"],
}

# Common keys per genre
COMMON_KEYS = {
    "boom_bap": ["Am", "Cm", "Dm", "Em", "Gm", "Fm"],
    "trap": ["Cm", "Am", "Em", "Dm", "Gm"],
    "jazz_hiphop": ["Dm", "Am", "Gm", "Cm"],
    "phonk": ["Am", "Em", "Cm"],
    "lofi": ["Am", "Dm", "Em", "Cm"],
}


def get_scale_notes(root: str, scale_type: str, octave: int = 4) -> List[int]:
    """Return MIDI note numbers for one octave of a scale.

    Args:
        root: Root note name (e.g. "A", "C", "D#")
        scale_type: Scale type key from SCALE_INTERVALS
        octave: Starting octave (default 4, where C4=60)

    Returns:
        List of MIDI note numbers for the scale in one octave
    """
    if scale_type not in SCALE_INTERVALS:
        raise ValueError(f"Unknown scale: {scale_type}. Available: {list(SCALE_INTERVALS.keys())}")

    root_midi = note_to_midi(root, octave)
    return [root_midi + interval for interval in SCALE_INTERVALS[scale_type]]


def get_scale_notes_range(root: str, scale_type: str,
                          low_octave: int = 3, high_octave: int = 5) -> List[int]:
    """Return all MIDI notes in a scale across multiple octaves.

    Args:
        root: Root note name
        scale_type: Scale type key
        low_octave: Lowest octave to include
        high_octave: Highest octave to include

    Returns:
        Sorted list of MIDI note numbers across the octave range
    """
    notes = []
    for octave in range(low_octave, high_octave + 1):
        notes.extend(get_scale_notes(root, scale_type, octave))
    return sorted([n for n in notes if 0 <= n <= 127])


def format_scale_info(root: str, scale_type: str) -> str:
    """Format scale information as a readable string."""
    if scale_type not in SCALE_DESCRIPTIONS:
        return f"Unknown scale: {scale_type}"

    info = SCALE_DESCRIPTIONS[scale_type]
    notes = get_scale_notes(root, scale_type, 4)
    note_names = [f"{SEMITONE_TO_NAME[n % 12]}{n // 12 - 1}" for n in notes]

    lines = [
        f"=== {info['name']} en {root} ===",
        f"Descripcion: {info['description']}",
        f"Formula: {info['formula']}",
        f"Mood: {info['mood']}",
        f"Notas: {' - '.join(note_names)}",
        f"MIDI: {notes}",
        f"Referencia: {', '.join(info['reference_tracks'])}",
    ]
    return "\n".join(lines)
