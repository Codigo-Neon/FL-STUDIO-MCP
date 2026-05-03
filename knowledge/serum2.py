"""Conocimiento de sound design con Serum 2 para FL Studio MCP.

Recetas de patches, técnicas de síntesis, wavetables y FX chains
organizados por tipo de sonido y género.
"""

from typing import Dict, List


# ============================================================================
# 1. RECETAS DE PATCHES INICIALES
# ============================================================================

INIT_PATCHES: Dict[str, Dict] = {
    "808_sub": {
        "name": "808 Sub Limpio",
        "description": "Sub bass puro para boom bap y trap. Fundamental sin armónicos.",
        "osc_a": {
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "detune": 0,
            "octave": -1,
            "level": 100,
        },
        "osc_b": {"enabled": False},
        "filter": {
            "type": "LowPass 24dB",
            "cutoff": "200 Hz",
            "resonance": 0,
            "env_amount": 0,
        },
        "amp_env": {
            "attack": "0 ms",
            "decay": "800 ms",
            "sustain": "70%",
            "release": "300 ms",
        },
        "pitch_env": {
            "attack": "0 ms",
            "decay": "80 ms",
            "amount": "+12 semi (1 octava arriba, cae al pitch base)",
        },
        "fx": ["Compressor (ratio 4:1, threshold -12dB)", "EQ (cortar >300Hz)"],
        "tips": "El pitch envelope es clave para el 'punch'. Decay corto = más punch, largo = más tonal.",
    },
    "808_distorted": {
        "name": "808 Distorsionado (Trap/Phonk)",
        "description": "808 con armónicos y distorsión para que suene en parlantes chicos.",
        "osc_a": {
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "octave": -1,
            "level": 100,
        },
        "osc_b": {
            "enabled": True,
            "waveform": "Basic Shapes → Triangle",
            "unison": 1,
            "octave": -1,
            "level": 40,
            "note": "Mismo que OSC A, genera armónicos pares",
        },
        "filter": {
            "type": "LowPass 12dB",
            "cutoff": "800 Hz",
            "resonance": 15,
            "env_amount": 30,
            "drive": 20,
        },
        "amp_env": {
            "attack": "0 ms",
            "decay": "1200 ms",
            "sustain": "60%",
            "release": "400 ms",
        },
        "pitch_env": {
            "attack": "0 ms",
            "decay": "60 ms",
            "amount": "+12 semi",
        },
        "fx": [
            "Distortion (tube, drive 30%, mix 60%)",
            "Compressor (ratio 6:1, threshold -10dB)",
            "EQ (boost 60Hz +3dB, cut >2kHz)",
        ],
        "tips": "Subir el drive del filtro agrega calidez. Para phonk, usar Hyper/Dimension en FX.",
    },
    "trap_lead": {
        "name": "Lead Melódico Trap",
        "description": "Lead brillante tipo flute/bell para melodías trap.",
        "osc_a": {
            "waveform": "Basic Shapes → Saw",
            "unison": 4,
            "detune": "15%",
            "octave": 0,
            "level": 80,
        },
        "osc_b": {
            "enabled": True,
            "waveform": "Basic Shapes → Square",
            "unison": 2,
            "detune": "10%",
            "octave": 1,
            "level": 40,
        },
        "filter": {
            "type": "LowPass 24dB",
            "cutoff": "2.5 kHz",
            "resonance": 25,
            "env_amount": 50,
        },
        "filter_env": {
            "attack": "0 ms",
            "decay": "300 ms",
            "sustain": "30%",
            "release": "200 ms",
        },
        "amp_env": {
            "attack": "5 ms",
            "decay": "400 ms",
            "sustain": "50%",
            "release": "250 ms",
        },
        "fx": [
            "Chorus (rate 0.3Hz, depth 40%)",
            "Delay (1/8, feedback 30%, mix 20%)",
            "Reverb (size 40%, mix 15%)",
        ],
        "tips": "Automatizar el cutoff del filtro para variación melódica.",
    },
    "boom_bap_keys": {
        "name": "Rhodes/Wurlitzer Boom Bap",
        "description": "EP eléctrico cálido estilo jazz/soul para boom bap.",
        "osc_a": {
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "octave": 0,
            "level": 100,
        },
        "osc_b": {
            "enabled": True,
            "waveform": "Basic Shapes → Triangle",
            "unison": 1,
            "octave": 1,
            "level": 30,
            "note": "FM desde OSC A, amount 20%",
        },
        "filter": {
            "type": "LowPass 12dB",
            "cutoff": "3 kHz",
            "resonance": 10,
            "env_amount": 20,
            "key_tracking": 50,
        },
        "amp_env": {
            "attack": "10 ms",
            "decay": "600 ms",
            "sustain": "40%",
            "release": "400 ms",
        },
        "fx": [
            "Chorus (rate 0.5Hz, depth 30%, mix 25%)",
            "Phaser (rate 0.2Hz, depth 20%, mix 15%)",
            "Reverb (size 50%, mix 20%, damping 60%)",
        ],
        "tips": "El secreto del Rhodes es la FM sutil. Subir FM amount para más 'bark'.",
    },
    "dark_pad": {
        "name": "Pad Oscuro Ambiental",
        "description": "Pad atmosférico para intros, bridges y texturas.",
        "osc_a": {
            "waveform": "Basic Shapes → Saw",
            "unison": 7,
            "detune": "35%",
            "octave": 0,
            "level": 70,
        },
        "osc_b": {
            "enabled": True,
            "waveform": "Basic Shapes → Square",
            "unison": 5,
            "detune": "40%",
            "octave": -1,
            "level": 50,
        },
        "filter": {
            "type": "LowPass 24dB",
            "cutoff": "1.2 kHz",
            "resonance": 20,
            "env_amount": 15,
        },
        "amp_env": {
            "attack": "800 ms",
            "decay": "2000 ms",
            "sustain": "70%",
            "release": "1500 ms",
        },
        "lfo": {
            "target": "Filter Cutoff",
            "shape": "Sine",
            "rate": "0.1 Hz",
            "amount": "20%",
        },
        "fx": [
            "Reverb (size 80%, mix 40%, damping 30%)",
            "Delay (1/4 dotted, feedback 40%, mix 20%)",
            "Hyper/Dimension (mix 30%)",
        ],
        "tips": "Mucho unison + detune = amplitud. LFO lento al cutoff para movimiento.",
    },
    "pluck_melody": {
        "name": "Pluck Melódico",
        "description": "Sonido percusivo corto para melodías y arreglos.",
        "osc_a": {
            "waveform": "Basic Shapes → Saw",
            "unison": 3,
            "detune": "10%",
            "octave": 0,
            "level": 100,
        },
        "osc_b": {"enabled": False},
        "filter": {
            "type": "LowPass 24dB",
            "cutoff": "500 Hz",
            "resonance": 30,
            "env_amount": 70,
        },
        "filter_env": {
            "attack": "0 ms",
            "decay": "150 ms",
            "sustain": "0%",
            "release": "100 ms",
        },
        "amp_env": {
            "attack": "0 ms",
            "decay": "200 ms",
            "sustain": "0%",
            "release": "150 ms",
        },
        "fx": [
            "Delay (1/8, feedback 25%, mix 15%)",
            "Reverb (size 35%, mix 20%)",
        ],
        "tips": "El env amount del filtro es lo que crea el 'pluck'. Más amount = más brillante.",
    },
    "phonk_cowbell": {
        "name": "Cowbell Phonk (FM)",
        "description": "Cowbell metálico estilo Memphis/phonk via FM synthesis.",
        "osc_a": {
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "octave": 2,
            "level": 100,
        },
        "osc_b": {
            "enabled": True,
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "octave": 3,
            "level": 0,
            "note": "FM amount: 50%. Ratio inarmónico crea el timbre metálico.",
            "fine_tune": "+7 semi (ratio no entero)",
        },
        "filter": {"type": "Bypass"},
        "amp_env": {
            "attack": "0 ms",
            "decay": "250 ms",
            "sustain": "0%",
            "release": "100 ms",
        },
        "fx": [
            "Distortion (tube, drive 15%)",
            "EQ (boost 2-4kHz +4dB para brillo metálico)",
        ],
        "tips": "Ajustar el fine tune de OSC B cambia el timbre. Probar +5, +7, +11 semi.",
    },
    "vinyl_texture": {
        "name": "Textura Vinyl/Lo-fi",
        "description": "Capa de ruido y textura para dar carácter lo-fi.",
        "noise_osc": {
            "enabled": True,
            "type": "White → filtrar con LP",
            "level": 60,
            "pitch_tracking": False,
        },
        "osc_a": {
            "waveform": "Basic Shapes → Sine",
            "unison": 1,
            "octave": 0,
            "level": 20,
            "note": "Sub sutil para cuerpo",
        },
        "filter": {
            "type": "BandPass 12dB",
            "cutoff": "1.5 kHz",
            "resonance": 15,
            "note": "BP para simular el rango de vinyl",
        },
        "amp_env": {
            "attack": "200 ms",
            "decay": "0 ms",
            "sustain": "100%",
            "release": "500 ms",
        },
        "lfo": {
            "target": "Filter Cutoff",
            "shape": "Random/S&H",
            "rate": "2 Hz",
            "amount": "10%",
        },
        "fx": [
            "Distortion (tape, drive 20%, mix 40%)",
            "EQ (roll off <200Hz, roll off >8kHz)",
            "Compressor (ratio 3:1, para 'pegar' la textura)",
        ],
        "tips": "Usar como capa sutil (vol -15dB en mixer). El S&H LFO simula crackle.",
    },
}


