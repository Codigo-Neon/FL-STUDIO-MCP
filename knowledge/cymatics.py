"""Cymatics plugins knowledge - Diablo, Pluto, Space, Quake, Vortex.

Guia completa de plugins Cymatics instalados con presets por contexto,
cadenas por genero y parametros detallados.
"""

from typing import Dict, Optional


# ============================================================================
# 1. PLUGINS CYMATICS
# ============================================================================

CYMATICS_PLUGINS: Dict[str, Dict] = {
    "diablo": {
        "name": "Cymatics Diablo",
        "type": "Distorsion / Saturacion",
        "description": "Distorsion y saturacion versatil. Desde calidez sutil hasta destruccion total. Ideal para 808s, drums y buses.",
        "key_parameters": {
            "drive": {"range": (0, 100), "default": 30, "desc": "Cantidad de distorsion/saturacion"},
            "mix": {"range": (0, 100), "default": 50, "desc": "Dry/Wet blend"},
            "tone": {"range": (-100, 100), "default": 0, "desc": "Tilt EQ post-distorsion. Negativo=oscuro, positivo=brillante"},
            "mode": {"options": ["soft", "hard", "tube", "tape", "digital"], "default": "tube", "desc": "Algoritmo de saturacion"},
            "output": {"range": (-12, 12), "default": 0, "desc": "Ganancia de salida en dB"},
        },
    },
    "pluto": {
        "name": "Cymatics Pluto",
        "type": "Reverb",
        "description": "Reverb con caracter. Desde rooms tight hasta halls masivos. Muy musical para vocales y melodias.",
        "key_parameters": {
            "size": {"range": (0, 100), "default": 50, "desc": "Tamano del espacio. 0=room pequeno, 100=hall infinito"},
            "decay": {"range": (0.1, 20.0), "default": 2.0, "desc": "Tiempo de decaimiento en segundos"},
            "damping": {"range": (0, 100), "default": 50, "desc": "Absorcion de agudos. Alto=reverb oscura"},
            "pre_delay": {"range": (0, 200), "default": 20, "desc": "Pre-delay en ms. Separa senal seca del reverb"},
            "mix": {"range": (0, 100), "default": 25, "desc": "Dry/Wet blend"},
            "width": {"range": (0, 100), "default": 80, "desc": "Amplitud estereo del reverb"},
        },
    },
    "space": {
        "name": "Cymatics Space",
        "type": "Delay",
        "description": "Delay ritmico y creativo. Sync a tempo con feedback controlable. Bueno para vocales y melodias.",
        "key_parameters": {
            "time": {"range": (1, 2000), "default": 375, "desc": "Tiempo de delay en ms (o sync a BPM)"},
            "sync": {"options": ["free", "1/4", "1/8", "1/8d", "1/16", "1/4t"], "default": "1/4", "desc": "Subdivision ritmica"},
            "feedback": {"range": (0, 100), "default": 35, "desc": "Repeticiones. >70 = peligro de feedback infinito"},
            "mix": {"range": (0, 100), "default": 25, "desc": "Dry/Wet blend"},
            "filter_lp": {"range": (200, 20000), "default": 8000, "desc": "Filtro low-pass en Hz sobre las repeticiones"},
            "filter_hp": {"range": (20, 5000), "default": 200, "desc": "Filtro high-pass en Hz sobre las repeticiones"},
            "ping_pong": {"options": [True, False], "default": True, "desc": "Alternar repeticiones izquierda/derecha"},
        },
    },
    "quake": {
        "name": "Cymatics Quake",
        "type": "Sub Bass Enhancer",
        "description": "Generador y reforzador de sub graves. Sintetiza armonicos sub para anadir peso sin ensuciar la mezcla.",
        "key_parameters": {
            "sub_level": {"range": (0, 100), "default": 50, "desc": "Nivel del sub generado"},
            "frequency": {"range": (30, 120), "default": 60, "desc": "Frecuencia central del sub en Hz"},
            "drive": {"range": (0, 100), "default": 20, "desc": "Saturacion del sub generado"},
            "mix": {"range": (0, 100), "default": 40, "desc": "Dry/Wet blend"},
            "filter": {"range": (40, 150), "default": 80, "desc": "Low-pass del sub generado en Hz"},
            "output": {"range": (-12, 12), "default": 0, "desc": "Ganancia de salida en dB"},
        },
    },
    "vortex": {
        "name": "Cymatics Vortex",
        "type": "Modulacion (Chorus/Flanger/Phaser)",
        "description": "Efectos de modulacion. Chorus para amplitud, flanger para movimiento metalico, phaser para barridos. Ideal para pads, guitarras y texturas.",
        "key_parameters": {
            "mode": {"options": ["chorus", "flanger", "phaser"], "default": "chorus", "desc": "Tipo de modulacion"},
            "rate": {"range": (0.01, 20.0), "default": 1.0, "desc": "Velocidad de modulacion en Hz"},
            "depth": {"range": (0, 100), "default": 50, "desc": "Profundidad/intensidad del efecto"},
            "feedback": {"range": (-100, 100), "default": 0, "desc": "Retroalimentacion. Negativo=resonancia invertida"},
            "mix": {"range": (0, 100), "default": 50, "desc": "Dry/Wet blend"},
            "stereo": {"range": (0, 100), "default": 70, "desc": "Separacion estereo del efecto"},
        },
    },
}


