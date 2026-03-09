"""Drum patterns with exact step/velocity data from GUIA_BOOM_BAP_90s_COMPLETA.txt."""

from typing import List, Dict, Tuple, Optional
from .constants import DRUM_MIDI_MAP, DrumPiece
import random


# Velocity reference guide
VELOCITY_GUIDE = {
    "kick": {
        "main": (100, 110),
        "secondary": (80, 95),
        "ghost": (50, 65),
    },
    "snare": {
        "backbeat": (100, 127),
        "ghost": (30, 50),
        "fill": (70, 90),
    },
    "hihat": {
        "downbeat": (85, 100),
        "offbeat": (55, 75),
        "ghost": (30, 45),
    },
}

# Swing values reference
SWING_VALUES = {
    "none": 50,
    "subtle": 55,           # Havoc, Alchemist
    "standard": 60,         # THE boom bap standard (Premier, Pete Rock)
    "strong_jazz": 65,      # Pete Rock jazzy, ATCQ
    "extreme_dilla": 72,    # J Dilla "drunk" feel
}

SWING_DESCRIPTIONS = {
    "none": "50% - Sin swing, recto, robotico",
    "subtle": "54-57% - Sutil (Havoc, Alchemist). Apenas perceptible pero anade vida",
    "standard": "58-62% - EL ESTANDAR BOOM BAP (Premier, Pete Rock, Large Professor). Si solo vas a usar un valor, usa 60%",
    "strong_jazz": "64-68% - Fuerte/jazz (Pete Rock jazzy, Tribe Called Quest)",
    "extreme_dilla": "70%+ - Extremo/Dilla. Suena 'borracho'. Muy dificil de hacer bien",
}


# ============================================================================
# DRUM PATTERNS
# ============================================================================
# Each hit: (step 1-16, piece, velocity)
# Steps are 1-indexed sixteenth notes within a bar