# ============================================================================
# 2. TÉCNICAS DE SOUND DESIGN
# ============================================================================

SOUND_DESIGN_TECHNIQUES: Dict[str, Dict] = {
    "wavetable_manipulation": {
        "name": "Manipulación de Wavetables",
        "steps": [
            "Cargar wavetable desde menú de OSC (click en display)",
            "Usar WT Position para barrer entre frames",
            "Automatizar WT Position con LFO para movimiento",
            "Warp modes: Bend+, Bend-, PWM, Asym cambian el carácter",
            "FM From B: usar OSC B como modulador FM",
        ],
        "tips": [
            "Las wavetables 'Analog' son buenas para sonidos orgánicos",
            "Las 'Digital' y 'Spectral' para sonidos modernos/futuristas",
            "Importar audio propio como wavetable: arrastrar WAV al display del OSC",
        ],
    },
    "fm_synthesis": {
        "name": "Síntesis FM en Serum",
        "steps": [
            "Activar OSC B como modulador: click derecho en OSC A → FM from B",
            "Ajustar FM Amount (empieza bajo, 10-20%)",
            "Octava de OSC B define el ratio (1:1, 2:1, 3:1...)",
            "Ratios enteros = armónico. No enteros = inarmónico/metálico",
            "Fine tune de OSC B cambia dramáticamente el timbre",
        ],
        "tips": [
            "FM + Sine = bells, FM + Saw = growl",
            "Automatizar FM amount con envelope para evolución",
            "Ratio 1:1 (misma octava) = sonido tipo campana",
        ],
    },
    "noise_oscillator": {
        "name": "Oscillador de Ruido Creativo",
        "uses": [
            "Capa de textura sutil en pads",
            "Ataque percusivo en plucks (env rápido)",
            "Ruido de fondo lo-fi",
            "Simular breath/air en sonidos de viento",
            "Hi-hats sintéticos (noise + BP filter + env corto)",
        ],
    },
    "macro_assignments": {
        "name": "Macros para Performance",
        "recommended": {
            "Macro 1": "Filter Cutoff — control tonal principal",
            "Macro 2": "Reverb/Delay Mix — espacialidad",
            "Macro 3": "Distortion Drive — agresividad",
            "Macro 4": "LFO Rate — velocidad de movimiento",
            "Macro 5": "Detune Amount — amplitud/coro",
            "Macro 6": "Attack Time — percusivo vs pad",
            "Macro 7": "FM Amount — complejidad armónica",
            "Macro 8": "Dry/Wet FX global",
        },
    },
    "resampling": {
        "name": "Workflow de Resampling",
        "steps": [
            "1. Diseñar sonido base en Serum",
            "2. Grabar/renderizar a WAV en FL Studio",
            "3. Arrastrar WAV de vuelta a un OSC de Serum",
            "4. Serum lo convierte en wavetable automáticamente",
            "5. Aplicar nuevos filtros, FX y modulaciones",
            "6. Repetir para sonidos cada vez más complejos",
        ],
        "tips": "El resampling es la técnica más poderosa para sonidos únicos.",
    },
}