# ============================================================================
# 2. PRESETS POR CONTEXTO
# ============================================================================

PRESETS_BY_CONTEXT: Dict[str, Dict] = {
    "vocal_warmth": {
        "descripcion": "Calidez sutil para vocales. Anade presencia sin distorsion audible.",
        "plugin": "diablo",
        "parametros": {
            "drive": 15,
            "mix": 40,
            "tone": -10,
            "mode": "tube",
            "output": -1,
        },
        "notas": "Usar en insert de vocal despues del EQ. El modo tube anade armonicos pares (calidos). Bajar output para compensar ganancia.",
    },
    "808_crunch": {
        "descripcion": "Crunch agresivo para 808s. Anade armonicos que se escuchan en parlantes pequenos.",
        "plugin": "diablo",
        "parametros": {
            "drive": 55,
            "mix": 70,
            "tone": 20,
            "mode": "hard",
            "output": -3,
        },
        "notas": "El drive alto genera armonicos que hacen audible el 808 en celulares/laptops. Tone positivo para cortar en la mezcla. Compensar volumen con output.",
    },
    "drum_parallel": {
        "descripcion": "Saturacion paralela para bus de drums. Pega y punch sin destruir transientes.",
        "plugin": "diablo",
        "parametros": {
            "drive": 40,
            "mix": 30,
            "tone": 10,
            "mode": "tape",
            "output": -2,
        },
        "notas": "Mix bajo = procesamiento paralelo. Tape mode preserva transientes mejor que hard/digital. Ideal en bus de drums, no en elementos individuales.",
    },
    "master_glue": {
        "descripcion": "Saturacion muy sutil en master bus. Cohesiona la mezcla como pasarla por cinta.",
        "plugin": "diablo",
        "parametros": {
            "drive": 8,
            "mix": 100,
            "tone": 0,
            "mode": "tape",
            "output": -0.5,
        },
        "notas": "MUY sutil. Si se escucha la distorsion, es demasiado. Drive bajo + tape = glue analogico. Siempre A/B comparar con bypass.",
    },
    "lofi_texture": {
        "descripcion": "Textura lo-fi vintage. Degrada la senal de forma musical para sampling estetico.",
        "plugin": "diablo",
        "parametros": {
            "drive": 45,
            "mix": 60,
            "tone": -30,
            "mode": "digital",
            "output": -4,
        },
        "notas": "Tone negativo recorta agudos (efecto vinilo). Digital mode anade aliasing sutil. Combinar con Vortex chorus lento para mas textura. Ideal para samples de piano/keys.",
    },
    "phonk_distortion": {
        "descripcion": "Distorsion agresiva estilo phonk/Memphis. Senal rota y sucia a proposito.",
        "plugin": "diablo",
        "parametros": {
            "drive": 75,
            "mix": 85,
            "tone": 30,
            "mode": "digital",
            "output": -6,
        },
        "notas": "Distorsion extrema intencionada. Tone alto para que corte. Compensar mucho con output porque el drive anade volumen. Usar en cowbells, vox chops, leads.",
    },
}


# ============================================================================
# 3. CADENAS POR GENERO
# ============================================================================

