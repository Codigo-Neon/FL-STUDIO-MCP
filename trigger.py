from typing import Any
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import subprocess
import threading
import time

# Knowledge base imports
from knowledge.scales import (
    SCALE_INTERVALS, SCALE_DESCRIPTIONS, GENRE_SCALE_RECOMMENDATIONS,
    MOOD_SCALE_MAP, COMMON_KEYS,
    get_scale_notes, get_scale_notes_range, format_scale_info,
)
from knowledge.chords import (
    PROGRESSION_DEFINITIONS,
    get_progression_chords, progression_to_midi_notes,
    format_progression_info, list_progressions,
)
from knowledge.drum_patterns import (
    PATTERNS, VELOCITY_GUIDE, SWING_VALUES,
    pattern_to_midi_notes, list_patterns, format_velocity_guide,
    get_patterns_for_bpm, check_bpm_compatibility,
)
from knowledge.basslines import (
    BASS_TYPES, BASS_PROCESSING_CHAIN, BASS_GOLDEN_RULES, BASS_TRICKS,
    generate_bassline_notes, format_bass_type_info, format_processing_chain,
    format_growl_guide, format_golden_rules, list_distortion_plugins,
)
from knowledge.plugin_chains import (
    get_chain, get_mix_levels, get_mastering_chain, get_eq_guide,
    get_send_config, get_gain_staging_guide, get_mixer_template,
    get_lufs_targets, get_workflow, get_soundtoys_guide,
)
from knowledge.vocal_chains import (
    get_vocal_chain, get_vocal_tricks, get_vocal_checklist,
)
from knowledge.producers import (
    get_producer_profile, list_producers,
)
from knowledge.song_structures import (
    STRUCTURES, TRANSITIONS, QUICK_START_10_STEPS,
    get_structure, get_quick_start,
)
from knowledge.constants import (
    Genre, SEMITONE_TO_NAME, midi_to_note,
)

# New knowledge modules
from knowledge.ozone12 import (
    get_mastering_chain as get_ozone_chain, get_module_guide as get_ozone_module,
    get_quick_master, get_lufs_targets as get_ozone_lufs, list_ozone_modules,
)
from knowledge.fabfilter import (
    get_eq_preset, get_compressor_preset, get_fabfilter_chain,
    get_saturn_guide, format_plugin_info as fabfilter_info,
)
from knowledge.serum2 import (
    get_patch_recipe, get_genre_sounds, get_fx_chain as get_serum_fx,
    get_sound_design_tips, get_wavetable_guide, list_patches as list_serum_patches,
)
from knowledge.cymatics import (
    get_cymatics_chain, get_plugin_guide as get_cymatics_guide,
    list_cymatics_presets,
)
from knowledge.autotune import (
    get_autotune_settings, get_vocal_tuning_workflow,
    get_key_detection_guide,
)
from knowledge.rx11 import (
    get_cleanup_chain, get_module_guide as get_rx_module,
    get_repair_workflow, list_rx_modules,
)
from knowledge.sampling import (
    get_chopping_guide, get_sampling_workflow, get_drum_machine_emulation,
    get_sample_processing_chain,
)
from knowledge.mixing_advanced import (
    get_mixing_workflow, get_gain_staging_guide as get_advanced_staging,
    get_bus_setup, get_mixing_checklist as get_advanced_checklist,
)
from knowledge.serum2 import list_patches as list_serum_patches
from knowledge.learned.user_learning import (
    save_pattern, get_best_patterns, save_preference,
    get_all_preferences, log_tool_use, get_tool_stats,
    analyze_midi_file, format_learned_context,
)
from knowledge.midi_transport import create_transport
from knowledge import mix_analyzer
from bridge import SysExClient, SysExBridgeError
from indexer.manifest import build_manifest, search_samples as _search_samples, library_stats
from indexer.paths import default_packs_root, default_manifest_path
from indexer.keywords import (
    SAMPLE_TYPE_KEYWORDS, GENRE_KEYWORDS, MOOD_KEYWORDS, SUBTYPE_KEYWORDS,
)

# Initialize FastMCP server
mcp = FastMCP("flstudio")

_transport = create_transport()

# SysEx bridge client to FL Studio script. Lazily connected on first use
# because trigger.py may start before FL Studio / the virtual MIDI ports
# exist. We open the rtmidi ports on first request; on failure we leave
# _bridge_client as None so the next request retries.
_bridge_client: "SysExClient | None" = None
_bridge_lock = threading.Lock()


def _get_bridge() -> "SysExClient":
    """Return the singleton SysExClient, opening it on first call.

    Connects on first call; subsequent calls reuse the open ports.
    If connect() fails the singleton stays None so the next call retries.
    """
    global _bridge_client
    with _bridge_lock:
        if _bridge_client is None:
            client = SysExClient()
            client.connect()
            _bridge_client = client
        return _bridge_client


def send_raw_midi(hex_string: str) -> None:
    """Send raw MIDI bytes to the active transport (Linux raw device or Windows rtmidi port)."""
    data = bytes.fromhex(hex_string.replace(" ", ""))
    _transport.send(data)

# Global BPM state - tracks the current project tempo
current_bpm: float = 90.0  # Default BPM (boom bap standard)

# Global genre + mastering target state (see mix_analyzer.GENRE_TARGETS)
current_genre: str = "neutral"
current_mastering_target: dict = dict(mix_analyzer.GENRE_TARGETS["neutral"])


# ============================================================================
# EXISTING TOOLS - MIDI COMMUNICATION (preserved exactly)
# ============================================================================

@mcp.tool()
def list_midi_ports():
    """List all available MIDI input ports"""
    result = subprocess.run(["amidi", "-l"], capture_output=True, text=True)
    print(result.stdout)
    return result.stdout


@mcp.tool()
def play():
    """Send MIDI message to start playback in FL Studio"""
    send_raw_midi("90 3C 64")
    time.sleep(0.1)
    send_raw_midi("80 3C 00")
    print("Sent Play command")


@mcp.tool()
def stop():
    """Send MIDI message to stop playback in FL Studio"""
    send_raw_midi("90 3D 64")
    time.sleep(0.1)
    send_raw_midi("80 3D 00")
    print("Sent Stop command")


def int_to_midi_bytes(value):
    """Convert an integer value into an array of MIDI-compatible bytes (7-bit values)."""
    if value < 0:
        value = abs(value)
    if value == 0:
        return [0]
    midi_bytes = []
    while value > 0:
        midi_bytes.insert(0, value & 0x7F)
        value >>= 7
    return midi_bytes


def change_tempo(bpm):
    """Change the tempo in FL Studio using a sequence of MIDI notes."""
    if bpm < 20 or bpm > 999:
        bpm = max(20, min(bpm, 999))
    bpm_int = int(bpm)
    midi_notes = int_to_midi_bytes(bpm_int)
    send_midi_note(72)
    time.sleep(0.2)
    for note in midi_notes:
        send_midi_note(note)
        time.sleep(0.1)
    send_midi_note(73)
    time.sleep(0.2)
    print(f"Tempo change to {bpm_int} BPM sent successfully")


@mcp.tool()
def send_melody(notes_data, bpm=None):
    """
    Record notes to FL Studio piano roll by sending real-time MIDI while FL records.

    Args:
        notes_data (str): String containing note data in format "note,velocity,length,position"
                         with each note on a new line.
                         note: MIDI note number (0-127)
                         velocity: MIDI velocity (0-127)
                         length: Duration in beats (e.g. 1.0 = quarter note)
                         position: Position in beats from start (e.g. 0.0 = beat 1)
        bpm (float): Tempo in BPM. Uses current_bpm if not specified.
    """
    global current_bpm
    tempo = float(bpm) if bpm else current_bpm
    seconds_per_beat = 60.0 / tempo

    notes = []
    for line in notes_data.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split(',')
        if len(parts) != 4:
            continue
        try:
            note = min(127, max(0, int(parts[0])))
            velocity = min(127, max(0, int(parts[1])))
            length = max(0, float(parts[2]))
            position = max(0, float(parts[3]))
            notes.append((note, velocity, length, position))
        except ValueError:
            continue

    if not notes:
        return "No valid notes found in input data"

    # Build a timeline of events (note_on and note_off) sorted by time
    events = []
    for note, velocity, length, position in notes:
        t_on = position * seconds_per_beat
        t_off = (position + length) * seconds_per_beat
        events.append((t_on, 'on', note, velocity))
        events.append((t_off, 'off', note, 0))
    events.sort(key=lambda e: e[0])

    # Send command to start recording in FL Studio (Note 76)
    send_midi_note(76, velocity=1)

    # Send notes in real-time
    start_time = time.time()
    for event_time, event_type, note, vel in events:
        # Wait until the right moment
        wait = event_time - (time.time() - start_time)
        if wait > 0:
            time.sleep(wait)
        if event_type == 'on':
            send_raw_midi(f"90 {note:02X} {vel:02X}")
        else:
            send_raw_midi(f"80 {note:02X} 00")

    # Wait a bit after last note
    time.sleep(0.3)

    # Send command to stop recording (Note 77)
    send_midi_note(77, velocity=1)

    return f"Recorded {len(notes)} notes to FL Studio piano roll at {tempo} BPM"


@mcp.tool()
def send_midi_note(note, velocity=1, duration=0.01):
    """Send a MIDI note on/off message with specified duration"""
    note = int(note)
    velocity = int(velocity)
    duration = float(duration)
    # note_on: 0x90 = note on channel 0
    send_raw_midi(f"90 {note:02X} {velocity:02X}")
    time.sleep(duration)
    # note_off: 0x80 = note off channel 0
    send_raw_midi(f"80 {note:02X} 00")