# ============================================================================
# 3. CADENAS DE FX INTERNAS DE SERUM
# ============================================================================

FX_CHAINS: Dict[str, List[Dict]] = {
    "808_chain": [
        {"slot": 1, "fx": "Distortion", "type": "Tube", "drive": "30%", "mix": "50%"},
        {"slot": 2, "fx": "Compressor", "ratio": "4:1", "threshold": "-12dB"},
        {"slot": 3, "fx": "EQ", "low_shelf": "+2dB @ 60Hz", "high_cut": "2kHz"},
    ],
    "lead_chain": [
        {"slot": 1, "fx": "Chorus", "rate": "0.3Hz", "depth": "40%", "mix": "25%"},
        {"slot": 2, "fx": "Delay", "time": "1/8", "feedback": "30%", "mix": "15%"},
        {"slot": 3, "fx": "Reverb", "size": "40%", "mix": "15%", "damping": "50%"},
        {"slot": 4, "fx": "Compressor", "ratio": "3:1", "threshold": "-8dB"},
    ],
    "pad_chain": [
        {"slot": 1, "fx": "Hyper/Dimension", "mix": "30%"},
        {"slot": 2, "fx": "Reverb", "size": "75%", "mix": "35%", "damping": "30%"},
        {"slot": 3, "fx": "Delay", "time": "1/4 dotted", "feedback": "35%", "mix": "20%"},
        {"slot": 4, "fx": "EQ", "high_cut": "8kHz", "low_cut": "80Hz"},
    ],
    "pluck_chain": [
        {"slot": 1, "fx": "Delay", "time": "1/8", "feedback": "25%", "mix": "15%"},
        {"slot": 2, "fx": "Reverb", "size": "35%", "mix": "20%"},
    ],
    "phonk_chain": [
        {"slot": 1, "fx": "Distortion", "type": "Hard Clip", "drive": "50%", "mix": "70%"},
        {"slot": 2, "fx": "EQ", "low_shelf": "+4dB @ 80Hz", "mid_cut": "-3dB @ 500Hz"},
        {"slot": 3, "fx": "Compressor", "ratio": "8:1", "threshold": "-6dB"},
    ],
}


