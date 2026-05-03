"""Conocimiento de FabFilter Suite completa para FL Studio MCP.

Pro-Q 4, Pro-C 3, Pro-L 2, Pro-R 2, Saturn 2, Pro-DS, Pro-G, Pro-MB,
Timeless 3, Volcano 3, Twin 3, Simplon, Micro.
EQ presets, compressor presets, limiter, saturación y mixing chains.
"""

from typing import Dict, List


# ============================================================================
# 1. PLUGINS FABFILTER
# ============================================================================

FABFILTER_PLUGINS: Dict[str, Dict] = {
    "pro_q4": {
        "name": "FabFilter Pro-Q 4",
        "type": "EQ Paramétrico",
        "description": "EQ premium con hasta 24 bandas, analizador espectral, dynamic EQ por banda, matching EQ.",
        "key_features": ["Dynamic EQ por banda", "Spectrum Grab", "Auto-Gain", "Mid/Side", "Linear Phase"],
    },
    "pro_c3": {
        "name": "FabFilter Pro-C 3",
        "type": "Compresor",
        "description": "Compresor versátil con 8 estilos. Desde transparente hasta pump extremo.",
        "styles": ["Clean", "Classic", "Opto", "Vocal", "Mastering", "Bus", "Punch", "Pumping"],
    },
    "pro_l2": {
        "name": "FabFilter Pro-L 2",
        "type": "Limiter",
        "description": "Limiter de mastering con múltiples algoritmos y medidor LUFS integrado.",
        "styles": ["Transparent", "Punchy", "Dynamic", "Allround", "Aggressive", "Modern", "Bus", "Safe"],
    },
    "pro_r2": {
        "name": "FabFilter Pro-R 2",
        "type": "Reverb",
        "description": "Reverb algorítmico con decay rate variable por frecuencia. Muy musical.",
    },
    "saturn2": {
        "name": "FabFilter Saturn 2",
        "type": "Saturación Multibanda",
        "description": "Saturación/distorsión multibanda con 30+ estilos. Desde sutil hasta destrucción.",
        "styles": ["Clean Tube", "Warm Tube", "Hot Tube", "Tape", "Transformer", "FET", "Guitar Amp", "Fuzz", "Destroy"],
    },
    "pro_ds": {
        "name": "FabFilter Pro-DS",
        "type": "De-esser",
        "description": "De-esser inteligente con detección precisa de sibilancia.",
    },
    "pro_g": {
        "name": "FabFilter Pro-G",
        "type": "Gate/Expander",
        "description": "Gate con lookahead y sidechain. Para limpiar bleeds y tightening.",
    },
    "pro_mb": {
        "name": "FabFilter Pro-MB",
        "type": "Compresor Multibanda",
        "description": "Compresión/expansión multibanda con crossovers dinámicos.",
    },
    "timeless3": {
        "name": "FabFilter Timeless 3",
        "type": "Delay",
        "description": "Delay creativo con filtros, modulación y stretching temporal.",
    },
    "volcano3": {
        "name": "FabFilter Volcano 3",
        "type": "Filtro Creativo",
        "description": "Filtro multi-modo con modulación. Desde filter sweep hasta sound design.",
    },
    "twin3": {
        "name": "FabFilter Twin 3",
        "type": "Sintetizador",
        "description": "Synth con filtros FabFilter. Osciladores + filtros de alta calidad.",
    },
}


# ============================================================================
# 2. EQ PRESETS (PRO-Q 4)
# ============================================================================