PATTERNS = {
    "boom_bap_basic": {
        "name": "Boom Bap Basico",
        "style": "Gang Starr / Mobb Deep fundamental",
        "description": "El patron fundamental. Kick en 1,11,13; Snare en 5,13; Hat en corcheas.",
        "reference_tracks": ["Gang Starr", "Mobb Deep"],
        "bpm_range": (85, 95),
        "swing": "standard",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap"],
        "hits": [
            # Kicks
            (1, "kick", 105), (11, "kick", 90), (13, "kick", 95),
            # Snare backbeat
            (5, "snare", 120), (13, "snare", 115),
            # Hi-hat 8th notes with velocity alternation
            (1, "closed_hat", 90), (3, "closed_hat", 55),
            (5, "closed_hat", 85), (7, "closed_hat", 60),
            (9, "closed_hat", 90), (11, "closed_hat", 55),
            (13, "closed_hat", 85), (15, "closed_hat", 60),
        ],
    },

    "premier_style": {
        "name": "Premier Style",
        "style": "DJ Premier bounce",
        "description": "El kick en step 8 (la 'y' del beat 2) es EL sello de Premier. Hi-hat alternando velocities.",
        "reference_tracks": ["Gang Starr 'Mass Appeal'", "Nas 'N.Y. State of Mind'"],
        "bpm_range": (88, 96),
        "swing": "standard",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap"],
        "hits": [
            # Kicks - step 8 is the Premier signature
            (1, "kick", 105), (8, "kick", 95), (11, "kick", 90),
            # Snare
            (5, "snare", 120), (13, "snare", 115),
            # Hi-hat alternating: odd=soft, even=hard
            (1, "closed_hat", 55), (3, "closed_hat", 100),
            (5, "closed_hat", 55), (7, "closed_hat", 100),
            (9, "closed_hat", 55), (11, "closed_hat", 100),
            (13, "closed_hat", 55), (15, "closed_hat", 100),
            # Open hat at end for transition
            (16, "open_hat", 85),
        ],
    },

    "pete_rock_groove": {
        "name": "Pete Rock Groove",
        "style": "Jazz-influenced swing",
        "description": "Kick en 1,7,12: groove tipo jazz. NECESITA swing 55-60% para sonar bien. Ride sutil.",
        "reference_tracks": ["T.R.O.Y. (They Reminisce Over You)"],
        "bpm_range": (85, 93),
        "swing": "strong_jazz",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap", "jazz_hiphop"],
        "hits": [
            # Kicks - jazz placement
            (1, "kick", 105), (7, "kick", 90), (12, "kick", 85),
            # Snare
            (5, "snare", 120), (13, "snare", 115),
            # Hi-hat with strong/weak alternation
            (1, "closed_hat", 90), (3, "closed_hat", 55),
            (5, "closed_hat", 85), (7, "closed_hat", 60),
            (9, "closed_hat", 90), (11, "closed_hat", 55),
            (13, "closed_hat", 85), (15, "closed_hat", 60),
            # Ride on offbeats (step 8, 16) - jazz flavor
            (8, "ride", 60), (16, "ride", 55),
        ],
    },

    "havoc_minimal": {
        "name": "Havoc / Mobb Deep",
        "style": "Minimalista oscuro",
        "description": "Kick SOLO en 1 y 9: MINIMALISTA. Hi-hat en CADA step (semicorcheas). El espacio vacio es tan importante como los golpes.",
        "reference_tracks": ["Shook Ones Pt. II", "Survival of the Fittest"],
        "bpm_range": (88, 95),
        "swing": "subtle",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap"],
        "hits": [
            # Kicks - minimal
            (1, "kick", 110), (9, "kick", 100),
            # Snare
            (5, "snare", 125), (13, "snare", 120),
            # Hi-hat on EVERY 16th note with velocity variation
            (1, "closed_hat", 100), (2, "closed_hat", 50),
            (3, "closed_hat", 65), (4, "closed_hat", 45),
            (5, "closed_hat", 95), (6, "closed_hat", 50),
            (7, "closed_hat", 65), (8, "closed_hat", 45),
            (9, "closed_hat", 100), (10, "closed_hat", 50),
            (11, "closed_hat", 65), (12, "closed_hat", 45),
            (13, "closed_hat", 95), (14, "closed_hat", 50),
            (15, "closed_hat", 65), (16, "closed_hat", 45),
            # Perc accent
            (12, "perc", 75),
        ],
    },

    "dilla_drunk": {
        "name": "J Dilla Drunk Drums",
        "style": "Off-grid, humanized",
        "description": "Dilla NO cuantizaba. Cada nota desplazada del grid. Kicks 10-20ms TARDE, snares 15-30ms TARDE. NINGUN golpe al 127.",
        "reference_tracks": ["Donuts", "Slum Village 'Fall in Love'"],
        "bpm_range": (78, 95),
        "swing": "extreme_dilla",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap", "jazz_hiphop", "lofi"],
        "hits": [
            # Kicks - note: humanize will shift these
            (1, "kick", 100), (7, "kick", 90), (12, "kick", 85), (15, "kick", 80),
            # Snare - slightly off standard backbeat
            (6, "snare", 105), (14, "snare", 100),
            # Hi-hat 8th notes with inconsistent velocity
            (1, "closed_hat", 80), (3, "closed_hat", 60),
            (5, "closed_hat", 75), (7, "closed_hat", 55),
            (9, "closed_hat", 85), (11, "closed_hat", 50),
            (13, "closed_hat", 70), (15, "closed_hat", 65),
        ],
    },

    "9th_wonder_clean": {
        "name": "9th Wonder",
        "style": "Limpio y directo, FL Studio nativo",
        "description": "Cuantizacion PERFECTA. 9th Wonder usaba FL Studio, no hardware. Clap layeado con snare. Simple porque el sampling es complejo.",
        "reference_tracks": ["Little Brother 'The Listening'"],
        "bpm_range": (85, 95),
        "swing": "none",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap"],
        "hits": [
            # Kicks
            (1, "kick", 105), (9, "kick", 100), (11, "kick", 90),
            # Snare + Clap layered
            (5, "snare", 120), (13, "snare", 115),
            (5, "clap", 100), (13, "clap", 95),
            # Hi-hat 8th notes, even velocity
            (1, "closed_hat", 85), (3, "closed_hat", 85),
            (5, "closed_hat", 85), (7, "closed_hat", 85),
            (9, "closed_hat", 85), (11, "closed_hat", 85),
            (13, "closed_hat", 85), (15, "closed_hat", 85),
        ],
    },

    "rza_wu_tang": {
        "name": "Wu-Tang / RZA",
        "style": "Crudo, irregular, sucio",
        "description": "Kick irregular, no predecible. Hi-hat en OFFBEATS (3,7,11,15): crea tension. Drums MUY sucios, mucha saturacion, reverb en la snare.",
        "reference_tracks": ["C.R.E.A.M.", "Protect Ya Neck"],
        "bpm_range": (80, 95),
        "swing": "standard",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["boom_bap"],
        "hits": [
            # Kicks - irregular placement
            (1, "kick", 110), (4, "kick", 85), (9, "kick", 105), (14, "kick", 80),
            # Snare
            (5, "snare", 125), (13, "snare", 120),
            # Hi-hat on OFFBEATS only - creates tension
            (3, "closed_hat", 80), (7, "closed_hat", 75),
            (11, "closed_hat", 80), (15, "closed_hat", 75),
            # Crash on beat 1
            (1, "crash", 90),
        ],
    },

    "advanced_2bar": {
        "name": "Boom Bap Avanzado (2 compases)",
        "style": "Variacion de 2 compases con fills",
        "description": "Compas 1 standard + Compas 2 con kick extra en step 14, ghost snare en 16, open hat al final.",
        "reference_tracks": ["Boom bap avanzado"],
        "bpm_range": (85, 95),
        "swing": "standard",
        "steps_per_bar": 16,
        "bars": 2,
        "genre_tags": ["boom_bap"],
        "hits": [
            # === BAR 1 ===
            (1, "kick", 105), (8, "kick", 95), (11, "kick", 90),
            (5, "snare", 120), (13, "snare", 115),
            (1, "closed_hat", 90), (3, "closed_hat", 55),
            (5, "closed_hat", 85), (7, "closed_hat", 60),
            (9, "closed_hat", 90), (11, "closed_hat", 55),
            (13, "closed_hat", 85), (15, "closed_hat", 60),
            # === BAR 2 (steps 17-32) ===
            (17, "kick", 105), (24, "kick", 95), (27, "kick", 90), (30, "kick", 80),
            (21, "snare", 120), (29, "snare", 115), (32, "snare", 50),  # ghost snare
            (17, "closed_hat", 90), (19, "closed_hat", 55),
            (21, "closed_hat", 85), (23, "closed_hat", 60),
            (25, "closed_hat", 90), (27, "closed_hat", 55),
            (29, "closed_hat", 85), (31, "closed_hat", 60),
            (32, "open_hat", 85),  # open hat at end
        ],
    },

    # Trap pattern for versatility
    "trap_basic": {
        "name": "Trap Basico",
        "style": "Hi-hat rolls + 808 pattern",
        "description": "808 en beat 1, snare en 3. Hi-hats con rolls de 32nd notes. Swing minimo.",
        "reference_tracks": ["Metro Boomin", "Southside"],
        "bpm_range": (130, 160),
        "swing": "none",
        "steps_per_bar": 16,
        "bars": 1,
        "genre_tags": ["trap"],
        "hits": [
            # 808/Kick
            (1, "kick", 110), (11, "kick", 95),
            # Snare/Clap on beat 3
            (9, "clap", 127),
            # Hi-hat pattern with rolls
            (1, "closed_hat", 90), (2, "closed_hat", 50),
            (3, "closed_hat", 85), (4, "closed_hat", 50),
            (5, "closed_hat", 90), (6, "closed_hat", 50),
            (7, "closed_hat", 85), (8, "closed_hat", 50),
            (9, "closed_hat", 90), (10, "closed_hat", 50),
            (11, "closed_hat", 85), (12, "closed_hat", 50),
            (13, "closed_hat", 90), (14, "closed_hat", 70),
            (15, "closed_hat", 90), (16, "closed_hat", 70),
            # Open hat accent
            (8, "open_hat", 75),
        ],
    },
}