# ============================================================================
# 4. SONIDOS POR GÉNERO
# ============================================================================

GENRE_SOUNDS: Dict[str, Dict] = {
    "boom_bap": {
        "esenciales": ["808_sub", "boom_bap_keys", "pluck_melody", "vinyl_texture"],
        "opcionales": ["dark_pad"],
        "notas": "Boom bap usa más samples que síntesis. Serum para capas sutiles y subs.",
        "approach": "Minimalista. Pocos sonidos, bien mezclados. El sample es el rey.",
    },
    "trap": {
        "esenciales": ["808_distorted", "trap_lead", "pluck_melody", "dark_pad"],
        "opcionales": ["phonk_cowbell"],
        "notas": "Trap depende mucho del 808 y leads melódicos. Automatizar todo.",
        "approach": "Capas de leads, 808 prominente, pads atmosféricos.",
    },
    "phonk": {
        "esenciales": ["808_distorted", "phonk_cowbell", "dark_pad", "vinyl_texture"],
        "opcionales": ["pluck_melody"],
        "notas": "Phonk = distorsión + lo-fi + Memphis. Saturar todo.",
        "approach": "Oscuro, saturado, agresivo. Cowbells y 808s distorsionados.",
    },
    "lofi": {
        "esenciales": ["boom_bap_keys", "vinyl_texture", "dark_pad", "808_sub"],
        "opcionales": ["pluck_melody"],
        "notas": "Lo-fi = imperfección. Bitcrush, tape saturation, roll off agudos.",
        "approach": "Todo filtrado, cálido, imperfecto. Menos es más.",
    },
}


# ============================================================================
# 5. HELPER FUNCTIONS
# ============================================================================

def get_patch_recipe(sound_type: str) -> str:
    """Devuelve receta paso a paso para crear un patch."""
    patch = INIT_PATCHES.get(sound_type)
    if not patch:
        available = ", ".join(INIT_PATCHES.keys())
        return f"Patch no encontrado. Disponibles: {available}"

    lines = [
        f"## {patch['name']}",
        f"{patch['description']}\n",
    ]

    # OSC A
    osc_a = patch.get("osc_a", {})
    lines.append("### Oscillador A")
    for k, v in osc_a.items():
        lines.append(f"  - {k}: {v}")

    # OSC B
    osc_b = patch.get("osc_b", {})
    if osc_b.get("enabled"):
        lines.append("\n### Oscillador B")
        for k, v in osc_b.items():
            if k != "enabled":
                lines.append(f"  - {k}: {v}")

    # Noise
    noise = patch.get("noise_osc", {})
    if noise.get("enabled"):
        lines.append("\n### Noise Oscillator")
        for k, v in noise.items():
            if k != "enabled":
                lines.append(f"  - {k}: {v}")

    # Filter
    filt = patch.get("filter", {})
    lines.append("\n### Filtro")
    for k, v in filt.items():
        lines.append(f"  - {k}: {v}")

    # Envelopes
    for env_name in ["amp_env", "filter_env", "pitch_env"]:
        env = patch.get(env_name)
        if env:
            label = env_name.replace("_", " ").title()
            lines.append(f"\n### {label}")
            for k, v in env.items():
                lines.append(f"  - {k}: {v}")

    # LFO
    lfo = patch.get("lfo")
    if lfo:
        lines.append("\n### LFO")
        for k, v in lfo.items():
            lines.append(f"  - {k}: {v}")

    # FX
    fx = patch.get("fx", [])
    if fx:
        lines.append("\n### FX Chain")
        for i, f in enumerate(fx, 1):
            lines.append(f"  Slot {i}: {f}")

    # Tips
    if patch.get("tips"):
        lines.append(f"\n**Tip**: {patch['tips']}")

    return "\n".join(lines)