EQ_PRESETS: Dict[str, Dict] = {
    "kick": {
        "name": "EQ Kick",
        "bands": [
            {"freq": "30 Hz", "gain": "0 dB", "shape": "High Pass 24dB", "note": "Eliminar sub-sub innecesario"},
            {"freq": "60 Hz", "gain": "+3 dB", "q": 1.0, "shape": "Bell", "note": "Cuerpo del kick"},
            {"freq": "300 Hz", "gain": "-3 dB", "q": 2.0, "shape": "Bell", "note": "Limpiar boxiness"},
            {"freq": "3.5 kHz", "gain": "+2 dB", "q": 1.5, "shape": "Bell", "note": "Attack/click"},
        ],
    },
    "snare": {
        "name": "EQ Snare",
        "bands": [
            {"freq": "80 Hz", "gain": "0 dB", "shape": "High Pass 12dB", "note": "Limpiar low-end"},
            {"freq": "200 Hz", "gain": "+2 dB", "q": 1.0, "shape": "Bell", "note": "Cuerpo/weight"},
            {"freq": "400 Hz", "gain": "-2 dB", "q": 2.0, "shape": "Bell", "note": "Reducir mud"},
            {"freq": "5 kHz", "gain": "+3 dB", "q": 1.5, "shape": "Bell", "note": "Crack/snap"},
        ],
    },
    "bass_808": {
        "name": "EQ Bass/808",
        "bands": [
            {"freq": "30 Hz", "gain": "0 dB", "shape": "High Pass 12dB", "note": "Limpiar DC offset"},
            {"freq": "55 Hz", "gain": "+2 dB", "q": 1.5, "shape": "Bell", "note": "Fundamental del sub"},
            {"freq": "200 Hz", "gain": "-2 dB", "q": 2.0, "shape": "Bell", "note": "Limpiar para que no choque con kick"},
            {"freq": "800 Hz", "gain": "+1 dB", "q": 1.0, "shape": "Bell", "note": "Presencia en parlantes chicos"},
        ],
    },
    "vocals": {
        "name": "EQ Vocals",
        "bands": [
            {"freq": "80 Hz", "gain": "0 dB", "shape": "High Pass 18dB", "note": "Eliminar rumble"},
            {"freq": "250 Hz", "gain": "-2 dB", "q": 2.0, "shape": "Bell", "note": "Reducir boominess/proximidad"},
            {"freq": "3 kHz", "gain": "+2 dB", "q": 1.5, "shape": "Bell", "note": "Presencia y claridad"},
            {"freq": "8 kHz", "gain": "+1.5 dB", "q": 0.7, "shape": "High Shelf", "note": "Aire y brillo"},
            {"freq": "6 kHz", "gain": "-1 dB", "q": 3.0, "shape": "Bell (Dynamic)", "note": "De-ess dinámico"},
        ],
    },
    "piano_keys": {
        "name": "EQ Piano/Keys",
        "bands": [
            {"freq": "60 Hz", "gain": "0 dB", "shape": "High Pass 12dB"},
            {"freq": "200 Hz", "gain": "-1.5 dB", "q": 2.0, "shape": "Bell", "note": "Limpiar mud"},
            {"freq": "2.5 kHz", "gain": "+1 dB", "q": 1.0, "shape": "Bell", "note": "Presencia"},
            {"freq": "10 kHz", "gain": "+1 dB", "q": 0.7, "shape": "High Shelf", "note": "Brillo sutil"},
        ],
    },
    "hihats": {
        "name": "EQ Hi-Hats",
        "bands": [
            {"freq": "300 Hz", "gain": "0 dB", "shape": "High Pass 18dB", "note": "Quitar todo lo que no es hi-hat"},
            {"freq": "8 kHz", "gain": "+2 dB", "q": 1.0, "shape": "Bell", "note": "Brillo y definición"},
            {"freq": "12 kHz", "gain": "+1 dB", "q": 0.7, "shape": "High Shelf", "note": "Aire"},
        ],
    },
    "master": {
        "name": "EQ Master",
        "bands": [
            {"freq": "25 Hz", "gain": "0 dB", "shape": "High Pass 12dB", "note": "Limpiar sub-sub"},
            {"freq": "80 Hz", "gain": "+1 dB", "q": 0.8, "shape": "Low Shelf", "note": "Calidez sutil"},
            {"freq": "300 Hz", "gain": "-0.5 dB", "q": 1.0, "shape": "Bell", "note": "Limpiar mud levemente"},
            {"freq": "3 kHz", "gain": "+0.5 dB", "q": 1.0, "shape": "Bell", "note": "Presencia"},
            {"freq": "12 kHz", "gain": "+0.5 dB", "q": 0.5, "shape": "High Shelf", "note": "Aire"},
        ],
        "nota": "Movimientos SUTILES en master. Máximo ±1.5dB por banda.",
    },
}


# ============================================================================
# 3. COMPRESSOR PRESETS (PRO-C 3)
# ============================================================================