# Layering reference
LAYERING_GUIDE = {
    "kick": {
        "layers": [
            {"name": "Capa 1 - Caracter", "description": "Kick de vinilo (caracter, alma, suciedad)"},
            {"name": "Capa 2 - Peso", "description": "Kick sub/808 corto (peso, LP en 100-150Hz)"},
            {"name": "Capa 3 - Ataque", "description": "Click/snap (ataque, HP en 1kHz, volumen muy bajo)"},
        ],
        "tip": "ALINEAR transientes exactamente para evitar cancelacion de fase",
    },
    "snare": {
        "layers": [
            {"name": "Capa 1 - Caracter", "description": "Snare de vinilo (caracter principal)"},
            {"name": "Capa 2 - Ancho", "description": "Clap (HP 300Hz, -3 a -6dB, retrasar 5-10ms para efecto 'doble golpe')"},
            {"name": "Capa 3 - Brillo", "description": "Noise/snap (HP 2kHz, -8 a -12dB)"},
        ],
        "tip": "Reverb en la snare: Room/Plate, 0.5-1.0s decay, send al 20-35%",
    },
}


def _step_to_beat_position(step: int, steps_per_bar: int = 16) -> float:
    """Convert 1-indexed step number to beat position.

    Step 1 = beat 0.0, Step 5 = beat 1.0 (in 16-step bar = 4 beats)
    """
    return (step - 1) * (4.0 / steps_per_bar)