GENRE_CHAINS: Dict[str, Dict] = {
    "boom_bap": {
        "nombre": "Cadena Boom Bap",
        "descripcion": "Calidez analogica, reverb room sutil, delay con filtro. Todo suena a vinilo.",
        "cadena": [
            {
                "plugin": "diablo",
                "rol": "Calidez de cinta",
                "config": {"drive": 12, "mix": 50, "tone": -15, "mode": "tape", "output": -1},
            },
            {
                "plugin": "pluto",
                "rol": "Room sutil (sample vibe)",
                "config": {"size": 25, "decay": 0.8, "damping": 70, "pre_delay": 10, "mix": 15, "width": 60},
            },
            {
                "plugin": "space",
                "rol": "Delay filtrado (lo-fi echo)",
                "config": {"sync": "1/4", "feedback": 20, "mix": 12, "filter_lp": 3000, "filter_hp": 400, "ping_pong": False},
            },
        ],
        "aplicar_en": ["samples melodicos", "piano/keys", "bus de melodia"],
    },
    "trap": {
        "nombre": "Cadena Trap",
        "descripcion": "808 potente con armonicos, delay ritmico en melodias, sub enhancement.",
        "cadena": [
            {
                "plugin": "quake",
                "rol": "Refuerzo sub para 808",
                "config": {"sub_level": 60, "frequency": 55, "drive": 15, "mix": 35, "filter": 80, "output": 0},
            },
            {
                "plugin": "diablo",
                "rol": "Crunch de 808",
                "config": {"drive": 50, "mix": 65, "tone": 15, "mode": "hard", "output": -3},
            },
            {
                "plugin": "space",
                "rol": "Delay en melodias (1/8 dotted)",
                "config": {"sync": "1/8d", "feedback": 30, "mix": 20, "filter_lp": 6000, "filter_hp": 300, "ping_pong": True},
            },
        ],
        "aplicar_en": ["808 bass (Quake+Diablo)", "melodias (Space)", "hi-hats (Space sutil)"],
    },
    "phonk": {
        "nombre": "Cadena Phonk",
        "descripcion": "Distorsion extrema, modulacion oscura, reverb grande y espacioso.",
        "cadena": [
            {
                "plugin": "diablo",
                "rol": "Distorsion Memphis",
                "config": {"drive": 70, "mix": 80, "tone": 25, "mode": "digital", "output": -5},
            },
            {
                "plugin": "vortex",
                "rol": "Chorus oscuro (textura VHS)",
                "config": {"mode": "chorus", "rate": 0.3, "depth": 40, "feedback": 10, "mix": 25, "stereo": 50},
            },
            {
                "plugin": "pluto",
                "rol": "Hall grande y oscuro",
                "config": {"size": 75, "decay": 4.0, "damping": 80, "pre_delay": 40, "mix": 30, "width": 90},
            },
        ],
        "aplicar_en": ["cowbells/vox chops (Diablo)", "pads oscuros (Vortex+Pluto)", "leads distorsionados"],
    },
    "lofi": {
        "nombre": "Cadena Lo-Fi",
        "descripcion": "Degradacion vintage, chorus lento, reverb difuso. Suena a cassette viejo.",
        "cadena": [
            {
                "plugin": "diablo",
                "rol": "Saturacion vinilo/cassette",
                "config": {"drive": 35, "mix": 55, "tone": -25, "mode": "tape", "output": -3},
            },
            {
                "plugin": "vortex",
                "rol": "Chorus lento (wow & flutter)",
                "config": {"mode": "chorus", "rate": 0.5, "depth": 30, "feedback": 5, "mix": 35, "stereo": 60},
            },
            {
                "plugin": "pluto",
                "rol": "Reverb difuso y calido",
                "config": {"size": 45, "decay": 2.5, "damping": 65, "pre_delay": 25, "mix": 20, "width": 70},
            },
            {
                "plugin": "space",
                "rol": "Echo analogico sutil",
                "config": {"sync": "1/4", "feedback": 15, "mix": 10, "filter_lp": 2500, "filter_hp": 500, "ping_pong": False},
            },
        ],
        "aplicar_en": ["piano/rhodes", "guitarra", "samples de jazz/soul", "bus de melodia completo"],
    },
}


# ============================================================================
# 4. FUNCIONES HELPER
# ============================================================================