COMPRESSOR_PRESETS: Dict[str, Dict] = {
    "vocal_boom_bap": {
        "name": "Vocal Boom Bap",
        "style": "Vocal",
        "threshold": "-20 dB",
        "ratio": "3:1",
        "attack": "10 ms",
        "release": "60 ms",
        "knee": "6 dB",
        "gr_target": "3-6 dB",
        "note": "Estilo Vocal es transparente. Controla dinámica sin aplastar.",
    },
    "vocal_trap": {
        "name": "Vocal Trap",
        "style": "Punch",
        "threshold": "-18 dB",
        "ratio": "4:1",
        "attack": "5 ms",
        "release": "40 ms",
        "knee": "3 dB",
        "gr_target": "6-10 dB",
        "note": "Más agresivo. Punch mantiene transientes del flow.",
    },
    "808_trap": {
        "name": "808 Trap",
        "style": "Clean",
        "threshold": "-15 dB",
        "ratio": "4:1",
        "attack": "30 ms",
        "release": "100 ms",
        "knee": "3 dB",
        "gr_target": "3-5 dB",
        "note": "Attack lento para dejar pasar el punch del 808. Clean = transparente.",
    },
    "drum_bus_boom_bap": {
        "name": "Drum Bus Boom Bap",
        "style": "Bus",
        "threshold": "-22 dB",
        "ratio": "2:1",
        "attack": "20 ms",
        "release": "80 ms",
        "knee": "6 dB",
        "gr_target": "2-4 dB",
        "note": "Glue suave. Bus mode diseñado para subgrupos.",
    },
    "drum_bus_trap": {
        "name": "Drum Bus Trap",
        "style": "Punch",
        "threshold": "-18 dB",
        "ratio": "3:1",
        "attack": "8 ms",
        "release": "50 ms",
        "knee": "3 dB",
        "gr_target": "4-8 dB",
        "note": "Más agresivo. Punch para que los drums peguen.",
    },
    "drum_bus_phonk": {
        "name": "Drum Bus Phonk",
        "style": "Pumping",
        "threshold": "-15 dB",
        "ratio": "6:1",
        "attack": "1 ms",
        "release": "30 ms",
        "knee": "0 dB",
        "gr_target": "8-15 dB",
        "note": "Compresión extrema intencional. Pumping mode para efecto aplastado.",
    },
    "master_bus": {
        "name": "Master Bus",
        "style": "Mastering",
        "threshold": "-18 dB",
        "ratio": "1.5:1",
        "attack": "30 ms",
        "release": "150 ms",
        "knee": "10 dB",
        "gr_target": "1-2 dB",
        "note": "MUY suave. Solo glue. Mastering style tiene auto-gain.",
    },
}


# ============================================================================
# 4. LIMITER PRESETS (PRO-L 2)
# ============================================================================

LIMITER_PRESETS: Dict[str, Dict] = {
    "boom_bap": {
        "style": "Transparent",
        "gain": "+4 dB",
        "output": "-1 dB",
        "lookahead": "2 ms",
        "target_lufs": -14,
        "note": "Transparente, dinámico. No destruir la sensación vintage.",
    },
    "trap": {
        "style": "Modern",
        "gain": "+8 dB",
        "output": "-0.5 dB",
        "lookahead": "1 ms",
        "target_lufs": -8,
        "note": "Modern maneja bien el 808. Loud pero controlado.",
    },
    "phonk": {
        "style": "Aggressive",
        "gain": "+10 dB",
        "output": "-0.3 dB",
        "lookahead": "0.5 ms",
        "target_lufs": -7,
        "note": "Aplasta intencionalmente. Aggressive es el más heavy.",
    },
    "lofi": {
        "style": "Allround",
        "gain": "+5 dB",
        "output": "-1 dB",
        "lookahead": "2 ms",
        "target_lufs": -14,
        "note": "Suave y musical. No buscar loudness.",
    },
    "streaming": {
        "style": "Transparent",
        "gain": "+6 dB",
        "output": "-1 dB",
        "lookahead": "2 ms",
        "target_lufs": -14,
        "note": "Óptimo para Spotify/Apple Music. -14 LUFS.",
    },
}


# ============================================================================
# 5. SATURACIÓN PRESETS (SATURN 2)
# ============================================================================

SATURATION_PRESETS: Dict[str, Dict] = {
    "warm_bass": {
        "name": "Bass Cálido",
        "style": "Warm Tube",
        "drive": "30%",
        "mix": "50%",
        "dynamics": "40%",
        "bands": {"low": {"freq": "200 Hz", "drive": "40%"}, "high": {"drive": "10%"}},
        "note": "Tube cálido concentrado en graves. Añade armónicos pares.",
    },
    "tape_vocals": {
        "name": "Vocal Tape",
        "style": "Tape",
        "drive": "20%",
        "mix": "40%",
        "dynamics": "50%",
        "note": "Saturación de cinta sutil. Vocal suena más 'presente' sin distorsionar.",
    },
    "crushed_drums": {
        "name": "Drums Aplastados",
        "style": "FET",
        "drive": "60%",
        "mix": "100%",
        "dynamics": "20%",
        "note": "Para bus paralelo de drums. FET es agresivo y punchy.",
    },
    "808_grit": {
        "name": "808 Grit",
        "style": "Hot Tube",
        "drive": "50%",
        "mix": "60%",
        "dynamics": "30%",
        "bands": {"low": {"freq": "150 Hz", "drive": "60%"}, "mid": {"drive": "30%"}, "high": {"drive": "15%"}},
        "note": "Multibanda: más drive en graves para armónicos del 808.",
    },
    "vinyl_warmth": {
        "name": "Calidez Vinyl",
        "style": "Transformer",
        "drive": "15%",
        "mix": "30%",
        "dynamics": "60%",
        "note": "Transformer = sonido de hierro magnético. Sutil y vintage.",
    },
    "master_glue": {
        "name": "Master Glue",
        "style": "Clean Tube",
        "drive": "10%",
        "mix": "25%",
        "dynamics": "70%",
        "note": "Muy sutil en master bus. Clean Tube = armónicos sin distorsión audible.",
    },
    "parallel_crunch": {
        "name": "Parallel Crunch",
        "style": "Guitar Amp",
        "drive": "70%",
        "mix": "30%",
        "dynamics": "20%",
        "note": "Para bus paralelo. Mix bajo = blend de la señal cruncheada.",
    },
}