def get_patterns_for_bpm(bpm: float) -> List[Tuple[str, str, Tuple[int, int]]]:
    """Get drum patterns that match a specific BPM.

    Args:
        bpm: Current tempo in beats per minute

    Returns:
        List of (pattern_id, pattern_name, bpm_range) tuples that match,
        sorted by how well they fit (closest to center of range first)
    """
    matches = []
    for pat_id, pat in PATTERNS.items():
        low, high = pat["bpm_range"]
        if low <= bpm <= high:
            # Score: how close to the center of the range (lower = better)
            center = (low + high) / 2.0
            distance = abs(bpm - center)
            matches.append((distance, pat_id, pat["name"], pat["bpm_range"]))

    matches.sort(key=lambda x: x[0])
    return [(m[1], m[2], m[3]) for m in matches]


def check_bpm_compatibility(pattern_id: str, bpm: float) -> Optional[str]:
    """Check if a BPM is compatible with a pattern and return a warning if not.

    Args:
        pattern_id: Pattern key from PATTERNS
        bpm: Current tempo in BPM

    Returns:
        Warning string if BPM is outside the pattern's recommended range, None if OK
    """
    if pattern_id not in PATTERNS:
        return None
    pat = PATTERNS[pattern_id]
    low, high = pat["bpm_range"]
    if bpm < low or bpm > high:
        return (
            f"AVISO: El patron '{pat['name']}' esta disenado para {low}-{high} BPM, "
            f"pero el tempo actual es {bpm} BPM. "
            f"Puede sonar diferente al estilo original."
        )
    return None