# ============================================================================
# BPM / TEMPO TOOLS
# ============================================================================

@mcp.tool()
def set_bpm(bpm: float, sync_to_fl: bool = True) -> str:
    """Set the project BPM. All generation tools will use this tempo automatically.

    IMPORTANT: Always call this FIRST before generating patterns, melodies, or basslines.
    The BPM affects which patterns are recommended, note lengths, humanize amounts, etc.

    Args:
        bpm: Tempo in beats per minute (20-999). Common ranges:
             - Boom bap: 80-95 BPM
             - Jazz hip-hop: 75-95 BPM
             - Lo-fi: 70-90 BPM
             - Trap/Drill: 130-160 BPM
             - Reggaeton: 85-100 BPM
             - Phonk: 130-145 BPM
             - UK Drill: 140-145 BPM
        sync_to_fl: If True, also change the tempo in FL Studio (default True)

    Returns:
        Confirmation with BPM set and genre suggestions
    """
    global current_bpm
    bpm = max(20.0, min(999.0, float(bpm)))
    current_bpm = bpm

    if sync_to_fl:
        change_tempo(bpm)

    # Determine likely genre based on BPM
    genre_suggestions = []
    if 70 <= bpm <= 95:
        genre_suggestions.append("boom_bap (80-95)")
    if 75 <= bpm <= 95:
        genre_suggestions.append("jazz_hiphop (75-95)")
    if 70 <= bpm <= 90:
        genre_suggestions.append("lofi (70-90)")
    if 85 <= bpm <= 100:
        genre_suggestions.append("reggaeton (85-100)")
    if 130 <= bpm <= 160:
        genre_suggestions.append("trap (130-160)")
    if 130 <= bpm <= 145:
        genre_suggestions.append("phonk (130-145)")
    if 140 <= bpm <= 145:
        genre_suggestions.append("uk_drill (140-145)")

    sync_msg = " y sincronizado con FL Studio" if sync_to_fl else ""
    suggestions = ", ".join(genre_suggestions) if genre_suggestions else "BPM fuera de rangos tipicos"

    return (
        f"BPM establecido a {bpm}{sync_msg}.\n"
        f"Generos sugeridos para {bpm} BPM: {suggestions}\n"
        f"Todas las herramientas de generacion ahora usaran {bpm} BPM automaticamente."
    )


@mcp.tool()
def get_bpm() -> str:
    """Get the current project BPM and its genre context.

    Returns:
        Current BPM with matching patterns, styles, and recommendations
    """
    bpm = current_bpm

    # Find matching drum patterns
    matching_patterns = get_patterns_for_bpm(bpm)

    # Genre detection
    genres = []
    if 70 <= bpm <= 95:
        genres.append("boom_bap")
    if 75 <= bpm <= 95:
        genres.append("jazz_hiphop")
    if 70 <= bpm <= 90:
        genres.append("lofi")
    if 85 <= bpm <= 100:
        genres.append("reggaeton")
    if 130 <= bpm <= 160:
        genres.append("trap")
    if 130 <= bpm <= 145:
        genres.append("phonk")
    if 140 <= bpm <= 145:
        genres.append("uk_drill")

    lines = [
        f"=== TEMPO ACTUAL: {bpm} BPM ===\n",
        f"Generos compatibles: {', '.join(genres) if genres else 'Fuera de rangos tipicos'}",
        "",
        "Patrones de drums recomendados:",
    ]
    for pat_id, pat_name, pat_range in matching_patterns:
        lines.append(f"  - {pat_id} ({pat_name}) [{pat_range[0]}-{pat_range[1]} BPM]")

    if not matching_patterns:
        lines.append("  (ninguno encaja exacto - se pueden usar igualmente)")

    return "\n".join(lines)


# ============================================================================
# MIXER TOOLS - Configure mixer tracks, routing, sidechain
# ============================================================================

# Mixer command constants (must match device_test.py)
_MIXER_START = 74
_MIXER_END = 75
_MIXER_CMD_SET_VOLUME = 1
_MIXER_CMD_SET_PAN = 2
_MIXER_CMD_SET_ROUTE = 3
_MIXER_CMD_SET_ROUTE_LEVEL = 4
_MIXER_CMD_MUTE = 5
_MIXER_CMD_SOLO = 6
_MIXER_CMD_LINK_CHANNEL = 7
_MIXER_CMD_SET_COLOR = 8
_MIXER_CMD_ARM = 9
_MIXER_CMD_SET_NAME = 10
_MIXER_CMD_SET_EQ = 11


def _send_mixer_command(cmd_type: int, *params: int):
    """Send a mixer command via MIDI protocol.

    Protocol: Note 74 (start) → cmd_type → params → Note 75 (end)
    """
    send_midi_note(_MIXER_START)
    time.sleep(0.05)
    send_midi_note(cmd_type)
    time.sleep(0.05)
    for p in params:
        send_midi_note(max(0, min(127, int(p))))
        time.sleep(0.05)
    send_midi_note(_MIXER_END)
    time.sleep(0.1)


@mcp.tool()
def mixer_set_track_volume(track: int, volume_db: float = 0.0) -> str:
    """Set the volume of a mixer track.

    Args:
        track: Mixer track index (1-125 for inserts, 0 for current)
        volume_db: Volume in dB. 0.0 = unity gain (100%), -6.0 = half, -inf = silent.
                   Converted to 0-127 MIDI value internally.
                   Common values: 0.0 (unity), -3.0 (soft), -6.0 (half), -12.0 (quiet)

    Returns:
        Confirmation message
    """
    # Convert dB to 0.0-1.0 range (FL Studio uses 0.0-1.25, where 0.8 ≈ 0dB)
    # Approximation: 0.8 = 0dB, 0.0 = -inf
    if volume_db <= -60:
        volume_normalized = 0.0
    else:
        volume_normalized = min(1.0, 0.8 * (10 ** (volume_db / 20.0)))
    midi_value = int(volume_normalized * 127)
    _send_mixer_command(_MIXER_CMD_SET_VOLUME, track, midi_value)
    return f"Track {track} volumen: {volume_db:.1f} dB (MIDI {midi_value}/127)"


@mcp.tool()
def mixer_set_track_pan(track: int, pan: float = 0.0) -> str:
    """Set the panning of a mixer track.

    Args:
        track: Mixer track index (1-125)
        pan: Pan position from -1.0 (full left) to 1.0 (full right). 0.0 = center.

    Returns:
        Confirmation message
    """
    pan = max(-1.0, min(1.0, pan))
    midi_value = int((pan + 1.0) * 63.5)  # Map -1.0..1.0 to 0..127
    _send_mixer_command(_MIXER_CMD_SET_PAN, track, midi_value)
    direction = "center" if abs(pan) < 0.05 else f"{'left' if pan < 0 else 'right'} {abs(int(pan*100))}%"
    return f"Track {track} pan: {direction}"


@mcp.tool()
def mixer_create_route(
    source_track: int,
    destination_track: int,
    enable: bool = True,
    send_level: float = 0.8,
) -> str:
    """Create or remove a routing connection between two mixer tracks.
    This is how you send audio from one track to another (buses, sends, sidechain).

    Args:
        source_track: Source mixer track index (the one sending audio)
        destination_track: Destination mixer track index (the one receiving audio)
        enable: True to create the route, False to remove it
        send_level: Send level 0.0 to 1.0 (default 0.8 ≈ 0dB)

    Returns:
        Confirmation message

    Example routing for sidechain:
        mixer_create_route(1, 5)  # Route kick (track 1) to bass (track 5)
    """
    _send_mixer_command(_MIXER_CMD_SET_ROUTE, source_track, destination_track, 1 if enable else 0)
    if enable and send_level != 0.8:
        time.sleep(0.1)
        level_midi = int(send_level * 127)
        _send_mixer_command(_MIXER_CMD_SET_ROUTE_LEVEL, source_track, destination_track, level_midi)
    state = "creada" if enable else "eliminada"
    return f"Ruta {state}: Track {source_track} → Track {destination_track} (nivel: {send_level:.1f})"


@mcp.tool()
def mixer_mute_track(track: int, mute: bool = True) -> str:
    """Mute or unmute a mixer track.

    Args:
        track: Mixer track index
        mute: True to mute, False to unmute
    """
    _send_mixer_command(_MIXER_CMD_MUTE, track, 1 if mute else 0)
    state = "muteado" if mute else "activado"
    return f"Track {track} {state}"


@mcp.tool()
def mixer_solo_track(track: int) -> str:
    """Toggle solo on a mixer track. Solo lets you hear only this track.

    Args:
        track: Mixer track index to solo/unsolo
    """
    _send_mixer_command(_MIXER_CMD_SOLO, track)
    return f"Track {track} solo toggled"


@mcp.tool()
def mixer_link_channel_to_track(channel: int, track: int) -> str:
    """Link a Channel Rack channel to a specific mixer track.
    This routes the channel's audio output to the mixer track.

    Args:
        channel: Channel index in the Channel Rack (0-based)
        track: Mixer track index to route to (1-125)

    Example:
        mixer_link_channel_to_track(0, 1)  # Route first channel (kick) to mixer track 1
    """
    _send_mixer_command(_MIXER_CMD_LINK_CHANNEL, channel, track)
    return f"Channel {channel} → Mixer Track {track}"


@mcp.tool()
def mixer_name_track(track: int, name: str) -> str:
    """Set the name of a mixer track.

    Args:
        track: Mixer track index (1-125)
        name: Name for the track (max ~20 characters recommended)
    """
    # Convert string to ASCII values for MIDI transmission
    ascii_values = [ord(c) for c in name[:20] if 32 <= ord(c) <= 126]
    _send_mixer_command(_MIXER_CMD_SET_NAME, track, *ascii_values)
    return f"Track {track} renombrado a '{name}'"