# ============================================================================
# 6. REVERB PRESETS (PRO-R 2)
# ============================================================================

REVERB_PRESETS: Dict[str, Dict] = {
    "vocal_room": {
        "name": "Vocal Room",
        "decay": "0.8s",
        "predelay": "15 ms",
        "brightness": "40%",
        "distance": "30%",
        "mix": "18%",
        "note": "Room natural para vocal. No lavar. Pre-delay separa.",
    },
    "vocal_plate": {
        "name": "Vocal Plate",
        "decay": "1.5s",
        "predelay": "25 ms",
        "brightness": "60%",
        "distance": "50%",
        "mix": "22%",
        "note": "Plate para vocal con más presencia. Típico de hip-hop.",
    },
    "snare_plate": {
        "name": "Snare Plate",
        "decay": "1.2s",
        "predelay": "10 ms",
        "brightness": "50%",
        "distance": "40%",
        "mix": "20%",
        "note": "Plate corto en snare para profundidad.",
    },
    "drum_room": {
        "name": "Drum Room",
        "decay": "0.5s",
        "predelay": "5 ms",
        "brightness": "35%",
        "distance": "25%",
        "mix": "15%",
        "note": "Room tight para bus de drums. Apenas perceptible.",
    },
    "ambient_pad": {
        "name": "Pad Ambiental",
        "decay": "4s",
        "predelay": "40 ms",
        "brightness": "30%",
        "distance": "70%",
        "mix": "35%",
        "note": "Hall grande para pads y texturas atmosféricas.",
    },
    "dark_hall": {
        "name": "Hall Oscuro (Phonk)",
        "decay": "3.5s",
        "predelay": "30 ms",
        "brightness": "15%",
        "distance": "60%",
        "mix": "25%",
        "note": "Hall oscuro para phonk. Brightness bajo = reverb sin brillo.",
    },
}


# ============================================================================
# 7. MIXING CHAINS FABFILTER
# ============================================================================

MIXING_CHAINS: Dict[str, Dict] = {
    "vocal_chain": {
        "name": "Cadena Vocal FabFilter",
        "chain": [
            {"plugin": "pro_q4", "role": "EQ substractivo", "preset": "vocals"},
            {"plugin": "pro_c3", "role": "Compresión", "preset": "vocal_boom_bap"},
            {"plugin": "pro_ds", "role": "De-ess", "settings": "Freq 6kHz, threshold -20dB, range 6dB"},
            {"plugin": "pro_q4", "role": "EQ aditivo", "settings": "Air shelf +1.5dB @ 10kHz"},
            {"plugin": "saturn2", "role": "Saturación sutil", "preset": "tape_vocals"},
        ],
    },
    "drum_bus_chain": {
        "name": "Cadena Bus Drums FabFilter",
        "chain": [
            {"plugin": "pro_q4", "role": "EQ limpieza", "settings": "HPF 30Hz, cut -2dB @ 400Hz"},
            {"plugin": "pro_c3", "role": "Bus compression", "preset": "drum_bus_boom_bap"},
            {"plugin": "saturn2", "role": "Saturación paralela", "preset": "crushed_drums"},
            {"plugin": "pro_l2", "role": "Limiting suave", "settings": "Gain +2dB, transparent"},
        ],
    },
    "808_chain": {
        "name": "Cadena 808 FabFilter",
        "chain": [
            {"plugin": "pro_q4", "role": "EQ", "preset": "bass_808"},
            {"plugin": "pro_c3", "role": "Compresión", "preset": "808_trap"},
            {"plugin": "saturn2", "role": "Saturación", "preset": "808_grit"},
        ],
    },
    "master_chain": {
        "name": "Cadena Master FabFilter",
        "chain": [
            {"plugin": "pro_q4", "role": "EQ correctivo", "preset": "master"},
            {"plugin": "pro_mb", "role": "Multibanda", "settings": "3 bandas, ratio 1.5:1, 2-3dB GR"},
            {"plugin": "saturn2", "role": "Glue", "preset": "master_glue"},
            {"plugin": "pro_l2", "role": "Limiting final", "preset": "boom_bap"},
        ],
    },
}