def pattern_to_midi_notes(pattern_id: str, bars: int = 0,
                          humanize: float = 0.0, bpm: float = 0.0) -> str:
    """Convert a drum pattern to send_melody() compatible note data string.

    Args:
        pattern_id: Pattern key from PATTERNS
        bars: Number of bars to generate (0 = use pattern default)
        humanize: 0.0 (quantized) to 1.0 (very loose, Dilla-style)
        bpm: Current BPM for tempo-aware humanize scaling (0 = no scaling)

    Returns:
        String in format "note,velocity,length,position" per line
    """
    if pattern_id not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_id}. Available: {list(PATTERNS.keys())}")

    pattern = PATTERNS[pattern_id]
    pattern_bars = pattern["bars"]
    steps_per_bar = pattern["steps_per_bar"]

    if bars <= 0:
        bars = pattern_bars

    # BPM-aware humanize scaling:
    # At faster tempos each beat is shorter in real time, so the same beat offset
    # represents a larger timing shift. Scale humanize down at high BPM.
    # Reference: 90 BPM = standard scaling (1.0x)
    bpm_scale = 1.0
    if bpm > 0:
        bpm_scale = 90.0 / bpm  # at 180 BPM = 0.5x, at 45 BPM = 2.0x

    lines = []

    for bar_repeat in range(bars // pattern_bars + (1 if bars % pattern_bars else 0)):
        if bar_repeat * pattern_bars >= bars:
            break

        bar_offset_beats = bar_repeat * pattern_bars * 4.0

        for step, piece_name, velocity in pattern["hits"]:
            # Convert piece name to MIDI note
            piece = DrumPiece(piece_name)
            midi_note = DRUM_MIDI_MAP[piece]

            position = _step_to_beat_position(step, steps_per_bar) + bar_offset_beats

            # Check if this position is within requested bars
            if position >= bars * 4.0:
                continue

            # Apply humanize (random timing offset) - scaled by BPM
            if humanize > 0:
                max_offset = humanize * 0.15 * bpm_scale
                offset = random.uniform(-max_offset * 0.3, max_offset)  # biased late
                position = max(0, position + offset)
                # Also vary velocity slightly
                vel_variation = int(humanize * 15)
                velocity = max(1, min(127, velocity + random.randint(-vel_variation, vel_variation)))

            # Drum hits are short (0.1 beats)
            length = 0.1
            lines.append(f"{midi_note},{velocity},{length},{position:.2f}")

    return "\n".join(lines)


def list_patterns(genre: str = "") -> str:
    """List all available patterns, optionally filtered by genre."""
    lines = ["=== PATRONES DE BATERIA DISPONIBLES ===\n"]

    for pat_id, pat in PATTERNS.items():
        if genre and genre not in pat["genre_tags"]:
            continue
        lines.append(f"ID: {pat_id}")
        lines.append(f"  Nombre: {pat['name']}")
        lines.append(f"  Estilo: {pat['style']}")
        lines.append(f"  Descripcion: {pat['description']}")
        lines.append(f"  BPM: {pat['bpm_range'][0]}-{pat['bpm_range'][1]}")
        lines.append(f"  Swing: {pat['swing']} ({SWING_VALUES.get(pat['swing'], '?')}%)")
        lines.append(f"  Compases: {pat['bars']}")
        lines.append(f"  Referencia: {', '.join(pat['reference_tracks'])}")
        lines.append("")

    return "\n".join(lines)


def format_velocity_guide() -> str:
    """Format velocity reference as readable string."""
    lines = ["=== GUIA DE VELOCIDADES ===\n"]
    for piece, levels in VELOCITY_GUIDE.items():
        lines.append(f"{piece.upper()}:")
        for level_name, (low, high) in levels.items():
            lines.append(f"  {level_name}: {low}-{high}")
    lines.append("\n=== VALORES DE SWING ===\n")
    for name, desc in SWING_DESCRIPTIONS.items():
        lines.append(f"  {name}: {desc}")
    lines.append("\nTRUCO CLAVE: pon swing SOLO en los hats (55-65%) y deja kicks/snares")
    lines.append("en el grid. La tension entre el ritmo 'recto' del kick/snare y el")
    lines.append("'shuffle' del hat ES el sonido clasico del boom bap.")
    return "\n".join(lines)