def get_genre_sounds(genre: str) -> str:
    """Lista sonidos recomendados para un género."""
    gs = GENRE_SOUNDS.get(genre)
    if not gs:
        available = ", ".join(GENRE_SOUNDS.keys())
        return f"Género no encontrado. Disponibles: {available}"

    lines = [
        f"## Sonidos Serum 2 para {genre.replace('_', ' ').title()}\n",
        f"**Approach**: {gs['approach']}\n",
        "### Esenciales:",
    ]
    for s in gs["esenciales"]:
        patch = INIT_PATCHES.get(s, {})
        lines.append(f"  - **{s}**: {patch.get('name', s)} — {patch.get('description', '')}")

    if gs.get("opcionales"):
        lines.append("\n### Opcionales:")
        for s in gs["opcionales"]:
            patch = INIT_PATCHES.get(s, {})
            lines.append(f"  - **{s}**: {patch.get('name', s)}")

    lines.append(f"\n**Nota**: {gs['notas']}")
    return "\n".join(lines)


def get_fx_chain(chain_type: str) -> str:
    """Devuelve cadena de FX interna de Serum."""
    chain = FX_CHAINS.get(chain_type)
    if not chain:
        available = ", ".join(FX_CHAINS.keys())
        return f"Chain no encontrada. Disponibles: {available}"

    lines = [f"## FX Chain: {chain_type}\n"]
    for slot in chain:
        slot_num = slot["slot"]
        fx = slot["fx"]
        params = {k: v for k, v in slot.items() if k not in ("slot", "fx")}
        param_str = ", ".join(f"{k}: {v}" for k, v in params.items())
        lines.append(f"  Slot {slot_num}: **{fx}** — {param_str}")

    return "\n".join(lines)


def get_sound_design_tips() -> str:
    """Devuelve todas las técnicas de sound design."""
    lines = ["## Técnicas de Sound Design en Serum 2\n"]

    for key, tech in SOUND_DESIGN_TECHNIQUES.items():
        lines.append(f"### {tech['name']}")
        if "steps" in tech:
            for step in tech["steps"]:
                lines.append(f"  {step}")
        if "uses" in tech:
            for use in tech["uses"]:
                lines.append(f"  - {use}")
        if "recommended" in tech:
            for macro, desc in tech["recommended"].items():
                lines.append(f"  - **{macro}**: {desc}")
        if "tips" in tech:
            for tip in tech["tips"]:
                lines.append(f"  💡 {tip}")
        lines.append("")

    return "\n".join(lines)


def get_wavetable_guide() -> str:
    """Guía de selección de wavetables."""
    lines = [
        "## Guía de Wavetables en Serum 2\n",
        "### Categorías principales:",
        "  - **Analog**: Sonidos clásicos, cálidos. Para bass, leads vintage.",
        "  - **Digital**: Sonidos modernos, limpios. Para leads trap, plucks.",
        "  - **Spectral**: Timbres complejos, evolutivos. Para pads, texturas.",
        "  - **Vowel**: Formantes vocales. Para leads tipo vocal, wobble bass.",
        "  - **Basic Shapes**: Sine, Saw, Square, Triangle. Punto de partida.",
        "",
        "### Por tipo de sonido:",
        "  - **808/Sub**: Basic Shapes → Sine (siempre)",
        "  - **Lead**: Digital o Analog → barrer con WT Position",
        "  - **Pad**: Spectral o Analog → mucho unison + WT movement",
        "  - **Pluck**: Digital → env rápido al WT Position",
        "  - **Bell/Keys**: Basic Shapes + FM synthesis",
        "  - **Growl/Bass**: Vowel o Spectral → automación agresiva",
        "",
        "### Importar wavetables propias:",
        "  1. Arrastrar archivo WAV al display del oscillador",
        "  2. Serum lo divide en frames automáticamente",
        "  3. Ajustar número de frames si es necesario",
        "  4. Funciona con samples, grabaciones, o audio procesado",
    ]
    return "\n".join(lines)


def list_patches() -> str:
    """Lista todos los patches disponibles."""
    lines = ["## Patches disponibles en Serum 2\n"]
    for key, patch in INIT_PATCHES.items():
        lines.append(f"  - **{key}**: {patch['name']} — {patch['description']}")
    return "\n".join(lines)