@mcp.tool()
def mixer_set_track_color(track: int, r: int, g: int, b: int) -> str:
    """Set the color of a mixer track.

    Args:
        track: Mixer track index (1-125)
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Common colors:
        Kick: r=255, g=50, b=50 (red)
        Snare: r=255, g=150, b=0 (orange)
        HiHats: r=255, g=255, b=0 (yellow)
        Bass: r=50, g=50, b=255 (blue)
        Melody: r=0, g=200, b=0 (green)
        Vocals: r=200, g=0, b=200 (purple)
    """
    # MIDI values 0-127, device_test.py scales to 0-255
    r_midi = min(127, r // 2)
    g_midi = min(127, g // 2)
    b_midi = min(127, b // 2)
    _send_mixer_command(_MIXER_CMD_SET_COLOR, track, r_midi, g_midi, b_midi)
    return f"Track {track} color: RGB({r},{g},{b})"


@mcp.tool()
def setup_sidechain(
    kick_track: int,
    bass_track: int,
    send_level: float = 0.8,
) -> str:
    """Set up sidechain compression: route the kick to the bass track for ducking.

    This creates the ROUTING in FL Studio's mixer. After this, you need to add
    Fruity Limiter on the bass track and configure it for sidechain compression.

    Args:
        kick_track: Mixer track number where the KICK is (e.g. 1)
        bass_track: Mixer track number where the BASS is (e.g. 5)
        send_level: How much kick signal to send (0.0-1.0, default 0.8)

    Returns:
        Routing confirmation + step-by-step guide to complete the sidechain setup

    Example:
        setup_sidechain(1, 5)  # Kick on track 1, bass on track 5
    """
    # Create the sidechain route
    _send_mixer_command(_MIXER_CMD_SET_ROUTE, kick_track, bass_track, 1)
    time.sleep(0.1)
    level_midi = int(send_level * 127)
    _send_mixer_command(_MIXER_CMD_SET_ROUTE_LEVEL, kick_track, bass_track, level_midi)

    return f"""=== SIDECHAIN CONFIGURADO ===

RUTA CREADA: Track {kick_track} (Kick) → Track {bass_track} (Bass)
Nivel de envio: {send_level:.1f}

Ahora completa estos pasos en FL Studio:

PASO 1 - Agregar Fruity Limiter al Bass:
  - Ve al Mixer, selecciona Track {bass_track} (Bass)
  - En un slot de efectos vacio, agrega "Fruity Limiter"

PASO 2 - Configurar el Sidechain:
  - En Fruity Limiter, haz click en la seccion "COMP" (compresor)
  - En la parte inferior, busca el selector de sidechain
  - Selecciona "Track {kick_track}" como fuente del sidechain

PASO 3 - Ajustar los parametros:
  - RATIO: Al maximo (∞:1) para un ducking fuerte
  - ATTACK: 0.5 ms (instantaneo - el bajo desaparece al instante con el kick)
  - RELEASE: 100-200 ms (ajustar al tempo: {int(60000 / current_bpm * 0.25)}-{int(60000 / current_bpm * 0.5)} ms para {current_bpm} BPM)
  - THRESHOLD: Ajustar hasta que el bajo baje ~3-6 dB cuando pega el kick

PASO 4 - Verificar:
  - Dale play y mira el medidor de ganancia del Fruity Limiter
  - Deberias ver el bajo "duckear" (bajar) cada vez que pega el kick
  - El bajo debe volver a su volumen normal entre kicks

TIPS:
  - Release MUY corto ({int(60000 / current_bpm * 0.15)} ms) = efecto "pumping" (EDM/sidechain extremo)
  - Release medio ({int(60000 / current_bpm * 0.3)} ms) = sutil, natural (boom bap)
  - Release largo ({int(60000 / current_bpm * 0.5)} ms) = muy sutil, casi imperceptible
  - El release ideal es que el bajo vuelva JUSTO antes del siguiente kick"""


@mcp.tool()
def apply_mixer_template(genre: str = "boom_bap") -> str:
    """Apply a complete mixer routing template: name tracks, set colors, create bus routes.

    Sets up the standard mixer layout:
    - Tracks 1-5: Drums (Kick, Snare, HiHats, Percs, Clap)
    - Track 6: Bass
    - Track 7: 808
    - Tracks 8-10: Melodics (Sample, Melody, Pads)
    - Tracks 11-13: Vocals (Main, Doubles, Ad-libs)
    - Track 100: Bus Drums (receives from 1-5)
    - Track 101: Bus Melodies (receives from 8-10)
    - Track 102: Bus Vocals (receives from 11-13)

    Args:
        genre: boom_bap or trap (affects naming and routing)

    Returns:
        Summary of all configured tracks and routes
    """
    template = [
        # (track, name, r, g, b)
        (1, "KICK", 255, 50, 50),
        (2, "SNARE", 255, 150, 0),
        (3, "HIHATS", 255, 255, 0),
        (4, "PERCS", 200, 200, 0),
        (5, "CLAP", 255, 100, 50),
        (6, "BASS", 50, 50, 255),
        (7, "808" if genre == "trap" else "SUB", 0, 100, 255),
        (8, "SAMPLE", 0, 200, 0),
        (9, "MELODY", 0, 255, 100),
        (10, "PADS", 100, 200, 100),
        (11, "VOX MAIN", 200, 0, 200),
        (12, "DOUBLES", 180, 50, 180),
        (13, "ADLIBS", 150, 80, 150),
    ]

    bus_routes = [
        # (src, dest, name)
        (1, 100, "Kick → Bus Drums"),
        (2, 100, "Snare → Bus Drums"),
        (3, 100, "HiHats → Bus Drums"),
        (4, 100, "Percs → Bus Drums"),
        (5, 100, "Clap → Bus Drums"),
        (8, 101, "Sample → Bus Melodies"),
        (9, 101, "Melody → Bus Melodies"),
        (10, 101, "Pads → Bus Melodies"),
        (11, 102, "Vox Main → Bus Vocals"),
        (12, 102, "Doubles → Bus Vocals"),
        (13, 102, "Adlibs → Bus Vocals"),
    ]

    bus_tracks = [
        (100, "BUS DRUMS", 255, 80, 80),
        (101, "BUS MELODY", 80, 255, 80),
        (102, "BUS VOCALS", 200, 80, 200),
    ]

    lines = [f"=== MIXER TEMPLATE ({genre.upper()}) ===\n"]

    # Name and color all tracks
    lines.append("Configurando tracks...")
    for track, name, r, g, b in template + bus_tracks:
        _send_mixer_command(_MIXER_CMD_SET_NAME, track, *[ord(c) for c in name[:20]])
        time.sleep(0.05)
        _send_mixer_command(_MIXER_CMD_SET_COLOR, track, min(127, r // 2), min(127, g // 2), min(127, b // 2))
        time.sleep(0.05)
        lines.append(f"  Track {track}: {name}")

    lines.append("\nCreando rutas de bus...")
    for src, dest, desc in bus_routes:
        _send_mixer_command(_MIXER_CMD_SET_ROUTE, src, dest, 1)
        time.sleep(0.05)
        lines.append(f"  {desc}")

    lines.append(f"""
TEMPLATE APLICADO. Estructura:
  Tracks 1-5   → BUS DRUMS (100)
  Tracks 8-10  → BUS MELODY (101)
  Tracks 11-13 → BUS VOCALS (102)
  Track 6      → BASS (directo al master)
  Track 7      → {'808' if genre == 'trap' else 'SUB'} (directo al master)

SIGUIENTE PASO:
  - Conecta cada channel del Channel Rack a su mixer track:
    mixer_link_channel_to_track(channel=0, track=1)  # primer canal → kick
  - O hazlo manualmente en FL: Channel Settings → Mixer Track number""")

    return "\n".join(lines)


@mcp.tool()
def get_sidechain_guide() -> str:
    """Get the complete sidechain compression guide with theory and techniques.

    Returns:
        Complete sidechain tutorial: what it is, why use it, how to set it up,
        settings per genre, and common mistakes.
    """
    bpm = current_bpm
    beat_ms = 60000 / bpm  # Duration of one beat in ms

    return f"""=== GUIA COMPLETA DE SIDECHAIN ===

QUE ES SIDECHAIN:
  El kick y el bajo compiten por las MISMAS frecuencias (40-100Hz).
  Si suenan al mismo tiempo, el mix se enturbia.
  Sidechain = el bajo BAJA de volumen cuando pega el kick, y vuelve a subir despues.
  Resultado: mix limpio, cada golpe de kick se siente.

COMO FUNCIONA:
  1. El kick envia su senal al compresor del bajo (via routing del mixer)
  2. Cada vez que el kick pega, el compresor reduce el volumen del bajo
  3. Cuando el kick deja de sonar, el bajo vuelve a su volumen normal

CONFIGURACION RAPIDA (usa setup_sidechain):
  setup_sidechain(kick_track=1, bass_track=6)
  Esto crea la ruta automaticamente. Luego sigue los pasos del guide.

SETTINGS POR GENERO A {bpm} BPM (beat = {beat_ms:.0f} ms):

  BOOM BAP (80-95 BPM):
    Attack: 0.5 ms
    Release: {int(beat_ms * 0.3)}-{int(beat_ms * 0.5)} ms
    Ratio: 4:1 a 8:1
    Reduccion: 3-4 dB (SUTIL - no debe notarse)
    Estilo: Casi invisible, solo limpia

  TRAP (130-160 BPM):
    Attack: 0.5 ms
    Release: {int(beat_ms * 0.2)}-{int(beat_ms * 0.35)} ms
    Ratio: 8:1 a inf:1
    Reduccion: 4-6 dB
    Estilo: Mas agresivo, el 808 "respira" con el kick

  EDM / PUMPING:
    Attack: 0.5 ms
    Release: {int(beat_ms * 0.6)}-{int(beat_ms * 0.8)} ms
    Ratio: inf:1
    Reduccion: 8-12 dB
    Estilo: MUY exagerado, efecto "pumping" audible

  REGGAETON:
    Attack: 0.5 ms
    Release: {int(beat_ms * 0.25)}-{int(beat_ms * 0.4)} ms
    Ratio: inf:1
    Reduccion: 6-8 dB
    Estilo: Marcado - el bombo y el bajo "bailan"

ALTERNATIVA SIN PLUGIN (Volume Automation):
  Si no quieres usar Fruity Limiter, puedes hacer sidechain manual:
  1. En el canal del bajo, click derecho en el volumen → Create Automation Clip
  2. Dibuja bajadas de volumen donde cae el kick
  3. Mas trabajo pero control TOTAL

ERRORES COMUNES:
  1. Release MUY corto = el bajo suena "cortado", antinatural
  2. Release MUY largo = el bajo no vuelve a tiempo, se pierde
  3. Threshold MUY bajo = comprime demasiado, el bajo desaparece
  4. No verificar en mono = puede haber cancelacion de fase
  5. Sidechain en la melodia tambien = suena amateur (solo en el bajo)

HERRAMIENTAS EN FL STUDIO:
  - Fruity Limiter (NATIVO - el mas usado, gratis)
  - Fruity Peak Controller + Volume (metodo avanzado)
  - Grossbeat (sidechain via patron de volumen)
  - Kickstart (Nicky Romero - plugin dedicado, simple)
  - LFO Tool (Xfer - sidechain via LFO, preciso)"""


# ============================================================================
# GENERATION TOOLS - Create patterns and send to FL Studio
# ============================================================================

@mcp.tool()
def generate_drum_pattern(
    style: str = "boom_bap_basic",
    bars: int = 0,
    humanize: float = 0.0,
    send_to_fl: bool = False,
) -> str:
    """Generate a drum pattern and optionally send it to FL Studio.
    Uses the current BPM (set with set_bpm) for tempo-aware generation.

    Args:
        style: Pattern style ID. Use list_drum_patterns() to see available styles.
               Options: boom_bap_basic, premier_style, pete_rock_groove, havoc_minimal,
               dilla_drunk, 9th_wonder_clean, rza_wu_tang, advanced_2bar, trap_basic
        bars: Number of bars (0 = use pattern default)
        humanize: Random velocity variation 0.0-1.0 (0=exact, 0.3=subtle, 0.7=heavy)
        send_to_fl: If True, send the generated pattern directly to FL Studio via MIDI

    Returns:
        Generated MIDI note data string (note,velocity,length,position per line)
    """
    bpm = current_bpm

    # Check BPM compatibility
    warning = check_bpm_compatibility(style, bpm)

    try:
        notes_data = pattern_to_midi_notes(style, bars, humanize, bpm)
    except ValueError as e:
        return str(e)

    header = f"Drum pattern '{style}' @ {bpm} BPM"
    parts = []

    if warning:
        parts.append(warning)
        # Suggest better patterns
        better = get_patterns_for_bpm(bpm)
        if better:
            suggestions = ", ".join(f"{p[0]} ({p[1]})" for p in better[:3])
            parts.append(f"Patrones recomendados para {bpm} BPM: {suggestions}")

    if send_to_fl:
        result = send_melody(notes_data)
        parts.append(f"{header} generado y enviado a FL Studio.\n{result}")
    else:
        parts.append(f"{header} generado ({bars or 'default'} bars, humanize={humanize}):")

    parts.append(f"\nNote data:\n{notes_data}")
    return "\n\n".join(parts)


@mcp.tool()
def generate_chord_progression(
    progression: str = "classic_dark",
    key: str = "A",
    bars: int = 4,
    velocity: int = 85,
    octave: int = 3,
    send_to_fl: bool = False,
) -> str:
    """Generate a chord progression and optionally send it to FL Studio.

    Args:
        progression: Progression ID. Use list_chord_progressions() to see options.
                    Options: classic_dark, jazz_hiphop, soul_feel, melancholic,
                    minimal_jazz, phrygian_dark, neo_soul
        key: Musical key root note (e.g. "A", "C", "D", "F#")
        bars: Number of bars to generate
        velocity: MIDI velocity for all notes (0-127)
        octave: Base octave for voicings (2-5)
        send_to_fl: If True, send directly to FL Studio

    Returns:
        Generated MIDI note data and chord information
    """
    try:
        info = format_progression_info(progression, key)
        notes_data = progression_to_midi_notes(progression, key, bars, 4.0, velocity, octave)
    except (ValueError, KeyError) as e:
        return str(e)

    if send_to_fl:
        result = send_melody(notes_data)
        return f"{info}\n\n{result}\n\nNote data:\n{notes_data}"

    return f"{info}\n\nNote data ({bars} bars):\n{notes_data}"


@mcp.tool()
def generate_bassline(
    root_notes: str = "A,A,F,G",
    style: str = "root_follow",
    bars: int = 4,
    octave: int = 1,
    velocity: int = 100,
    send_to_fl: bool = False,
) -> str:
    """Generate a bassline pattern and optionally send it to FL Studio.
    Uses the current BPM (set with set_bpm) to adapt note lengths and rhythmic density.

    At fast tempos (130+ BPM, trap/phonk): 808s get full sustain, walking bass simplifies.
    At slow tempos (<85 BPM, boom bap): walking bass adds passing tones, more groove.

    Args:
        root_notes: Comma-separated root notes for each bar (e.g. "A,A,F,G")
        style: Bass style - root_follow, walking, syncopated, sub_808
        bars: Number of bars
        octave: Bass octave (1-2 recommended)
        velocity: MIDI velocity (0-127)
        send_to_fl: If True, send directly to FL Studio

    Returns:
        Generated bass MIDI note data
    """
    bpm = current_bpm
    roots = [r.strip() for r in root_notes.split(",")]

    try:
        notes_data = generate_bassline_notes(roots, style, bars, octave, velocity, bpm)
    except (ValueError, KeyError) as e:
        return str(e)

    bpm_info = f" @ {bpm} BPM"
    parts = []

    # Add BPM-aware style recommendation
    from knowledge.basslines import _get_bpm_style_recommendation
    recommendation = _get_bpm_style_recommendation(bpm)
    if bpm > 0:
        parts.append(f"Estilo recomendado para {bpm} BPM: {recommendation}")

    if send_to_fl:
        result = send_melody(notes_data)
        parts.append(f"Bassline '{style}'{bpm_info} generado y enviado a FL Studio.\n{result}")
    else:
        parts.append(f"Bassline '{style}'{bpm_info} ({bars} bars, roots: {root_notes}):")

    parts.append(f"\nNote data:\n{notes_data}")
    return "\n\n".join(parts)


@mcp.tool()
def generate_scale_notes(
    root: str = "A",
    scale: str = "minor_natural",
    octave_low: int = 3,
    octave_high: int = 5,
) -> str:
    """Get all MIDI notes in a scale across octaves.

    Args:
        root: Root note (e.g. "A", "C", "D#")
        scale: Scale type - minor_natural, pentatonic_minor, blues, dorian,
               harmonic_minor, phrygian, major, pentatonic_major
        octave_low: Lowest octave
        octave_high: Highest octave

    Returns:
        Scale information with MIDI note numbers and note names
    """
    try:
        info = format_scale_info(root, scale)
        notes = get_scale_notes_range(root, scale, octave_low, octave_high)
        note_names = [midi_to_note(n) for n in notes]
    except (ValueError, KeyError) as e:
        return str(e)

    return f"{info}\n\nFull range ({octave_low}-{octave_high}):\nMIDI: {notes}\nNames: {', '.join(note_names)}"


@mcp.tool()
def suggest_for_bpm(bpm: float = 0) -> str:
    """Get complete production recommendations based on the current BPM.
    Suggests drum patterns, bass styles, chord progressions, and genre context.

    Args:
        bpm: BPM to analyze (0 = use current project BPM set with set_bpm)

    Returns:
        Complete BPM-aware production recommendations
    """
    if bpm <= 0:
        bpm = current_bpm

    lines = [f"=== RECOMENDACIONES PARA {bpm} BPM ===\n"]

    # Genre detection
    genres = []
    if 70 <= bpm <= 95:
        genres.append("boom_bap")
    if 75 <= bpm <= 95:
        genres.append("jazz_hiphop")
    if 70 <= bpm <= 90:
        genres.append("lofi")
    if 85 <= bpm <= 100:
        genres.append("reggaeton")
    if 130 <= bpm <= 160:
        genres.append("trap")
    if 130 <= bpm <= 145:
        genres.append("phonk")
    if 140 <= bpm <= 145:
        genres.append("uk_drill")
    lines.append(f"Generos: {', '.join(genres) if genres else 'Tempo atipico - vale experimentar'}")
    lines.append("")

    # Drum patterns
    lines.append("--- PATRONES DE DRUMS ---")
    matching = get_patterns_for_bpm(bpm)
    if matching:
        for pat_id, pat_name, pat_range in matching:
            lines.append(f"  >> {pat_id} - {pat_name} [{pat_range[0]}-{pat_range[1]} BPM]")
    else:
        lines.append("  No hay patrones exactos. Los mas cercanos:")
        # Show closest patterns
        all_pats = []
        for pat_id, pat in PATTERNS.items():
            low, high = pat["bpm_range"]
            center = (low + high) / 2
            dist = min(abs(bpm - low), abs(bpm - high))
            all_pats.append((dist, pat_id, pat["name"], pat["bpm_range"]))
        all_pats.sort()
        for _, pat_id, name, rng in all_pats[:3]:
            lines.append(f"  >> {pat_id} - {name} [{rng[0]}-{rng[1]} BPM]")
    lines.append("")

    # Bass style
    lines.append("--- ESTILO DE BAJO ---")
    from knowledge.basslines import _get_bpm_style_recommendation
    lines.append(f"  {_get_bpm_style_recommendation(bpm)}")
    if bpm >= 130:
        lines.append("  Nota: A tempos rapidos el 808 con sustain largo es el estandar.")
        lines.append("  Los 808s se generan con sustain completo (sin gap entre compases).")
    elif bpm <= 85:
        lines.append("  Nota: A tempos lentos hay espacio para walking bass con passing tones.")
        lines.append("  Los bajos se generan con mas notas de paso y groove.")
    lines.append("")

    # Chord progressions
    lines.append("--- PROGRESIONES RECOMENDADAS ---")
    for prog_id, prog in PROGRESSION_DEFINITIONS.items():
        for genre in genres:
            if genre in prog.get("genre_tags", []):
                lines.append(f"  >> {prog_id} - {prog['name']} ({prog['numerals']})")
                lines.append(f"     {prog['description']}")
                break
    lines.append("")

    # Swing recommendation
    lines.append("--- SWING ---")
    if bpm >= 130:
        lines.append("  Swing: none (50%) - Trap/drill es cuantizado, recto.")
        lines.append("  Humanize: 0.0 - Los patrones rapidos necesitan precision.")
    elif bpm >= 95:
        lines.append("  Swing: subtle (55%) - Un poco de vida sin perder el groove.")
        lines.append("  Humanize: 0.1-0.2 - Sutil variacion.")
    elif bpm >= 80:
        lines.append("  Swing: standard (60%) - EL CLASICO boom bap.")
        lines.append("  Humanize: 0.2-0.4 - Variacion natural.")
    else:
        lines.append("  Swing: strong_jazz (65%) - Mucho groove, jazz feel.")
        lines.append("  Humanize: 0.3-0.6 - Bastante variacion tipo Dilla.")
    lines.append("")

    # Quick command reference
    lines.append("--- COMANDOS RAPIDOS ---")
    lines.append(f"  set_bpm({bpm}) -> Ya configurado")
    if matching:
        lines.append(f"  generate_drum_pattern('{matching[0][0]}', send_to_fl=True)")
    lines.append(f"  generate_bassline('A,A,F,G', style='{'sub_808' if bpm >= 130 else 'syncopated'}', send_to_fl=True)")

    return "\n".join(lines)


# ============================================================================
# LISTING TOOLS - Browse available patterns, progressions, scales
# ============================================================================

@mcp.tool()
def list_available_drum_patterns(genre: str = "") -> str:
    """List all available drum patterns, optionally filtered by genre.

    Args:
        genre: Filter by genre (boom_bap, trap, phonk, lofi, jazz_hiphop) or empty for all
    """
    return list_patterns(genre)


@mcp.tool()
def list_available_progressions(genre: str = "") -> str:
    """List all available chord progressions, optionally filtered by genre.

    Args:
        genre: Filter by genre (boom_bap, trap, phonk, lofi, jazz_hiphop) or empty for all
    """
    return list_progressions(genre)


# ============================================================================
# MIXING ADVISOR TOOLS - Plugin chains, EQ, levels, mastering
# ============================================================================

@mcp.tool()
def get_plugin_chain(element: str, genre: str = "boom_bap") -> str:
    """Get the recommended plugin chain for a specific mix element.

    Args:
        element: Mix element - kick, snare, clap, hihats, bass, 808,
                sample, melody, pads, vocals, bus_drums, bus_melody, bus_vocals
        genre: Genre - boom_bap or trap

    Returns:
        Slot-by-slot plugin chain with exact settings
    """
    return get_chain(element, genre)


@mcp.tool()
def get_vocal_processing(style: str = "standard") -> str:
    """Get complete vocal processing chain (10 slots) with exact plugin settings.

    Args:
        style: Vocal style - standard, bright_trap, yung_beef

    Returns:
        Complete vocal chain: Gate > Pitch > EQ sub > Comp > EQ add > Sat > De-esser > Maximizer > Sends > Limiter
    """
    return get_vocal_chain(style)


@mcp.tool()
def get_mastering_guide(genre: str = "boom_bap") -> str:
    """Get complete mastering chain with exact plugin settings per genre.

    Args:
        genre: Genre - boom_bap, trap, lofi, general

    Returns:
        Full mastering chain (Ozone 12 modules) + LUFS targets per platform
    """
    chain = get_mastering_chain(genre)
    targets = get_lufs_targets()
    return f"{chain}\n\n{targets}"


@mcp.tool()
def get_mix_reference_levels(genre: str = "boom_bap") -> str:
    """Get reference mix levels and panning for all elements.

    Args:
        genre: boom_bap or trap

    Returns:
        Relative levels (dB) and panning for every element
    """
    return get_mix_levels(genre)


@mcp.tool()
def get_eq_frequency_guide(element: str = "") -> str:
    """Get EQ frequency guide for a specific element or all elements.

    Args:
        element: Element name (kick, snare, bass, vocals, etc.) or empty for full guide

    Returns:
        Cut/boost frequencies, problem areas, tips per element
    """
    return get_eq_guide(element)


@mcp.tool()
def get_send_effects(genre: str = "boom_bap") -> str:
    """Get send/return effects configuration (reverb, delay, parallel compression).

    Args:
        genre: boom_bap or trap

    Returns:
        Send configurations with plugin settings and routing
    """
    return get_send_config(genre)


@mcp.tool()
def get_bass_technique(genre: str = "boom_bap") -> str:
    """Get bass production techniques, plugins, and processing for a genre.

    Args:
        genre: boom_bap, trap, phonk, reggaeton, dubstep, uk_drill

    Returns:
        Bass type, generator, processing chain, and golden rules
    """
    info = format_bass_type_info(genre)
    chain = format_processing_chain()
    rules = format_golden_rules()
    return f"{info}\n\n{chain}\n\n{rules}"


@mcp.tool()
def get_bass_growl_guide() -> str:
    """Get the complete bass growl/distortion guide with plugin settings."""
    growl = format_growl_guide()
    plugins = list_distortion_plugins()
    return f"{growl}\n\n{plugins}"


# ============================================================================
# ANALYSIS & RECOMMENDATION TOOLS
# ============================================================================

@mcp.tool()
def suggest_scale(genre: str = "boom_bap", mood: str = "") -> str:
    """Recommend scales based on genre and/or mood.

    Args:
        genre: boom_bap, trap, phonk, lofi, jazz_hiphop, reggaeton, uk_drill
        mood: dark, melancholic, aggressive, jazzy, hopeful, cinematic, soulful (optional)

    Returns:
        Recommended scales with descriptions and common keys
    """
    lines = [f"=== ESCALAS RECOMENDADAS ===\n"]

    if mood and mood in MOOD_SCALE_MAP:
        lines.append(f"Para mood '{mood}':")
        for scale_id in MOOD_SCALE_MAP[mood]:
            info = SCALE_DESCRIPTIONS.get(scale_id, {})
            lines.append(f"  - {info.get('name', scale_id)}: {info.get('description', '')}")
        lines.append("")

    if genre in GENRE_SCALE_RECOMMENDATIONS:
        lines.append(f"Para genero '{genre}':")
        for scale_id in GENRE_SCALE_RECOMMENDATIONS[genre]:
            info = SCALE_DESCRIPTIONS.get(scale_id, {})
            lines.append(f"  - {info.get('name', scale_id)}: {info.get('description', '')}")
        lines.append("")

    if genre in COMMON_KEYS:
        lines.append(f"Keys mas comunes en {genre}: {', '.join(COMMON_KEYS[genre])}")

    if not mood and genre not in GENRE_SCALE_RECOMMENDATIONS:
        lines.append("Usa minor_natural si no estas seguro - es la reina del hip-hop.")

    return "\n".join(lines)


@mcp.tool()
def suggest_progression(key: str = "A", genre: str = "boom_bap", mood: str = "") -> str:
    """Recommend chord progressions for a key, genre, and mood.

    Args:
        key: Musical key root (e.g. "A", "C", "D")
        genre: boom_bap, trap, phonk, lofi, jazz_hiphop
        mood: dark, melancholic, aggressive, jazzy, hopeful, soulful (optional)

    Returns:
        Matching progressions with chords in the requested key
    """
    lines = [f"=== PROGRESIONES RECOMENDADAS en {key}m ===\n"]
    found = False

    for prog_id, prog in PROGRESSION_DEFINITIONS.items():
        genre_match = genre in prog.get("genre_tags", [])
        mood_match = (not mood) or prog.get("mood", "") == mood
        if genre_match and mood_match:
            found = True
            chords = get_progression_chords(prog_id, key, 3)
            chord_names = [c["name"] for c in chords]
            lines.append(f">> {prog['name']} ({prog['numerals']})")
            lines.append(f"   Acordes: {' - '.join(chord_names)}")
            lines.append(f"   {prog['description']}")
            lines.append(f"   Ref: {', '.join(prog['reference_tracks'])}")
            lines.append(f"   ID para generar: {prog_id}")
            lines.append("")

    if not found:
        lines.append(f"No hay progresiones exactas para genre={genre}, mood={mood}.")
        lines.append("Prueba con genre='boom_bap' o sin filtro de mood.")

    return "\n".join(lines)


@mcp.tool()
def get_producer_info(producer: str) -> str:
    """Get complete production style profile of a legendary producer.

    Args:
        producer: Producer ID - dj_premier, pete_rock, rza, j_dilla, 9th_wonder,
                 madlib, havoc, large_professor, alchemist, hi_tek, buckwild,
                 lord_finesse, marley_marl. Use 'list' to see all available.

    Returns:
        Complete profile: style, drum machine, swing, sampling, scales,
        progressions, effects, reference tracks, and replication tips
    """
    if producer == "list":
        return list_producers()
    return get_producer_profile(producer)


@mcp.tool()
def get_song_structure_template(genre: str = "boom_bap") -> str:
    """Get song structure template with section lengths, tips, and transitions.

    Args:
        genre: boom_bap or trap

    Returns:
        Complete structure: sections with bar counts, descriptions, tips, and transition techniques
    """
    return get_structure(genre)


@mcp.tool()
def get_mixing_checklist(genre: str = "boom_bap") -> str:
    """Get complete mixing workflow checklist step by step.

    Args:
        genre: boom_bap or trap

    Returns:
        Full workflow from gain staging to final export, plus common mistakes to avoid
    """
    workflow = get_workflow()
    staging = get_gain_staging_guide()
    return f"{staging}\n\n{workflow}"


@mcp.tool()
def get_vocal_tricks_guide() -> str:
    """Get advanced vocal production tricks (doubles, autotune, vocal chops, etc.)."""
    tricks = get_vocal_tricks()
    checklist = get_vocal_checklist()
    return f"{tricks}\n\n{checklist}"


@mcp.tool()
def get_quick_start_guide() -> str:
    """Get the 10-step quick start guide for making a boom bap beat from scratch."""
    return get_quick_start()


@mcp.tool()
def get_mixer_layout() -> str:
    """Get the recommended FL Studio mixer layout template with insert/bus/send assignments."""
    return get_mixer_template()


@mcp.tool()
def get_velocity_guide() -> str:
    """Get the MIDI velocity guide for realistic drum programming."""
    return format_velocity_guide()


@mcp.tool()
def get_soundtoys_plugins_guide() -> str:
    """Get guide for using Soundtoys plugins in hip-hop production."""
    return get_soundtoys_guide()


# ============================================================================
# PLUGIN-SPECIFIC TOOLS (Ozone, FabFilter, Serum, Cymatics, Auto-Tune, RX)
# ============================================================================

@mcp.tool()
def get_ozone_mastering(genre: str = "boom_bap") -> str:
    """Get complete Ozone 12 mastering chain for a genre with module settings.

    Args:
        genre: boom_bap, trap, phonk, lofi, jazz_hiphop

    Returns:
        Full mastering chain with each module's parameters
    """
    return get_ozone_chain(genre)


@mcp.tool()
def get_ozone_quick_master(genre: str = "boom_bap") -> str:
    """Get simplified 3-4 module Ozone mastering chain for quick results.

    Args:
        genre: boom_bap, trap, phonk, lofi, jazz_hiphop
    """
    return get_quick_master(genre)


@mcp.tool()
def get_ozone_module_guide(module: str) -> str:
    """Get detailed guide for a specific Ozone 12 module.

    Args:
        module: equalizer, dynamic_eq, dynamics, maximizer, exciter, imager,
                vintage_tape, vintage_eq, vintage_compressor, vintage_limiter,
                spectral_shaper, stabilizer, bass_control, clarity, impact,
                low_end_focus, match_eq, master_rebalance, unlimiter, stem_eq
    """
    return get_ozone_module(module)


@mcp.tool()
def get_lufs_target(genre: str = "", platform: str = "") -> str:
    """Get LUFS loudness targets by genre and streaming platform.

    Args:
        genre: boom_bap, trap, phonk, lofi, jazz_hiphop (optional)
        platform: spotify, youtube, apple_music, soundcloud (optional)
    """
    return get_ozone_lufs(genre, platform)


@mcp.tool()
def get_fabfilter_eq(element: str = "vocals") -> str:
    """Get Pro-Q 4 EQ preset for a specific element.

    Args:
        element: kick, snare, bass_808, vocals, piano_keys, hihats, master
    """
    return get_eq_preset(element)


@mcp.tool()
def get_fabfilter_compressor(element: str = "vocal_boom_bap") -> str:
    """Get Pro-C 3 compressor settings for an element.

    Args:
        element: vocal_boom_bap, vocal_trap, 808_trap, drum_bus_boom_bap,
                drum_bus_trap, drum_bus_phonk, master_bus
    """
    return get_compressor_preset(element)


@mcp.tool()
def get_fabfilter_mixing_chain(chain_type: str = "vocal_chain") -> str:
    """Get complete FabFilter-only mixing chain for an element.

    Args:
        chain_type: vocal_chain, drum_bus_chain, 808_chain, master_chain
    """
    return get_fabfilter_chain(chain_type)


@mcp.tool()
def get_saturation_guide() -> str:
    """Get FabFilter Saturn 2 saturation presets and guide."""
    return get_saturn_guide()


@mcp.tool()
def get_serum_patch(sound_type: str = "808_sub") -> str:
    """Get step-by-step Serum 2 patch recipe for a sound type.

    Args:
        sound_type: 808_sub, 808_distorted, trap_lead, boom_bap_keys,
                   dark_pad, pluck_melody, phonk_cowbell, vinyl_texture
    """
    return get_patch_recipe(sound_type)


@mcp.tool()
def get_serum_sounds_for_genre(genre: str = "boom_bap") -> str:
    """Get recommended Serum 2 sounds to create for a genre.

    Args:
        genre: boom_bap, trap, phonk, lofi
    """
    return get_genre_sounds(genre)


@mcp.tool()
def get_serum_sound_design() -> str:
    """Get Serum 2 sound design techniques (wavetables, FM, resampling, macros)."""
    return get_sound_design_tips()


@mcp.tool()
def get_cymatics_plugin_chain(element: str = "808", genre: str = "trap") -> str:
    """Get Cymatics plugin chain for an element and genre.

    Args:
        element: drums, bass, 808, vocals, leads, melody, keys
        genre: boom_bap, trap, phonk, lofi
    """
    return get_cymatics_chain(element, genre)


@mcp.tool()
def get_cymatics_plugin_guide(plugin: str = "diablo") -> str:
    """Get detailed guide for a Cymatics plugin.

    Args:
        plugin: diablo, pluto, space, quake, vortex
    """
    return get_cymatics_guide(plugin)


@mcp.tool()
def get_autotune_guide(style: str = "hard_tune") -> str:
    """Get Auto-Tune Pro settings for a vocal style.

    Args:
        style: natural (boom_bap/jazz), moderate (rnb/pop),
               hard_tune (trap/drill), extreme (hyperpop)
    """
    return get_autotune_settings(style)


@mcp.tool()
def get_vocal_tuning_guide() -> str:
    """Get complete vocal tuning workflow from recording to tuned vocal."""
    return get_vocal_tuning_workflow()


@mcp.tool()
def get_key_detection() -> str:
    """Get Auto-Key key detection workflow and tips."""
    return get_key_detection_guide()


@mcp.tool()
def get_rx_cleanup(source_type: str = "vinyl_sample") -> str:
    """Get iZotope RX 11 cleanup chain for a source type.

    Args:
        source_type: vinyl_sample, youtube_sample, vocal_recording,
                    field_recording, stem_isolation
    """
    return get_cleanup_chain(source_type)


@mcp.tool()
def get_rx_module_guide(module: str = "spectral_denoise") -> str:
    """Get detailed guide for a specific RX 11 module.

    Args:
        module: spectral_denoise, voice_denoise, de_click, de_crackle,
               de_clip, de_ess, de_plosive, breath_control, mouth_de_click,
               de_hum, de_reverb, dialogue_isolate, repair_assistant
    """
    return get_rx_module(module)


@mcp.tool()
def get_rx_overview() -> str:
    """Get general RX 11 repair workflow overview with all modules."""
    return get_repair_workflow()


# ============================================================================
# SAMPLING & ADVANCED MIXING TOOLS
# ============================================================================

@mcp.tool()
def get_sampling_guide(source: str = "vinyl") -> str:
    """Get sampling workflow for a source type.

    Args:
        source: vinyl, youtube, streaming, sample_packs
    """
    return get_sampling_workflow(source)


@mcp.tool()
def get_chopping_technique(technique: str = "") -> str:
    """Get chopping technique guide. Empty for overview of all techniques.

    Args:
        technique: manual, slicex, by_bar, by_beat, stutter (or empty for all)
    """
    return get_chopping_guide(technique)


@mcp.tool()
def get_drum_machine_guide(machine: str = "mpc_60") -> str:
    """Get drum machine emulation guide for FL Studio.

    Args:
        machine: mpc_60, sp_1200, mpc_3000
    """
    return get_drum_machine_emulation(machine)


@mcp.tool()
def get_sample_processing(style: str = "standard") -> str:
    """Get sample processing chain (EQ, filtering, vinyl simulation).

    Args:
        style: standard, lofi, aggressive, clean
    """
    return get_sample_processing_chain(style)


@mcp.tool()
def get_advanced_mixing_workflow(genre: str = "boom_bap") -> str:
    """Get advanced mixing workflow with gain staging, bus setup, and checklist.

    Args:
        genre: boom_bap, trap, phonk
    """
    return get_mixing_workflow(genre)


@mcp.tool()
def get_bus_routing(genre: str = "boom_bap") -> str:
    """Get recommended bus routing and processing setup.

    Args:
        genre: boom_bap, trap, phonk
    """
    return get_bus_setup(genre)


# ============================================================================
# LEARNING & ANALYSIS TOOLS
# ============================================================================

@mcp.tool()
def save_favorite_pattern(
    pattern_type: str,
    name: str,
    notes_data: str,
    genre: str = "",
    key: str = "",
    bpm: float = 0,
    rating: int = 5,
    notes: str = "",
) -> str:
    """Save a pattern the user liked for future reference and learning.

    Args:
        pattern_type: bassline, melody, drums, chord_progression
        name: Descriptive name
        notes_data: The MIDI note data or pattern description
        genre: Genre it was used for
        key: Musical key
        bpm: Tempo
        rating: 1-5 how much the user liked it
        notes: Additional notes
    """
    return save_pattern(pattern_type, name, {"notes_data": notes_data}, genre, key, bpm, rating, notes)


@mcp.tool()
def get_favorite_patterns(pattern_type: str = "", genre: str = "") -> str:
    """Get saved favorite patterns, optionally filtered.

    Args:
        pattern_type: bassline, melody, drums, chord_progression (or empty for all)
        genre: Filter by genre (or empty for all)
    """
    return get_best_patterns(pattern_type, genre)


@mcp.tool()
def analyze_midi(file_path: str) -> str:
    """Analyze a MIDI file and detect key, scale, range, note count, duration.

    Args:
        file_path: Path to the .mid file
    """
    return analyze_midi_file(file_path)


@mcp.tool()
def get_learned_context(genre: str = "") -> str:
    """Get summary of what the system has learned from user preferences and patterns.

    Args:
        genre: Optional genre filter
    """
    return format_learned_context(genre)


@mcp.tool()
def suggest_plugin_chain(element: str, genre: str, priority: str = "fabfilter") -> str:
    """Recommend a complete plugin chain using YOUR installed plugins.

    Args:
        element: kick, snare, bass, 808, vocals, hihats, piano, drums_bus, master
        genre: boom_bap, trap, phonk, lofi
        priority: fabfilter (default), cymatics, ozone, mixed
    """
    parts = [f"## Cadena para {element} ({genre})\n"]

    if priority == "fabfilter" or priority == "mixed":
        ff = get_fabfilter_chain(f"{element}_chain") if f"{element}_chain" in ["vocal_chain", "drum_bus_chain", "808_chain", "master_chain"] else ""
        if ff:
            parts.append(f"### FabFilter:\n{ff}\n")
        eq = get_eq_preset(element)
        if "no encontrado" not in eq.lower():
            parts.append(f"### EQ (Pro-Q 4):\n{eq}\n")

    if priority == "cymatics" or priority == "mixed":
        cym = get_cymatics_chain(element, genre)
        if "no encontrado" not in cym.lower():
            parts.append(f"### Cymatics:\n{cym}\n")

    if element == "master" and (priority == "ozone" or priority == "mixed"):
        oz = get_ozone_chain(genre)
        parts.append(f"### Ozone 12 Mastering:\n{oz}\n")

    return "\n".join(parts) if len(parts) > 1 else f"No hay cadena específica para {element}/{genre}. Probá con 'mixed' como priority."


# ============================================================================
# MCP RESOURCES - Contextual knowledge Claude can access automatically
# ============================================================================

@mcp.resource("flstudio://guides/quick-start")
def resource_quick_start() -> str:
    """10-step quick start guide for boom bap beat production."""
    return get_quick_start()


@mcp.resource("flstudio://guides/mixing/{genre}")
def resource_mixing_guide(genre: str) -> str:
    """Complete mixing guide for a genre."""
    workflow = get_workflow()
    staging = get_gain_staging_guide()
    levels = get_mix_levels(genre)
    return f"{staging}\n\n{levels}\n\n{workflow}"


@mcp.resource("flstudio://guides/vocals")
def resource_vocals_guide() -> str:
    """Complete vocal processing guide."""
    chain = get_vocal_chain("standard")
    tricks = get_vocal_tricks()
    checklist = get_vocal_checklist()
    return f"{chain}\n\n{tricks}\n\n{checklist}"


@mcp.resource("flstudio://guides/bass")
def resource_bass_guide() -> str:
    """Complete bass production guide."""
    chain = format_processing_chain()
    rules = format_golden_rules()
    growl = format_growl_guide()
    return f"{chain}\n\n{rules}\n\n{growl}"


@mcp.resource("flstudio://knowledge/scales")
def resource_scales() -> str:
    """Reference of all scales with descriptions and genre recommendations."""
    lines = ["=== REFERENCIA DE ESCALAS ===\n"]
    for scale_id in SCALE_INTERVALS:
        info = SCALE_DESCRIPTIONS.get(scale_id, {})
        lines.append(f"{info.get('name', scale_id)}:")
        lines.append(f"  {info.get('description', '')}")
        lines.append(f"  Mood: {info.get('mood', '')}")
        lines.append(f"  Formula: {info.get('formula', '')}")
        lines.append("")
    lines.append("RECOMENDACIONES POR GENERO:")
    for genre, scales in GENRE_SCALE_RECOMMENDATIONS.items():
        lines.append(f"  {genre}: {', '.join(scales)}")
    return "\n".join(lines)


@mcp.resource("flstudio://knowledge/producers/{name}")
def resource_producer(name: str) -> str:
    """Profile of a legendary producer."""
    return get_producer_profile(name)


@mcp.resource("flstudio://knowledge/mixer-template")
def resource_mixer_template() -> str:
    """FL Studio mixer layout template."""
    return get_mixer_template()


@mcp.resource("flstudio://knowledge/drum-patterns")
def resource_drum_patterns() -> str:
    """All available drum patterns."""
    return list_patterns()


@mcp.resource("flstudio://knowledge/chord-progressions")
def resource_progressions() -> str:
    """All available chord progressions."""
    return list_progressions()


# ============================================================================
# MCP PROMPTS - Reusable workflow templates
# ============================================================================

@mcp.prompt()
def new_beat(genre: str = "boom_bap", key: str = "Am", bpm: str = "90") -> str:
    """Guided workflow to create a complete beat from scratch."""
    return f"""Quiero crear un beat de {genre} en {key} a {bpm} BPM. Guiame paso a paso:

1. PRIMERO configura el tempo del proyecto
   - Usa set_bpm({bpm}) para establecer el BPM y sincronizar con FL Studio
   - Usa suggest_for_bpm() para ver todas las recomendaciones para este tempo
2. Recomiendame una escala y progresion de acordes para {key} en estilo {genre}
   - Usa suggest_scale(genre="{genre}") y suggest_progression(key="{key.replace('m','')}", genre="{genre}")
3. Genera un patron de drums apropiado para {genre} y {bpm} BPM
   - Usa generate_drum_pattern() - el sistema ya sabe el BPM y avisara si el patron no encaja
4. Genera la progresion de acordes en {key}
   - Usa generate_chord_progression() con la progresion elegida
5. Genera un bassline que siga los acordes
   - Usa generate_bassline() - las notas se adaptan automaticamente al tempo
6. Recomienda la cadena de plugins para cada elemento
   - Usa get_plugin_chain() para kick, snare, hihats, bass, sample
7. Dame la estructura de la cancion
   - Usa get_song_structure_template(genre="{genre}")
8. Dame los niveles de mezcla de referencia
   - Usa get_mix_reference_levels(genre="{genre}")

Vamos paso a paso. Empieza con el paso 1."""


@mcp.prompt()
def mix_element(element: str = "kick", genre: str = "boom_bap") -> str:
    """Get mixing advice for a specific element."""
    return f"""Necesito mezclar el {element} para un track de {genre}. Dame toda la info:

1. Cadena de plugins: get_plugin_chain("{element}", "{genre}")
2. Guia de EQ: get_eq_frequency_guide("{element}")
3. Niveles: get_mix_reference_levels("{genre}")
4. Sends/efectos: get_send_effects("{genre}")

Explica cada plugin, por que esta en ese orden, y que debo escuchar."""


@mcp.prompt()
def producer_style(producer: str = "dj_premier") -> str:
    """Guide to emulate a specific producer's style."""
    return f"""Quiero hacer un beat al estilo de {producer}. Dame la guia completa:

1. Perfil del productor: get_producer_info("{producer}")
2. Patron de drums que usa: usa list_available_drum_patterns() y elige el que mas se acerque
3. Escalas que prefiere: usa suggest_scale() con los generos del productor
4. Progresiones tipicas: usa list_available_progressions()
5. Cadena de mezcla: usa get_plugin_chain() para cada elemento

Armame el beat paso a paso siguiendo su estilo."""


@mcp.prompt()
def vocal_session() -> str:
    """Complete vocal recording and mixing workflow."""
    return """Voy a grabar y mezclar vocales. Dame el workflow completo:

1. Tips de grabacion: get_vocal_processing("standard")
2. Cadena de procesamiento 10 slots: get_vocal_processing("standard")
3. Trucos avanzados: get_vocal_tricks_guide()
4. Niveles en la mezcla: get_mix_reference_levels()

Explica cada paso, desde la grabacion hasta la mezcla final."""


@mcp.prompt()
def mastering_checklist(genre: str = "boom_bap") -> str:
    """Complete mastering checklist and workflow."""
    return f"""Necesito masterizar un track de {genre}. Dame el checklist completo:

1. Cadena de mastering: get_mastering_guide("{genre}")
2. Workflow completo: get_mixing_checklist("{genre}")
3. LUFS targets: estan incluidos en get_mastering_guide()
4. Errores comunes a evitar

Paso a paso, desde el pre-master hasta el archivo final."""


@mcp.tool()
def ping_fl() -> dict:
    """Send a ping to the FL Studio script and return its response.

    Use this to verify the bridge is alive and FL Studio's script is loaded.
    Returns {"pong": True} on success, or raises if FL is unreachable.
    """
    try:
        client = _get_bridge()
        return client.request("ping", timeout=2.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def get_fl_state() -> dict:
    """Query the live state of the FL Studio project via the bridge.

    Returns a dict with:
        bpm: current project tempo
        current_pattern: index of the focused pattern
        pattern_count: total patterns in the project
        channels: list of {index, name} for the channel rack
        mixer_tracks: list of {index, name} for the mixer

    Requires the bridge server to be running inside FL Studio. If unreachable,
    returns {"error": "..."} rather than raising — the LLM should treat this
    as 'FL not currently controllable'.
    """
    try:
        client = _get_bridge()
        return client.request("get_fl_state", timeout=5.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def set_genre(genre: str) -> str:
    """Set the project genre, configuring default mastering targets.

    Valid genres: boom_bap, trap, phonk, neutral.
    """
    global current_genre, current_mastering_target
    if genre not in mix_analyzer.GENRE_TARGETS:
        valid = ", ".join(mix_analyzer.GENRE_TARGETS.keys())
        return f"Género '{genre}' no soportado. Disponibles: {valid}."
    current_genre = genre
    current_mastering_target = mix_analyzer.get_genre_target(genre)
    t = current_mastering_target
    return (f"Género {genre}: target {t['lufs']} LUFS, true peak {t['true_peak']}dB, "
            f"headroom {t['headroom_db']}dB, dinámica {t['dynamics']}.")


@mcp.tool()
def set_mastering_target(lufs: float = None, true_peak: float = None,
                         headroom_db: float = None) -> str:
    """Override numeric mastering target values. Only changes the params passed."""
    global current_mastering_target
    if lufs is not None:
        if not (-30 <= lufs <= 0):
            return f"LUFS fuera de rango razonable [-30, 0]. Recibido: {lufs}."
        current_mastering_target["lufs"] = lufs
    if true_peak is not None:
        if not (-12 <= true_peak <= 0):
            return f"True peak fuera de rango razonable [-12, 0]. Recibido: {true_peak}."
        current_mastering_target["true_peak"] = true_peak
    if headroom_db is not None:
        current_mastering_target["headroom_db"] = headroom_db
    return f"Target actualizado: {current_mastering_target}"


@mcp.tool()
def get_mastering_target() -> dict:
    """Return the active mastering target (genre default + any overrides)."""
    return dict(current_mastering_target)


@mcp.tool()
def analyze_mix_static() -> str:
    """Analyze the current mix without playback. Reads the mixer snapshot and
    reports FX-heavy tracks, silent-active tracks, and master clipping risk."""
    try:
        client = _get_bridge()
        snapshot = client.request("get_mixer_snapshot", timeout=5.0)
    except SysExBridgeError as exc:
        return f"Bridge desconectado: {exc}. Verificá que FL Studio esté abierto."

    report = mix_analyzer.analyze_static(snapshot)
    fixes = mix_analyzer.suggest_fixes(report, {"flags": []}, current_mastering_target)
    return mix_analyzer.format_report_es(report, fixes=fixes)


@mcp.tool()
def analyze_master() -> str:
    """Analyze the master chain and peaks against the current mastering target.
    For peak data, run start_peak_monitoring(), play the track, then
    stop_peak_monitoring() before calling this."""
    try:
        client = _get_bridge()
        snapshot = client.request("get_mixer_snapshot", timeout=5.0)
        peaks = client.request("get_peak_report", timeout=5.0)
    except SysExBridgeError as exc:
        return f"Bridge desconectado: {exc}. Verificá que FL Studio esté abierto."

    tracks = snapshot.get("tracks", [])
    master_snap = next((t for t in tracks if t.get("idx") == 0), {})
    names = {t.get("idx"): t.get("name") for t in tracks}

    master_report = mix_analyzer.score_master(master_snap, peaks, current_mastering_target)
    peak_report = mix_analyzer.analyze_peaks(peaks, current_mastering_target)
    for t in peak_report.get("tracks", []):
        t["name"] = names.get(t["idx"], f"Track {t['idx']}")

    fixes = mix_analyzer.suggest_fixes(peak_report, master_report, current_mastering_target)
    return mix_analyzer.format_report_es(master_report, fixes=fixes)


@mcp.tool()
def start_peak_monitoring() -> str:
    """Start sampling mixer peaks (max-hold) inside FL. Play the section you
    want to measure, then call stop_peak_monitoring() and analyze_master()."""
    try:
        client = _get_bridge()
        res = client.request("start_peak_monitoring", timeout=5.0)
    except SysExBridgeError as exc:
        return f"Bridge desconectado: {exc}. Verificá que FL Studio esté abierto."
    if res.get("restarted"):
        return "Monitor de peaks reiniciado (estaba activo). Reproducí lo que quieras medir."
    return "Monitor de peaks activo. Reproducí lo que quieras medir."


@mcp.tool()
def stop_peak_monitoring() -> str:
    """Stop the peak monitoring service. Accumulated max-hold peaks are kept
    and readable via analyze_master() or get_peak_report()."""
    try:
        client = _get_bridge()
        res = client.request("stop_peak_monitoring", timeout=5.0)
    except SysExBridgeError as exc:
        return f"Bridge desconectado: {exc}. Verificá que FL Studio esté abierto."
    if not res.get("was_active"):
        return "Monitor ya estaba detenido."
    return "Monitor detenido. Peaks listos para analizar."


@mcp.tool()
def get_peak_report() -> dict:
    """Return accumulated max-hold peaks since the last start_peak_monitoring."""
    try:
        client = _get_bridge()
        return client.request("get_peak_report", timeout=5.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def get_track_volume(track: int) -> dict:
    """Return the current fader volume (0.0-1.0+) of a mixer track."""
    try:
        client = _get_bridge()
        return client.request("get_track_volume", {"track": track}, timeout=5.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def get_track_peaks(track: int) -> dict:
    """Return the current L/R peaks (dB) of a mixer track."""
    try:
        client = _get_bridge()
        return client.request("get_track_peaks", {"track": track}, timeout=5.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def get_track_pan(track: int) -> dict:
    """Return the current pan (-1.0..1.0) of a mixer track."""
    try:
        client = _get_bridge()
        return client.request("get_track_pan", {"track": track}, timeout=5.0)
    except SysExBridgeError as exc:
        return {"error": str(exc)}


@mcp.tool()
def search_samples_in_library(
    sample_type: str | None = None,
    subtype: str | None = None,
    genre: str | None = None,
    mood: str | None = None,
    key: str | None = None,
    bpm: int | None = None,
    bpm_tolerance: int = 5,
    loops_only: bool = False,
    oneshots_only: bool = False,
    limit: int = 20,
) -> dict:
    """Search the user's sample library by structured tags.

    All filters AND together. Returns paths + metadata for up to `limit`
    matches. The library must have been indexed first via `reindex_library`
    (or the manifest exists at the default location).

    Filter values must match the canonical category names. Use
    `list_sample_categories` to see what's valid.
    """
    manifest = default_manifest_path()
    if not manifest.exists():
        return {"error": "library not indexed yet — call reindex_library first"}
    results = _search_samples(
        manifest,
        sample_type=sample_type,
        subtype=subtype,
        genre=genre,
        mood=mood,
        key=key,
        bpm=bpm,
        bpm_tolerance=bpm_tolerance,
        is_loop=loops_only or None,
        is_oneshot=oneshots_only or None,
        limit=limit,
    )
    return {
        "count": len(results),
        "results": [
            {
                "path": r["path"],
                "filename": r["filename"],
                "folder": r["relative_folder"],
                "sample_type": r["sample_type"],
                "subtype": r["subtype"],
                "genres": r["genres"],
                "moods": r["moods"],
                "bpm": r["bpm"],
                "key": r["key"],
                "is_loop": r["is_loop"],
                "is_oneshot": r["is_oneshot"],
            }
            for r in results
        ],
    }


@mcp.tool()
def list_sample_categories() -> dict:
    """List the canonical category values accepted by `search_samples_in_library`.

    Returns categories for: sample_type, subtype, genre, mood. Use these
    exact strings when filtering.
    """
    return {
        "sample_types": list(SAMPLE_TYPE_KEYWORDS.keys()),
        "subtypes": list(SUBTYPE_KEYWORDS.keys()),
        "genres": list(GENRE_KEYWORDS.keys()),
        "moods": list(MOOD_KEYWORDS.keys()),
    }


@mcp.tool()
def get_library_stats() -> dict:
    """Return aggregate statistics about the indexed sample library:
    total samples, breakdown by sample type, breakdown by genre, count of
    samples with detected BPM, count with detected key, count of untyped
    samples.

    Use this to gauge whether the library is well-indexed before relying
    on `search_samples_in_library`.
    """
    manifest = default_manifest_path()
    if not manifest.exists():
        return {"error": "library not indexed yet — call reindex_library first"}
    return library_stats(manifest)


@mcp.tool()
def reindex_library(packs_root: str | None = None) -> dict:
    """Walk the sample library and update the manifest incrementally.

    On first run this indexes the entire library (1-2 minutes for ~40k
    samples on filename-only Capa 1 indexing). Subsequent runs are
    near-instant if nothing has changed.

    If `packs_root` is None the default location is used.

    Returns counts: {added, updated, unchanged, removed, total}.
    """
    root = Path(packs_root) if packs_root else default_packs_root()
    manifest = default_manifest_path()
    if not root.exists():
        return {"error": f"packs root does not exist: {root}"}
    stats = build_manifest(root, manifest)
    return stats


if __name__ == "__main__":
    mcp.run(transport='stdio')