def get_cymatics_chain(element: str, genre: str) -> str:
    """Devuelve la cadena de plugins Cymatics recomendada para un elemento en un genero.

    Args:
        element: Tipo de elemento (808, vocal, drums, melodia, sample, etc.)
        genre: Genero musical (boom_bap, trap, phonk, lofi)

    Returns:
        Cadena formateada en espanol con configuraciones.
    """
    genre_key = genre.lower().replace(" ", "_").replace("-", "_")
    if genre_key not in GENRE_CHAINS:
        generos_disp = ", ".join(GENRE_CHAINS.keys())
        return f"Genero '{genre}' no encontrado. Disponibles: {generos_disp}"

    chain = GENRE_CHAINS[genre_key]
    lines = [
        f"=== CADENA CYMATICS: {chain['nombre'].upper()} ===",
        f"Descripcion: {chain['descripcion']}",
        f"Elemento: {element}",
        f"Aplicar en: {', '.join(chain['aplicar_en'])}",
        "",
    ]

    for i, step in enumerate(chain["cadena"], 1):
        plugin_info = CYMATICS_PLUGINS.get(step["plugin"], {})
        plugin_name = plugin_info.get("name", step["plugin"])
        lines.append(f"--- Paso {i}: {plugin_name} ---")
        lines.append(f"  Rol: {step['rol']}")
        lines.append(f"  Configuracion:")
        for param, value in step["config"].items():
            param_info = plugin_info.get("key_parameters", {}).get(param, {})
            desc = param_info.get("desc", "")
            lines.append(f"    {param}: {value}  ({desc})" if desc else f"    {param}: {value}")
        lines.append("")

    return "\n".join(lines)


def get_plugin_guide(plugin_name: str) -> str:
    """Devuelve guia completa de un plugin Cymatics.

    Args:
        plugin_name: Nombre del plugin (diablo, pluto, space, quake, vortex)

    Returns:
        Guia formateada en espanol.
    """
    key = plugin_name.lower().strip()
    if key not in CYMATICS_PLUGINS:
        disponibles = ", ".join(CYMATICS_PLUGINS.keys())
        return f"Plugin '{plugin_name}' no encontrado. Disponibles: {disponibles}"

    plugin = CYMATICS_PLUGINS[key]
    lines = [
        f"=== {plugin['name'].upper()} ===",
        f"Tipo: {plugin['type']}",
        f"Descripcion: {plugin['description']}",
        "",
        "PARAMETROS:",
    ]

    for param_name, param_info in plugin["key_parameters"].items():
        if "range" in param_info:
            rango = f"Rango: {param_info['range'][0]} - {param_info['range'][1]}"
        elif "options" in param_info:
            rango = f"Opciones: {', '.join(str(o) for o in param_info['options'])}"
        else:
            rango = ""
        lines.append(f"  {param_name}:")
        lines.append(f"    {param_info['desc']}")
        lines.append(f"    {rango}  |  Default: {param_info['default']}")

    # Presets relacionados
    related_presets = [
        (name, preset) for name, preset in PRESETS_BY_CONTEXT.items()
        if preset["plugin"] == key
    ]
    if related_presets:
        lines.append("")
        lines.append("PRESETS RELACIONADOS:")
        for preset_name, preset in related_presets:
            lines.append(f"  [{preset_name}] {preset['descripcion']}")

    return "\n".join(lines)


def list_cymatics_presets() -> str:
    """Lista todos los presets Cymatics disponibles con sus configuraciones.

    Returns:
        Todos los presets formateados en espanol.
    """
    lines = ["=== PRESETS CYMATICS POR CONTEXTO ===", ""]

    for preset_name, preset in PRESETS_BY_CONTEXT.items():
        plugin_info = CYMATICS_PLUGINS.get(preset["plugin"], {})
        plugin_display = plugin_info.get("name", preset["plugin"])
        lines.append(f"--- {preset_name.upper()} ---")
        lines.append(f"  Plugin: {plugin_display}")
        lines.append(f"  Descripcion: {preset['descripcion']}")
        lines.append(f"  Parametros:")
        for param, value in preset["parametros"].items():
            lines.append(f"    {param}: {value}")
        lines.append(f"  Notas: {preset['notas']}")
        lines.append("")

    return "\n".join(lines)