# ============================================================================
# 8. HELPER FUNCTIONS
# ============================================================================

def get_eq_preset(element: str) -> str:
    """Devuelve preset de EQ (Pro-Q 4) para un elemento."""
    preset = EQ_PRESETS.get(element)
    if not preset:
        available = ", ".join(EQ_PRESETS.keys())
        return f"Elemento no encontrado. Disponibles: {available}"

    lines = [f"## Pro-Q 4: {preset['name']}\n"]
    for i, band in enumerate(preset["bands"], 1):
        parts = [f"Band {i}: {band['shape']} @ {band['freq']}"]
        if "gain" in band and band["gain"] != "0 dB":
            parts.append(f"gain {band['gain']}")
        if "q" in band:
            parts.append(f"Q={band['q']}")
        line = " | ".join(parts)
        if band.get("note"):
            line += f"  — {band['note']}"
        lines.append(f"  {line}")

    if preset.get("nota"):
        lines.append(f"\n{preset['nota']}")

    return "\n".join(lines)


def get_compressor_preset(element: str) -> str:
    """Devuelve preset de compresor (Pro-C 3)."""
    preset = COMPRESSOR_PRESETS.get(element)
    if not preset:
        available = ", ".join(COMPRESSOR_PRESETS.keys())
        return f"Preset no encontrado. Disponibles: {available}"

    lines = [
        f"## Pro-C 3: {preset['name']}\n",
        f"  Style: {preset['style']}",
        f"  Threshold: {preset['threshold']}",
        f"  Ratio: {preset['ratio']}",
        f"  Attack: {preset['attack']}",
        f"  Release: {preset['release']}",
        f"  Knee: {preset['knee']}",
        f"  GR Target: {preset['gr_target']}",
        f"\n  {preset['note']}",
    ]
    return "\n".join(lines)


def get_fabfilter_chain(chain_type: str) -> str:
    """Devuelve cadena de mezcla completa usando solo FabFilter."""
    chain = MIXING_CHAINS.get(chain_type)
    if not chain:
        available = ", ".join(MIXING_CHAINS.keys())
        return f"Chain no encontrada. Disponibles: {available}"

    lines = [f"## {chain['name']}\n"]
    for i, slot in enumerate(chain["chain"], 1):
        plugin = FABFILTER_PLUGINS.get(slot["plugin"], {})
        name = plugin.get("name", slot["plugin"])
        lines.append(f"### Slot {i}: {name} — {slot['role']}")
        if "preset" in slot:
            lines.append(f"  Preset: {slot['preset']}")
        if "settings" in slot:
            lines.append(f"  Settings: {slot['settings']}")
        lines.append("")

    return "\n".join(lines)


def get_saturn_guide() -> str:
    """Devuelve guía de Saturn 2 con todos los presets de saturación."""
    lines = ["## FabFilter Saturn 2 — Guía de Saturación\n"]

    for key, preset in SATURATION_PRESETS.items():
        lines.append(f"### {preset['name']}")
        lines.append(f"  Style: {preset['style']} | Drive: {preset['drive']} | Mix: {preset['mix']}")
        if "bands" in preset:
            lines.append("  Bandas:")
            for band, settings in preset["bands"].items():
                lines.append(f"    {band}: {settings}")
        lines.append(f"  {preset['note']}")
        lines.append("")

    return "\n".join(lines)


def format_plugin_info(plugin_name: str) -> str:
    """Devuelve info detallada de un plugin FabFilter."""
    plugin = FABFILTER_PLUGINS.get(plugin_name)
    if not plugin:
        available = ", ".join(FABFILTER_PLUGINS.keys())
        return f"Plugin no encontrado. Disponibles: {available}"

    lines = [
        f"## {plugin['name']}",
        f"Tipo: {plugin['type']}",
        f"{plugin['description']}",
    ]

    if "styles" in plugin:
        lines.append(f"Estilos: {', '.join(plugin['styles'])}")
    if "key_features" in plugin:
        lines.append("Features:")
        for f in plugin["key_features"]:
            lines.append(f"  - {f}")

    return "\n".join(lines)
