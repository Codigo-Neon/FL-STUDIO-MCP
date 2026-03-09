"""
Complete mixing and mastering knowledge for FL Studio MCP.

Encodes all plugin chains, EQ guides, mix levels, gain staging,
mastering chains, send configurations, and LUFS targets from the
comprehensive boom bap / trap mixing guide.

Plugins referenced: iZotope Ozone 12, iZotope RX, FabFilter Pro-Q 3,
Soundtoys (full bundle), Antares Auto-Tune, FL Studio native plugins.
"""

from .constants import Genre

# ---------------------------------------------------------------------------
# 1. MIXER_TEMPLATE -- Recommended FL Studio mixer layout
# ---------------------------------------------------------------------------

MIXER_TEMPLATE = {
    "inserts": {
        1:   {"name": "KICK 1",          "color": "red",       "group": "drums"},
        2:   {"name": "KICK 2 (capa)",   "color": "red",       "group": "drums"},
        3:   {"name": "SNARE / CLAP",    "color": "orange",    "group": "drums"},
        4:   {"name": "HI-HATS / SHAKERS / RIDES", "color": "yellow", "group": "drums"},
        5:   {"name": "PERCS",           "color": "yellow",    "group": "drums"},
        6:   {"name": "BAJO / 808 (1)",  "color": "blue",      "group": "bass"},
        7:   {"name": "BAJO / 808 (2)",  "color": "blue",      "group": "bass"},
        8:   {"name": "SAMPLES / MELODIAS (1)", "color": "green", "group": "melody"},
        9:   {"name": "SAMPLES / MELODIAS (2)", "color": "green", "group": "melody"},
        10:  {"name": "PADS / TEXTURAS", "color": "teal",      "group": "melody"},
        11:  {"name": "VOZ PRINCIPAL",   "color": "purple",    "group": "vocals"},
        12:  {"name": "DOBLES / COROS",  "color": "purple",    "group": "vocals"},
        13:  {"name": "AD-LIBS",         "color": "purple",    "group": "vocals"},
        14:  {"name": "(RESERVA)",       "color": "gray",      "group": "other"},
    },
    "buses": {
        100: {"name": "BUS DRUMS",       "color": "red",       "receives_from": [1, 2, 3, 4, 5]},
        101: {"name": "BUS MELODIAS",    "color": "green",     "receives_from": [8, 9, 10]},
        102: {"name": "BUS VOCES",       "color": "purple",    "receives_from": [11, 12, 13]},
    },
    "sends": {
        103: {"name": "VOX REVERB",      "color": "pink",      "wet": "100%"},
        104: {"name": "VOX DELAY",       "color": "pink",      "wet": "100%"},
        105: {"name": "DRUM REVERB",     "color": "pink",      "wet": "100%"},
    },
    "master": {
        "name": "MASTER",
        "note": "Cadena de mastering final",
    },
}


# ---------------------------------------------------------------------------
# 2. PLUGIN_CHAINS -- keyed by (element, genre) tuples
#    Each value is a list of PluginSlot dicts with:
#       plugin_name, purpose, settings (dict)
# ---------------------------------------------------------------------------

PLUGIN_CHAINS = {
    # ===================================================================
    # KICK
    # ===================================================================
    ("kick", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ substractivo",
            "settings": {
                "high_pass": "30Hz, 18dB/oct (quitar sub-rumble del sample)",
                "cut_1": "300-400Hz, -2dB, Q=2 (quitar carton)",
                "boost_1": "60-80Hz, +2dB, Q=1.5 (peso)",
                "boost_2": "3-5kHz, +2-3dB, Q=1 (ataque/punch)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion analogica (sonido MPC por cinta)",
            "settings": {
                "style": "T (Tape)",
                "drive": "3-4 de 10 (sutil, solo calor)",
                "tone": "50-60%",
                "mix": "40-60%",
                "low_cut": "OFF (queremos golpe gordo)",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion (modo COMP)",
            "settings": {
                "mode": "COMP",
                "ratio": "4:1",
                "attack": "15-30ms (dejar pasar el transiente = punch)",
                "release": "80-120ms",
                "threshold": "ajustar para -3 a -4dB de reduccion",
                "knee": "medio",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Soft Clipper",
            "purpose": "Control de picos",
            "settings": {
                "threshold": "por defecto",
                "post_gain": "-1dB",
                "note": "Solo para atrapar picos que se escapen",
            },
        },
    ],

    ("kick", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ (el sub lo pone el 808)",
            "settings": {
                "high_pass": "40Hz, 24dB/oct (el sub lo pone el 808)",
                "cut_1": "200-350Hz, -3dB (espacio para el 808)",
                "boost_1": "2-5kHz, +3-4dB, Q=1.5 (CLICK/ataque)",
                "low_pass": "10kHz, 12dB/oct (quitar ruido innecesario)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion agresiva",
            "settings": {
                "ratio": "6:1",
                "attack": "5-10ms (ataque mas corto)",
                "release": "50ms",
                "reduction": "-4 a -6dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Soft Clipper",
            "purpose": "Drive sutil para que el kick muerda",
            "settings": {
                "drive": "sutil",
            },
        },
    ],

    # ===================================================================
    # SNARE
    # ===================================================================
    ("snare", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "80Hz, 18dB/oct (quitar sub del sample)",
                "boost_1": "150-250Hz, +2dB, Q=1.5 (CUERPO de la snare)",
                "cut_1": "400-600Hz, -2dB (quitar caja de carton)",
                "boost_2": "2-4kHz, +2-3dB (CRACK/snap)",
                "boost_3": "8-12kHz, +1-2dB shelf (brillo/aire del vinilo)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Textura analoga, crunch de MPC",
            "settings": {
                "style": "A (American) o N (Neve)",
                "drive": "3-5",
                "tone": "60-70%",
                "mix": "30-50%",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion",
            "settings": {
                "ratio": "4:1",
                "attack": "5-15ms",
                "release": "50-80ms",
                "reduction": "-3 a -5dB",
            },
        },
    ],

    ("snare", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100Hz, 24dB/oct",
                "boost_1": "200Hz, +2dB (cuerpo del clap)",
                "cut_1": "500Hz, -2dB",
                "boost_2": "3-6kHz, +3dB (SNAP agresivo)",
                "high_shelf": "10kHz, +2dB (aire)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion",
            "settings": {
                "ratio": "4:1",
                "attack": "3-10ms (transiente rapido)",
                "release": "40-60ms",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Radiator",
            "purpose": "Calor sutil (opcional)",
            "settings": {
                "mix": "20-30%",
                "alt": "Soundtoys Devil-Loc para snares que aplastas",
            },
        },
    ],

    # ===================================================================
    # HI-HATS
    # ===================================================================
    ("hihats", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "200Hz, 18dB/oct",
                "cut_1": "1-3kHz, -2dB (si suena metalico agresivo)",
                "boost_1": "8-12kHz, +1-2dB shelf (brillo)",
                "low_pass": "14-16kHz (quitar ultrasonica innecesaria)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Textura (opcional)",
            "settings": {
                "style": "T (Tape)",
                "drive": "2-3 (MUY sutil)",
                "mix": "20-30%",
                "tone": "medio",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Limiter",
            "purpose": "Solo si hay picos inconsistentes",
            "settings": {
                "ratio": "3:1",
                "reduction": "-2dB (suave)",
            },
        },
    ],

    ("hihats", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ (son PURO agudo)",
            "settings": {
                "high_pass": "300Hz, 24dB/oct",
                "cut_1": "2-4kHz, -1 a -2dB (si son chillones)",
                "boost_1": "10-14kHz, +2-3dB shelf (crispy)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys MicroShift",
            "purpose": "Abrir estereo (opcional)",
            "settings": {
                "note": "SOLO en hats, no en kick/snare/bajo",
                "alt": "Fruity Stereo Enhancer: separacion al 30-40%",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresor ligero para rolls consistentes",
            "settings": {
                "ratio": "3:1",
                "attack": "1-3ms",
                "release": "30ms",
            },
        },
    ],

    # ===================================================================
    # PERCS (shared for both genres with genre-specific delay)
    # ===================================================================
    ("percs", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100-200Hz segun la pieza",
                "technique": "Sweep & destroy para buscar y cortar resonancias",
                "boost": "Boost sutil en la zona de ataque de cada pieza",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys PrimalTap / EchoBoy",
            "purpose": "Delay corto con saturacion = groove lo-fi",
            "settings": {
                "delay": "1/16",
                "mix": "10-20%",
                "feedback": "10-15%",
                "saturation": "activar",
            },
        },
    ],

    ("percs", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100-200Hz segun la pieza",
                "technique": "Sweep & destroy para buscar y cortar resonancias",
                "boost": "Boost sutil en la zona de ataque de cada pieza",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Delay 3",
            "purpose": "Delay limpio",
            "settings": {
                "sync": "ON",
                "division": "1/8 o 1/16",
                "feedback": "15-20%",
                "filter_lp": "6kHz",
            },
        },
    ],

    # ===================================================================
    # BASS (boom bap) -- sample bass, contrabajo, Rhodes bass
    # ===================================================================
    ("bass", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Limpieza",
            "settings": {
                "high_pass": "25-30Hz, 18dB/oct (quitar sub-frecuencias inutiles)",
                "cut_1": "300-500Hz, -2dB (quitar mud SI lo necesita)",
                "boost_1": "60-80Hz, +2-3dB (PESO del bajo)",
                "boost_2": "700Hz-1kHz, +1-2dB (articulacion/dedo, si es bajo real)",
                "low_pass": "5-8kHz (quitar ruido de high end innecesario)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Calor analogico (suena a bajo pasado por 4-track)",
            "settings": {
                "style": "T (Tape)",
                "drive": "3-4",
                "tone": "40-50% (no queremos brillo, queremos calor)",
                "mix": "30-50%",
                "low_cut": "OFF",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion",
            "settings": {
                "ratio": "4:1",
                "attack": "20-40ms (dejar el ataque del dedo/pick pasar)",
                "release": "80-150ms",
                "reduction": "-3 a -5dB",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Stereo Enhancer",
            "purpose": "MONO obligatorio para graves",
            "settings": {
                "stereo_separation": "0% para todo bajo 200Hz",
            },
        },
        {
            "slot": 5,
            "plugin_name": "Fruity Soft Clipper",
            "purpose": "Control de picos final",
            "settings": {},
        },
    ],

    # ===================================================================
    # 808 (trap) -- long, slide, distorted top / clean sub
    # ===================================================================
    ("808", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Pre-distorsion (limpiar antes de distorsionar)",
            "settings": {
                "high_pass": "28Hz, 24dB/oct (limpiar sub-sub)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "DISTORSION / rugido del 808",
            "settings": {
                "style": "A (American) para 808 agresivo",
                "drive": "4-7 (aqui esta el GROWL)",
                "tone": "60-80% (queremos que ruja arriba)",
                "mix": "50-80%",
                "low_cut": "ACTIVAR a 60-80Hz",
                "secret": "El low cut hace que distorsione SOLO medias/altas, "
                          "manteniendo el sub limpio. ESTO es el secreto del 808 "
                          "que ruge.",
            },
            "alternative": {
                "plugin_name": "Soundtoys Devil-Loc Deluxe",
                "purpose": "Compresion destructiva (808 que APLASTA)",
                "settings": {
                    "crush": "40-60%",
                    "crunch": "50-70%",
                    "mix": "30-50%",
                    "darkness": "al gusto",
                },
            },
        },
        {
            "slot": 3,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Post-distorsion",
            "settings": {
                "high_pass": "30Hz (limpiar artefactos de distorsion)",
                "boost_1": "55-70Hz, +2-3dB (peso que sientes en el pecho)",
                "boost_2": "150-250Hz, +2-3dB (cuerpo del rugido)",
                "cut_1": "400-600Hz, -2dB (zona carton)",
                "boost_3": "1-3kHz, +1-2dB (presencia del crack)",
                "low_pass": "8-10kHz (quitar ruido de distorsion)",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion",
            "settings": {
                "ratio": "4:1 a 8:1",
                "attack": "20-50ms (LENTO = deja el transiente)",
                "release": "50-100ms (RAPIDO = mantiene energia)",
                "reduction": "-3 a -6dB",
            },
        },
        {
            "slot": 5,
            "plugin_name": "Fruity Stereo Enhancer",
            "purpose": "MONO el sub, siempre",
            "settings": {
                "stereo_separation": "0% bajo 200Hz",
            },
        },
        {
            "slot": 6,
            "plugin_name": "Fruity Soft Clipper",
            "purpose": "Redondear picos = mas volumen percibido",
            "settings": {
                "technique": "Sube volumen del 808 hasta que el clipper trabaje",
                "trick": "Sube threshold, baja post-gain",
            },
        },
    ],

    # Sidechain config stored separately but referenced here
    ("808_sidechain", "trap"): [
        {
            "slot": "sidechain",
            "plugin_name": "Fruity Limiter",
            "purpose": "Sidechain 808 con kick (el 808 desaparece cuando pega el kick)",
            "settings": {
                "sidechain_source": "kick",
                "attack": "0.5ms",
                "release": "80-150ms (ajustar al tempo)",
                "ratio": "maximo",
            },
        },
    ],

    # ===================================================================
    # SAMPLE (boom bap vinyl chops)
    # ===================================================================
    ("sample", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "iZotope RX",
            "purpose": "Limpieza previa (hacer ANTES en Edison o standalone)",
            "settings": {
                "de_click": "quitar clicks y pops del vinilo (sutil, no eliminar todo)",
                "de_hum": "quitar 50/60Hz de hum electrico si lo hay",
                "de_noise": "MUY SUTIL (-5 a -10dB). No matar el ruido del vinilo, "
                            "ESE RUIDO ES PARTE DEL SONIDO.",
            },
        },
        {
            "slot": 2,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "40-60Hz, 18dB/oct (quitar rumble del vinilo)",
                "cut_1": "200-400Hz, -2 a -3dB (quitar mud del sample viejo)",
                "boost_1": "1-3kHz, +2dB (sacar los detalles del sample)",
                "high_shelf": "8-12kHz, +2-3dB (abrir el sample, que respire)",
                "note": "Si el sample ya es brillante, NO anadir mas brillo",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Textura analogica (suena a SP-1200 por cinta de 4 pistas)",
            "settings": {
                "style": "T (Tape) - EL CLASICO para boom bap",
                "drive": "2-4 (calor, no destruccion)",
                "tone": "50%",
                "mix": "30-50%",
            },
            "alternative": {
                "plugin_name": "Soundtoys Radiator",
                "purpose": "Emulacion de consola Altec. Calido, musical, lo-fi.",
                "settings": {
                    "input": "subir hasta que sature ligeramente",
                    "bass": "al gusto",
                    "treble": "sutil boost",
                    "mix": "40-60%",
                },
            },
        },
        {
            "slot": 4,
            "plugin_name": "Soundtoys FilterFreak",
            "purpose": "Efecto creativo (opcional) - simular vinilo sucio",
            "settings": {
                "type": "Low-pass",
                "automation": "Automatizar cutoff para efecto DJ",
                "resonance": "sutil (10-20%)",
            },
        },
        {
            "slot": 5,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion (suave, no aplastar la dinamica del sample)",
            "settings": {
                "ratio": "3:1",
                "attack": "15-25ms",
                "release": "100ms",
                "reduction": "-2 a -4dB",
            },
        },
        {
            "slot": 6,
            "plugin_name": "Fruity Stereo Enhancer",
            "purpose": "Abrir mono a estereo (opcional)",
            "settings": {
                "stereo_separation": "20-30% si el sample es mono; dejar si es estereo",
            },
        },
    ],

    # ===================================================================
    # MELODY (trap synthetic melodies)
    # ===================================================================
    ("melody", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "80-120Hz, 24dB/oct (dejar espacio al 808)",
                "cut_1": "200-400Hz, -2dB (quitar mud)",
                "boost_1": "2-5kHz, +2dB (presencia)",
                "high_shelf": "10kHz, +2-3dB (brillo/aire)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys MicroShift",
            "purpose": "Amplitud estereo (melodias envuelven, voz en centro)",
            "settings": {
                "detune": "5-10 cents (sutil)",
                "delay": "5-15ms entre L y R",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys EchoBoy",
            "purpose": "Delay con caracter (mejor que Fruity Delay por saturacion)",
            "settings": {
                "style": "Studio Tape o Cheap Tape",
                "tempo_sync": "ON",
                "division": "1/4 o 3/8",
                "mix": "15-25%",
                "feedback": "20-30%",
                "saturation": "sutil",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion suave",
            "settings": {
                "ratio": "3:1",
                "attack": "10-20ms",
                "release": "80ms",
                "reduction": "-2 a -3dB",
            },
        },
    ],

    # ===================================================================
    # PADS / TEXTURAS (both genres, with genre-specific slot 2)
    # ===================================================================
    ("pads", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100-200Hz (dejar espacio a kick/bajo)",
                "low_pass": "8-12kHz (no competir con voz/hats)",
                "cut_mid": "1-3kHz, -2dB (dejar espacio a la voz)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Crystallizer",
            "purpose": "Efecto creativo - pitch shift + delay granular = texturas lo-fi",
            "settings": {
                "mix": "20-40%",
                "splice": "al gusto",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Reeverb 2",
            "purpose": "Reverb largo (puede ser insert aqui, no necesita send)",
            "settings": {
                "decay": "3-5s",
                "damping": "4-6kHz",
                "mix": "30-50%",
            },
        },
    ],

    ("pads", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100-200Hz (dejar espacio a kick/bajo)",
                "low_pass": "8-12kHz (no competir con voz/hats)",
                "cut_mid": "1-3kHz, -2dB (dejar espacio a la voz)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Tremolator",
            "purpose": "Pads que respiran (tremolo sincronizado)",
            "settings": {
                "sync": "al tempo",
                "depth": "30-60%",
                "shape": "sine o triangle",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Fruity Reeverb 2",
            "purpose": "Reverb largo",
            "settings": {
                "decay": "3-5s",
                "damping": "4-6kHz",
                "mix": "30-50%",
            },
        },
    ],

    # ===================================================================
    # VOZ PRINCIPAL -- BOOM BAP (rap crudo)
    # ===================================================================
    ("vocal_main", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "iZotope RX",
            "purpose": "Limpieza previa (hacer PRIMERO)",
            "settings": {
                "voice_de_noise": "Learn perfil de ruido, reduccion -10 a -15dB",
                "de_click": "si hay clicks del micro",
                "mouth_de_click": "quitar chasquidos de saliva",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Antares Auto-Tune",
            "purpose": "Corrector SUTIL, casi imperceptible (si el MC tiene buen oido, saltar)",
            "settings": {
                "retune_speed": "50-80ms (MUY SUAVE)",
                "humanize": "60-80 (ALTO, queremos que suene NATURAL)",
                "key": "detectar o poner manual segun la instrumental",
            },
        },
        {
            "slot": 3,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ substractivo (limpieza)",
            "settings": {
                "high_pass": "80-100Hz, 24dB/oct (obligatorio)",
                "sweep_destroy_1": "200-400Hz, -2 a -3dB (mud)",
                "sweep_destroy_2": "400-800Hz, -1 a -2dB (boxiness)",
                "sweep_destroy_3": "2-4kHz, -1 a -2dB (harshness)",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion 1 - domando picos",
            "settings": {
                "ratio": "3:1",
                "attack": "10-15ms",
                "release": "80ms",
                "reduction": "-2 a -3dB (SUAVE, solo los picos)",
            },
        },
        {
            "slot": 5,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion 2 - control de dinamica (serial comp: 2 suaves > 1 agresivo)",
            "settings": {
                "ratio": "4:1",
                "attack": "15-25ms",
                "release": "100ms",
                "reduction": "-3 a -4dB",
            },
        },
        {
            "slot": 6,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ aditivo (brillo)",
            "settings": {
                "boost_1": "2.5-4kHz, +2-3dB, Q=1 (PRESENCIA, que se entienda cada palabra)",
                "boost_2": "8-12kHz, +2-3dB high shelf (AIRE, apertura)",
                "boost_3": "200-300Hz, +1dB (calidez, solo si suena fina)",
            },
        },
        {
            "slot": 7,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion vocal (suena a estudio de los 90s)",
            "settings": {
                "style": "A (American)",
                "drive": "2-4 (sutil a medio)",
                "tone": "55-65%",
                "mix": "30-50%",
                "low_cut": "activar a 100Hz",
            },
        },
        {
            "slot": 8,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "De-esser manual",
            "settings": {
                "band": "5-8kHz, modo dinamico",
                "threshold": "ajustar para que solo actue en las S",
                "reduction": "-3 a -6dB",
                "alt": "Fruity Limiter como de-esser",
            },
        },
        {
            "slot": 9,
            "plugin_name": "Fruity Limiter",
            "purpose": "Limiter final (proteccion)",
            "settings": {
                "mode": "LIMIT",
                "ceiling": "-0.3dB",
                "note": "Solo proteccion, no debe estar trabajando constantemente",
            },
        },
    ],

    # ===================================================================
    # VOZ PRINCIPAL -- TRAP (autotune / melodica)
    # ===================================================================
    ("vocal_main", "trap"): [
        {
            "slot": 1,
            "plugin_name": "iZotope RX",
            "purpose": "Limpieza previa",
            "settings": {
                "voice_de_noise": "-10 a -20dB",
                "mouth_de_click": "activar",
                "de_reverb": "si la grabacion tiene reverb de sala no deseado",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Antares Auto-Tune",
            "purpose": "Efecto autotune evidente / T-Pain effect",
            "settings": {
                "retune_speed": "0-20ms (RAPIDO = efecto autotune evidente)",
                "humanize": "0-30 (BAJO para trap)",
                "flex_tune": "0-20 (hard tune)",
                "key": "segun la instrumental",
                "tracking": "Relaxed",
                "t_pain_preset": "Retune Speed 0, Humanize 0, Flex-Tune 0 "
                                 "(correccion instantanea = sonido robotico/melodico clasico)",
            },
        },
        {
            "slot": 3,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ substractivo",
            "settings": {
                "high_pass": "90-110Hz, 24dB/oct",
                "cut_1": "250Hz, -2dB (mud)",
                "cut_2": "500Hz, -1.5dB (boxiness)",
                "sweep_destroy": "buscar y cortar resonancias",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion fuerte",
            "settings": {
                "ratio": "6:1 a 8:1 (agresivo para trap)",
                "attack": "5-15ms",
                "release": "50-80ms",
                "reduction": "-4 a -6dB",
            },
        },
        {
            "slot": 5,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ aditivo (voz trap es MAS brillante que boom bap)",
            "settings": {
                "boost_1": "3-5kHz, +3dB (presencia agresiva)",
                "high_shelf": "10-14kHz, +3-4dB (AIRE, el brillo del trap)",
            },
        },
        {
            "slot": 6,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion",
            "settings": {
                "style": "E (Ampex) para trap agresivo",
                "drive": "3-5",
                "tone": "65-75%",
                "mix": "40-60%",
                "low_cut": "100Hz",
            },
        },
        {
            "slot": 7,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "De-esser (especialmente necesario despues de tanto boost en agudos)",
            "settings": {
                "band": "5-9kHz, modo Dynamic EQ",
            },
        },
        {
            "slot": 8,
            "plugin_name": "Soundtoys Little AlterBoy",
            "purpose": "Efecto creativo (opcional)",
            "settings": {
                "pitch_shift": "para efecto vocal unico",
                "formant_shift": "cambiar caracter de la voz",
                "drive": "sutil",
                "mix": "20-40% para efecto parcial, 100% para efecto completo",
                "note": "Util para ad-libs y partes especificas",
            },
        },
        {
            "slot": 9,
            "plugin_name": "Fruity Limiter",
            "purpose": "Limiter final",
            "settings": {
                "ceiling": "-0.3dB",
            },
        },
    ],

    # ===================================================================
    # DOBLES / COROS (both genres)
    # ===================================================================
    ("doubles", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ (high-pass mas alto que la voz principal)",
            "settings": {
                "high_pass": "100-150Hz",
                "cut_1": "1-3kHz, -2dB (que la principal domine en presencia)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion media",
            "settings": {
                "ratio": "4:1",
                "reduction": "-3 a -5dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys MicroShift",
            "purpose": "Abrir estereo (dobles a los lados, principal en centro)",
            "settings": {
                "detune_delay": "sutil entre L y R",
            },
        },
    ],

    ("doubles", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "100-150Hz",
                "cut_1": "1-3kHz, -2dB (que la principal domine en presencia)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion media",
            "settings": {
                "ratio": "4:1",
                "reduction": "-3 a -5dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys MicroShift",
            "purpose": "Abrir estereo",
            "settings": {
                "detune_delay": "sutil entre L y R",
            },
        },
    ],

    # ===================================================================
    # AD-LIBS (both genres)
    # ===================================================================
    ("adlibs", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ (solo textura, quitar todo grave)",
            "settings": {
                "high_pass": "150-200Hz",
                "boost_1": "3-5kHz, +2dB",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Comprimir bastante para consistencia",
            "settings": {
                "ratio": "6:1",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys EchoBoy / Crystallizer",
            "purpose": "Efecto creativo (mas efecto que la voz principal)",
            "settings": {
                "note": "Mas delay y reverb que la voz principal",
            },
        },
    ],

    ("adlibs", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ",
            "settings": {
                "high_pass": "150-200Hz",
                "boost_1": "3-5kHz, +2dB",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Comprimir bastante para consistencia",
            "settings": {
                "ratio": "6:1",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys EchoBoy / Crystallizer",
            "purpose": "Efecto creativo (mas efecto que la voz principal)",
            "settings": {
                "note": "Mas delay, reverb y feedback que la voz principal",
            },
        },
    ],

    # ===================================================================
    # BUS DRUMS
    # ===================================================================
    ("bus_drums", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ correctivo del grupo",
            "settings": {
                "note": "Ajustes sutiles para balancear el grupo completo",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion de grupo / glue (que respire)",
            "settings": {
                "ratio": "2:1 a 3:1 (SUAVE)",
                "attack": "20-30ms (dejar todos los transientes)",
                "release": "100-150ms",
                "reduction": "-1 a -3dB",
                "knee": "soft",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion del grupo (TODO suena a SP-1200 por cinta)",
            "settings": {
                "style": "T (Tape)",
                "drive": "2-4",
                "mix": "30-50%",
            },
        },
        {
            "slot": 4,
            "plugin_name": "Soundtoys Devil-Loc Deluxe",
            "purpose": "Compresion paralela (SMASH de cinta, drums ENORMES)",
            "settings": {
                "crush": "30-50%",
                "mix": "15-25% (mezcla paralela)",
                "darkness": "40-60%",
            },
        },
    ],

    ("bus_drums", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ correctivo del grupo",
            "settings": {
                "note": "Ajustes sutiles para balancear el grupo completo",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Compresion de grupo / glue",
            "settings": {
                "ratio": "3:1 a 4:1",
                "attack": "10-20ms",
                "release": "60-100ms",
                "reduction": "-2 a -4dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion del grupo (mas sutil en trap)",
            "settings": {
                "style": "A (American) o N (Neve)",
                "drive": "2-3",
                "mix": "20-35%",
            },
        },
    ],

    # ===================================================================
    # BUS MELODIAS
    # ===================================================================
    ("bus_melody", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Sidechain EQ desde la voz / corte estatico para espacio vocal",
            "settings": {
                "sidechain_dynamic_cut": "2-5kHz, activado por la voz (Mid/Side)",
                "static_alternative": "corte sutil en 2-4kHz, -2dB",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Glue compresion",
            "settings": {
                "ratio": "2:1 a 3:1",
                "reduction": "-2 a -3dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Radiator",
            "purpose": "Calor global (todo el bloque melodico unificado y calido)",
            "settings": {
                "mix": "20-30%",
                "alt": "Decapitator Style T muy sutil",
            },
        },
    ],

    ("bus_melody", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Sidechain EQ desde la voz / corte estatico",
            "settings": {
                "sidechain_dynamic_cut": "2-5kHz, activado por la voz",
                "static_alternative": "corte sutil en 2-4kHz, -2dB",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Glue compresion",
            "settings": {
                "ratio": "2:1 a 3:1",
                "reduction": "-2 a -3dB",
            },
        },
    ],

    # ===================================================================
    # BUS VOCES
    # ===================================================================
    ("bus_vocals", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Ajuste final de voces (cortar donde se pisen con melodias)",
            "settings": {
                "note": "Ajustes finos tras escuchar todo junto",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Glue compresion (MUY SUAVE, solo pegar el grupo)",
            "settings": {
                "ratio": "2:1",
                "attack": "15ms",
                "release": "80ms",
                "reduction": "-1 a -2dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion de cohesion (todas las voces del mismo mundo)",
            "settings": {
                "drive": "2-3",
                "mix": "20-30%",
                "note": "SUTIL",
            },
        },
    ],

    ("bus_vocals", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "Ajuste final de voces",
            "settings": {
                "note": "Ajustes finos tras escuchar todo junto",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Fruity Limiter",
            "purpose": "Glue compresion",
            "settings": {
                "ratio": "2:1",
                "attack": "15ms",
                "release": "80ms",
                "reduction": "-1 a -2dB",
            },
        },
        {
            "slot": 3,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion de cohesion",
            "settings": {
                "drive": "2-3",
                "mix": "20-30%",
            },
        },
    ],

    # ===================================================================
    # MASTER
    # ===================================================================
    ("master", "boom_bap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ correctivo (maximo +/- 1.5dB en cualquier banda)",
            "settings": {
                "high_pass": "25Hz, 18dB/oct (limpiar sub-sub)",
                "cut_1": "300Hz, -1dB (si hay acumulacion de mud)",
                "boost_1": "100Hz, +1dB (si falta peso)",
                "boost_2": "12kHz, +1dB high shelf (si falta aire)",
                "note": "Si necesitas mover mas de 2dB, hazlo en los canales individuales",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion de master (EL SONIDO de los 90s)",
            "settings": {
                "style": "T (Tape)",
                "drive": "1.5-3 (MUY SUTIL en master)",
                "tone": "50%",
                "mix": "20-35%",
                "low_cut": "OFF",
                "note": "Pega toda la mezcla como si hubiera pasado por cinta. "
                        "Diferencia entre 'suena a computadora' y 'suena a DISCO'.",
            },
        },
        {
            "slot": 3,
            "plugin_name": "iZotope Ozone 12",
            "purpose": "Mastering suite (modulos individuales en orden)",
            "modules": [
                {
                    "name": "Ozone EQ (Match EQ opcional)",
                    "settings": {
                        "match_eq": "Comparar curva con referencia profesional boom bap",
                        "adjustment": "MUY sutiles post-match, maximo +/-1dB",
                        "note": "Si no usas Match EQ, saltar (ya tienes el Pro-Q arriba)",
                    },
                },
                {
                    "name": "Ozone Dynamic EQ",
                    "settings": {
                        "band_1": "200-400Hz: compresion dinamica -1 a -2dB (mud solo cuando se acumula)",
                        "band_2": "3-5kHz: compresion dinamica -1dB (harshness solo en picos)",
                        "band_3": "8-12kHz: expansion dinamica +1dB (aire cuando la mezcla se comprime)",
                    },
                },
                {
                    "name": "Ozone Vintage Compressor",
                    "settings": {
                        "mode": "Analog",
                        "threshold": "ajustar para -1 a -2dB de reduccion",
                        "ratio": "bajo (suave)",
                        "attack": "lento (20ms+)",
                        "release": "auto",
                        "mix": "60-80% (compresion paralela en el master)",
                        "note": "Para boom bap queremos POCA compresion. Que RESPIRE.",
                    },
                },
                {
                    "name": "Ozone Vintage Tape",
                    "settings": {
                        "input_drive": "sutil (2-3dB max)",
                        "bias": "al gusto",
                        "speed": "15ips (mas limpio) o 7.5ips (mas calor)",
                        "note": "DOBLE capa de cinta (Decapitator + Ozone Tape) = boom bap PURO",
                    },
                },
                {
                    "name": "Ozone Imager",
                    "settings": {
                        "band_low_0_200Hz": "MONO o casi mono (0-10% width)",
                        "band_mid_200_2kHz": "Stereo natural (90-110%)",
                        "band_high_2kHz_plus": "Ligeramente mas ancho (110-130%)",
                        "note": "NUNCA exagerar. Si suena raro en mono, reduce el width.",
                    },
                },
                {
                    "name": "Ozone Maximizer",
                    "settings": {
                        "mode": "IRC IV (transparente)",
                        "ceiling": "-1.0dB (boom bap deja MAS headroom que trap)",
                        "threshold": "ajustar para que reduzca MAXIMO -3 a -4dB",
                        "target_lufs": "-10 a -12 LUFS",
                        "character": "0-20%",
                        "note": "Boom bap es MAS DINAMICO que trap. No aplastar.",
                    },
                },
            ],
        },
    ],

    ("master", "trap"): [
        {
            "slot": 1,
            "plugin_name": "FabFilter Pro-Q 3",
            "purpose": "EQ correctivo (todo SUTIL, maximo +/-2dB)",
            "settings": {
                "high_pass": "25Hz, 24dB/oct (limpieza de sub-sub)",
                "cut_1": "200-350Hz, -1dB (si hay mud)",
                "boost_1": "50-70Hz, +1dB (si falta peso del 808)",
                "boost_2": "12-14kHz, +1-2dB high shelf (brillo/aire moderno)",
            },
        },
        {
            "slot": 2,
            "plugin_name": "Soundtoys Decapitator",
            "purpose": "Saturacion de master (OPCIONAL en trap, menos importante que en boom bap)",
            "settings": {
                "style": "A (American) o N (Neve)",
                "drive": "1.5-2.5 (MUY SUTIL)",
                "mix": "15-25%",
                "note": "Si prefieres un master limpio, SALTA este paso",
            },
        },
        {
            "slot": 3,
            "plugin_name": "iZotope Ozone 12",
            "purpose": "Mastering suite (modulos individuales en orden)",
            "modules": [
                {
                    "name": "Ozone Dynamic EQ",
                    "settings": {
                        "band_low": "40-80Hz: expansion dinamica +1-2dB (acentua 808 cuando pega)",
                        "band_mid_low": "200-400Hz: compresion dinamica -1 a -2dB (mud)",
                        "band_mid_high": "3-6kHz: compresion dinamica -1dB (harshness voz/snare)",
                        "band_high": "8-14kHz: expansion +1dB (aire dinamico)",
                    },
                },
                {
                    "name": "Ozone Dynamics (compresor multibanda)",
                    "settings": {
                        "bands": "3 o 4 bandas",
                        "band_low_20_120Hz": "Ratio 2:1, attack LENTO (30ms), release rapido "
                                             "(el 808 pega y se mantiene)",
                        "band_mid_120Hz_5kHz": "Ratio 3:1, attack 10ms, release 80ms "
                                               "(control de voces y melodias)",
                        "band_high_5kHz_plus": "Ratio 2:1, attack 5ms, release 50ms "
                                               "(control de hats y brillo)",
                        "max_reduction_per_band": "-2 a -3dB",
                    },
                },
                {
                    "name": "Ozone Exciter (opcional)",
                    "settings": {
                        "band_high": "Tape o Retro, amount sutil",
                        "purpose": "Armonicos al high-end = brillo sin EQ",
                        "note": "No exagerar, puede sonar metalico",
                    },
                },
                {
                    "name": "Ozone Imager",
                    "settings": {
                        "band_low_0_200Hz": "MONO (0-5% width) - CRITICO para 808",
                        "band_mid_200_2kHz": "Stereo natural (95-110%)",
                        "band_high_2kHz_plus": "Abierto (120-140%) - mas ancho que boom bap",
                        "note": "En trap se busca un sonido mas amplio y envolvente",
                    },
                },
                {
                    "name": "Ozone Maximizer",
                    "settings": {
                        "mode": "IRC IV",
                        "ceiling": "-0.5dB (mas agresivo que boom bap)",
                        "threshold": "ajustar para que reduzca -4 a -6dB",
                        "target_lufs": "-8 a -10 LUFS",
                        "character": "20-50%",
                        "transient_emphasis": "activar para preservar punch del kick/snare",
                        "note": "Trap es MAS ALTO y MAS COMPRIMIDO que boom bap",
                    },
                },
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# 3. SEND_CONFIGS -- per genre with reverb, delay, parallel compression
# ---------------------------------------------------------------------------

SEND_CONFIGS = {
    "boom_bap": {
        "vox_reverb": {
            "insert": 103,
            "plugin_name": "Fruity Reeverb 2",
            "wet": "100%",
            "settings": {
                "type": "Room o Plate",
                "decay": "1.0-1.5s (CORTO para boom bap, la voz es seca)",
                "pre_delay": "20-30ms",
                "damping": "5-7kHz",
                "send_level": "BAJO, 15-25% (el reverb acompana, no domina)",
            },
        },
        "vox_delay": {
            "insert": 104,
            "plugin_name": "Soundtoys EchoBoy",
            "wet": "100%",
            "settings": {
                "style": "Studio Tape (calor analogico en las repeticiones)",
                "sync": "ON, 1/4 o 3/8",
                "feedback": "20-30%",
                "mix": "100% (esta en send)",
                "send_level": "15-25%",
                "post_eq": "FabFilter Pro-Q despues: cortar <200Hz y >6kHz del delay "
                           "(el delay acompana sin competir)",
            },
        },
        "drum_reverb": {
            "insert": 105,
            "plugin_name": "Fruity Reeverb 2",
            "wet": "100%",
            "settings": {
                "type": "Room",
                "decay": "0.8-1.2s",
                "damping": "5kHz",
                "send_level": "10-20%",
            },
        },
        "parallel_compression": {
            "note": "Via Soundtoys Devil-Loc Deluxe en Bus Drums (slot 4)",
            "settings": {
                "crush": "30-50%",
                "mix": "15-25% (mezcla paralela)",
                "darkness": "40-60%",
            },
        },
    },
    "trap": {
        "vox_reverb": {
            "insert": 103,
            "plugin_name": "Fruity Reeverb 2",
            "wet": "100%",
            "settings": {
                "type": "Plate",
                "decay": "1.2-2.0s (mas largo que boom bap)",
                "pre_delay": "25-40ms",
                "damping": "5-8kHz",
                "send_level": "20-35%",
            },
        },
        "vox_delay": {
            "insert": 104,
            "plugin_name": "Soundtoys EchoBoy",
            "wet": "100%",
            "settings": {
                "style": "Digital o Studio Tape",
                "sync": "ON, 1/4",
                "feedback": "25-35%",
                "send_level": "20-30%",
            },
        },
        "drum_reverb": {
            "insert": 105,
            "plugin_name": "Fruity Reeverb 2",
            "wet": "100%",
            "settings": {
                "type": "Plate",
                "decay": "0.5-0.8s",
                "damping": "6kHz",
                "send_level": "10-15%",
            },
        },
    },
}


# ---------------------------------------------------------------------------
# 4. MIX_LEVELS -- relative levels and panning per element per genre
# ---------------------------------------------------------------------------

MIX_LEVELS = {
    "boom_bap": {
        "kick": {
            "level": "0dB (reference)",
            "pan": "C (center)",
            "notes": "El kick es la referencia; todo se mezcla relativo a el.",
        },
        "snare": {
            "level": "-1 a -2dB respecto al kick",
            "pan": "C (center)",
            "notes": "Crujiente, con cuerpo y cola. Suena a vinilo.",
        },
        "hihats": {
            "level": "-4 a -6dB respecto al kick",
            "pan": "ligeramente off-center (10-20% L o R)",
            "notes": "Samples de vinilo real, no sinteticos.",
        },
        "percs": {
            "level": "-6 a -8dB respecto al kick",
            "pan": "variado (20-50% L y R)",
            "notes": "Congas, bongos, shakers distribuidos en estereo.",
        },
        "bass": {
            "level": "-2 a -4dB respecto al kick",
            "pan": "C (center, MONO obligatorio bajo 200Hz)",
            "notes": "Bajo de sample: contrabajo, bajo electrico, Rhodes bass. Calido, redondo.",
        },
        "sample": {
            "level": "-4 a -6dB respecto al kick",
            "pan": "estereo natural del sample",
            "notes": "Chops de vinilo, soul, jazz, funk. EL ALMA del boom bap.",
        },
        "pads": {
            "level": "-8 a -10dB respecto al kick",
            "pan": "wide (estereo)",
            "notes": "Texturas y atmosferas. No deben dominar.",
        },
        "vocal_main": {
            "level": "+2 a +4dB respecto a la instrumental",
            "pan": "C (center)",
            "notes": "Directa, cruda, con caracter. Se entiende cada palabra.",
        },
        "doubles": {
            "level": "-6 a -10dB respecto a la voz principal",
            "pan": "30-70% L y R (una copia a cada lado)",
            "notes": "Abiertas a los lados, principal en centro.",
        },
        "adlibs": {
            "level": "-8 a -12dB respecto a la voz principal",
            "pan": "variado, 20-80% L y R (que se muevan)",
            "notes": "Mas reverb y delay que la voz principal.",
        },
    },
    "trap": {
        "kick": {
            "level": "0dB (reference, pero subordinado al 808)",
            "pan": "C (center)",
            "notes": "Solo transiente corto que trabaja con el 808.",
        },
        "snare": {
            "level": "-1 a -2dB respecto al kick",
            "pan": "C (center)",
            "notes": "Clap electronico, snap agresivo.",
        },
        "hihats": {
            "level": "-5 a -7dB respecto al kick",
            "pan": "ligeramente off-center o con auto-pan",
            "notes": "Rapidos (rolls), limpios, con mucho movimiento.",
        },
        "percs": {
            "level": "-6 a -8dB respecto al kick",
            "pan": "variado (30-60% L y R)",
            "notes": "Distribuidos para crear width.",
        },
        "808": {
            "level": "0 a +2dB (EL elemento principal, EL BAJO ES EL BEAT)",
            "pan": "C (center, MONO obligatorio bajo 200Hz)",
            "notes": "Largo, con slide, distorsionado arriba pero limpio abajo.",
        },
        "melody": {
            "level": "-4 a -6dB respecto al 808",
            "pan": "wide (MicroShift abre estereo)",
            "notes": "Dark, repetitivas, hipnoticas. Pianos, bells, pads, arps.",
        },
        "pads": {
            "level": "-8 a -10dB respecto al 808",
            "pan": "wide (estereo)",
            "notes": "Texturas y atmosferas de fondo.",
        },
        "vocal_main": {
            "level": "+2 a +4dB respecto a la instrumental",
            "pan": "C (center)",
            "notes": "Procesada, con autotune notable, saturacion, compresion agresiva.",
        },
        "doubles": {
            "level": "-6 a -10dB respecto a la voz principal",
            "pan": "30-70% L y R",
            "notes": "Abiertas a los lados.",
        },
        "adlibs": {
            "level": "-8 a -12dB respecto a la voz principal",
            "pan": "variado, 20-80% L y R",
            "notes": "Mas reverb y delay; pueden tener efecto creativo.",
        },
    },
}


# ---------------------------------------------------------------------------
# 5. GAIN_STAGING_GUIDE
# ---------------------------------------------------------------------------

GAIN_STAGING_GUIDE = {
    "title": "GAIN STAGING - LA BASE DE TODO",
    "rule": "Antes de poner UN SOLO plugin, cada canal del mixer debe piquear "
            "entre -18 y -12 dBFS.",
    "reason": "Esto garantiza que los plugins trabajen en su rango optimo.",
    "steps": [
        "1. Reproduce el proyecto sin plugins.",
        "2. Cada canal individual: ajusta el fader para que piquee a -12dBFS.",
        "3. El master debe quedar entre -6 y -3dBFS ANTES de mastering.",
        "4. Si el master clipea, baja TODOS los faders proporcionalmente.",
    ],
    "channel_target": "-18 a -12 dBFS por canal",
    "master_target_pre_mastering": "-6 a -3 dBFS",
    "common_mistakes": [
        "Si la senal entra al plugin a +6dB, va a distorsionar.",
        "Si entra a -30dB, va a sonar con ruido.",
        "SIEMPRE calibrar niveles ANTES de meter plugins.",
    ],
}


# ---------------------------------------------------------------------------
# 6. MASTERING_CHAINS -- per genre (detailed, mirrors PLUGIN_CHAINS master keys)
# ---------------------------------------------------------------------------

MASTERING_CHAINS = {
    "boom_bap": {
        "philosophy": "CALIDEZ, DINAMICA, TEXTURA ANALOGICA. "
                      "El master boom bap no aplasta. Respira. Suena a vinilo.",
        "prerequisite": "La mezcla tiene que sonar BIEN sin nada en el master. "
                        "Si necesitas arreglar algo, vuelve a los canales individuales. "
                        "El master debe recibir la senal picando entre -6 y -3dBFS.",
        "chain": [
            {
                "slot": 1,
                "plugin": "FabFilter Pro-Q 3",
                "purpose": "EQ correctivo",
                "settings": {
                    "high_pass": "25Hz, 18dB/oct",
                    "cut_mud": "300Hz, -1dB",
                    "boost_weight": "100Hz, +1dB",
                    "boost_air": "12kHz, +1dB high shelf",
                    "max_adjustment": "+/- 1.5dB en cualquier banda",
                },
            },
            {
                "slot": 2,
                "plugin": "Soundtoys Decapitator",
                "purpose": "Saturacion de master (cinta)",
                "settings": {
                    "style": "T (Tape)",
                    "drive": "1.5-3",
                    "tone": "50%",
                    "mix": "20-35%",
                    "low_cut": "OFF",
                },
            },
            {
                "slot": "3a",
                "plugin": "Ozone 12 - EQ (Match EQ)",
                "purpose": "Match con referencia profesional (opcional)",
                "settings": {
                    "max_adjustment": "+/-1dB post-match",
                },
            },
            {
                "slot": "3b",
                "plugin": "Ozone 12 - Dynamic EQ",
                "purpose": "Control dinamico por banda",
                "settings": {
                    "band_200_400Hz": "compresion dinamica -1 a -2dB (mud)",
                    "band_3_5kHz": "compresion dinamica -1dB (harshness)",
                    "band_8_12kHz": "expansion dinamica +1dB (aire)",
                },
            },
            {
                "slot": "3c",
                "plugin": "Ozone 12 - Vintage Compressor",
                "purpose": "Compresion paralela de master",
                "settings": {
                    "mode": "Analog",
                    "reduction": "-1 a -2dB",
                    "ratio": "bajo",
                    "attack": "lento (20ms+)",
                    "release": "auto",
                    "mix": "60-80%",
                },
            },
            {
                "slot": "3d",
                "plugin": "Ozone 12 - Vintage Tape",
                "purpose": "Doble capa de cinta (boom bap PURO)",
                "settings": {
                    "input_drive": "2-3dB max",
                    "bias": "al gusto",
                    "speed": "15ips (limpio) o 7.5ips (calor)",
                },
            },
            {
                "slot": "3e",
                "plugin": "Ozone 12 - Imager",
                "purpose": "Control estereo",
                "settings": {
                    "low_0_200Hz": "MONO (0-10% width)",
                    "mid_200_2kHz": "natural (90-110%)",
                    "high_2kHz_plus": "ligeramente ancho (110-130%)",
                },
            },
            {
                "slot": "3f",
                "plugin": "Ozone 12 - Maximizer",
                "purpose": "Limiter final",
                "settings": {
                    "mode": "IRC IV",
                    "ceiling": "-1.0dB",
                    "max_reduction": "-3 a -4dB",
                    "target_lufs": "-10 a -12 LUFS",
                    "character": "0-20%",
                },
            },
        ],
        "export": {
            "format": "WAV",
            "bit_depth": "24-bit",
            "sample_rate_music": "44100 Hz",
            "sample_rate_video": "48000 Hz",
            "dithering": "activar en Ozone Maximizer si bajas a 16-bit",
        },
    },
    "trap": {
        "philosophy": "POTENCIA, VOLUMEN, IMPACTO. PESO ENORME. "
                      "El master trap golpea fuerte pero sigue sonando limpio.",
        "prerequisite": "La mezcla tiene que sonar BIEN sin nada en el master. "
                        "El master debe recibir la senal picando entre -6 y -3dBFS.",
        "chain": [
            {
                "slot": 1,
                "plugin": "FabFilter Pro-Q 3",
                "purpose": "EQ correctivo",
                "settings": {
                    "high_pass": "25Hz, 24dB/oct",
                    "cut_mud": "200-350Hz, -1dB",
                    "boost_808": "50-70Hz, +1dB",
                    "boost_air": "12-14kHz, +1-2dB high shelf",
                    "max_adjustment": "+/-2dB",
                },
            },
            {
                "slot": 2,
                "plugin": "Soundtoys Decapitator (OPCIONAL)",
                "purpose": "Saturacion de master (menos importante en trap)",
                "settings": {
                    "style": "A (American) o N (Neve)",
                    "drive": "1.5-2.5",
                    "mix": "15-25%",
                },
            },
            {
                "slot": "3a",
                "plugin": "Ozone 12 - Dynamic EQ",
                "purpose": "Control dinamico por banda",
                "settings": {
                    "band_40_80Hz": "expansion dinamica +1-2dB (acentuar 808)",
                    "band_200_400Hz": "compresion dinamica -1 a -2dB (mud)",
                    "band_3_6kHz": "compresion dinamica -1dB (harshness)",
                    "band_8_14kHz": "expansion +1dB (aire)",
                },
            },
            {
                "slot": "3b",
                "plugin": "Ozone 12 - Dynamics (multibanda)",
                "purpose": "Compresor multibanda",
                "settings": {
                    "band_low_20_120Hz": "Ratio 2:1, attack 30ms, release rapido",
                    "band_mid_120Hz_5kHz": "Ratio 3:1, attack 10ms, release 80ms",
                    "band_high_5kHz_plus": "Ratio 2:1, attack 5ms, release 50ms",
                    "max_reduction": "-2 a -3dB por banda",
                },
            },
            {
                "slot": "3c",
                "plugin": "Ozone 12 - Exciter (opcional)",
                "purpose": "Brillo sin EQ (armonicos)",
                "settings": {
                    "band_high": "Tape o Retro, amount sutil",
                },
            },
            {
                "slot": "3d",
                "plugin": "Ozone 12 - Imager",
                "purpose": "Control estereo",
                "settings": {
                    "low_0_200Hz": "MONO (0-5% width) - CRITICO para 808",
                    "mid_200_2kHz": "natural (95-110%)",
                    "high_2kHz_plus": "abierto (120-140%)",
                },
            },
            {
                "slot": "3e",
                "plugin": "Ozone 12 - Maximizer",
                "purpose": "Limiter final",
                "settings": {
                    "mode": "IRC IV",
                    "ceiling": "-0.5dB",
                    "reduction": "-4 a -6dB",
                    "target_lufs": "-8 a -10 LUFS",
                    "character": "20-50%",
                    "transient_emphasis": "activar",
                },
            },
        ],
        "export": {
            "format": "WAV",
            "bit_depth": "24-bit",
            "sample_rate_music": "44100 Hz",
            "sample_rate_video": "48000 Hz",
            "dithering": "activar en Ozone Maximizer si bajas a 16-bit",
        },
    },
}


# ---------------------------------------------------------------------------
# 7. LUFS_TARGETS -- per platform
# ---------------------------------------------------------------------------

LUFS_TARGETS = {
    "spotify": {
        "lufs": -14,
        "note": "Normaliza a -14 LUFS",
    },
    "apple_music": {
        "lufs": -16,
        "note": "Normaliza a -16 LUFS",
    },
    "youtube": {
        "lufs": -14,
        "note": "Normaliza a -14 LUFS",
    },
    "soundcloud": {
        "lufs": None,
        "note": "No normaliza (puedes ir mas alto)",
    },
    "club_dj": {
        "lufs": "-6 a -8",
        "note": "Mucho mas alto; hacer un master separado",
    },
    "recommendation": {
        "streaming": "Masteriza a -10 a -12 LUFS. Las plataformas bajaran el volumen "
                     "pero preservaras dinamica.",
        "dj_club": "Hacer un master separado mas alto (-6 a -8 LUFS).",
        "boom_bap_target": "-10 a -12 LUFS (mas dinamico)",
        "trap_target": "-8 a -10 LUFS (mas comprimido)",
    },
}


# ---------------------------------------------------------------------------
# 8. EQ_FREQUENCY_GUIDE -- per element, what frequencies to cut/boost and why
# ---------------------------------------------------------------------------

EQ_FREQUENCY_GUIDE = {
    "kick": {
        "boom_bap": {
            "high_pass": {"freq": "30Hz", "slope": "18dB/oct", "why": "Quitar sub-rumble del sample"},
            "cut_1": {"freq": "300-400Hz", "gain": "-2dB", "Q": 2, "why": "Quitar carton"},
            "boost_1": {"freq": "60-80Hz", "gain": "+2dB", "Q": 1.5, "why": "Peso del kick"},
            "boost_2": {"freq": "3-5kHz", "gain": "+2-3dB", "Q": 1, "why": "Ataque/punch"},
        },
        "trap": {
            "high_pass": {"freq": "40Hz", "slope": "24dB/oct", "why": "El sub lo pone el 808"},
            "cut_1": {"freq": "200-350Hz", "gain": "-3dB", "why": "Espacio para el 808"},
            "boost_1": {"freq": "2-5kHz", "gain": "+3-4dB", "Q": 1.5, "why": "CLICK/ataque"},
            "low_pass": {"freq": "10kHz", "slope": "12dB/oct", "why": "Quitar ruido innecesario"},
        },
    },
    "snare": {
        "boom_bap": {
            "high_pass": {"freq": "80Hz", "slope": "18dB/oct", "why": "Quitar sub del sample"},
            "boost_1": {"freq": "150-250Hz", "gain": "+2dB", "Q": 1.5, "why": "CUERPO de la snare"},
            "cut_1": {"freq": "400-600Hz", "gain": "-2dB", "why": "Quitar caja de carton"},
            "boost_2": {"freq": "2-4kHz", "gain": "+2-3dB", "why": "CRACK/snap"},
            "boost_3": {"freq": "8-12kHz", "gain": "+1-2dB", "type": "shelf", "why": "Brillo/aire del vinilo"},
        },
        "trap": {
            "high_pass": {"freq": "100Hz", "slope": "24dB/oct", "why": "Limpieza"},
            "boost_1": {"freq": "200Hz", "gain": "+2dB", "why": "Cuerpo del clap"},
            "cut_1": {"freq": "500Hz", "gain": "-2dB", "why": "Limpieza"},
            "boost_2": {"freq": "3-6kHz", "gain": "+3dB", "why": "SNAP agresivo"},
            "high_shelf": {"freq": "10kHz", "gain": "+2dB", "why": "Aire"},
        },
    },
    "hihats": {
        "boom_bap": {
            "high_pass": {"freq": "200Hz", "slope": "18dB/oct", "why": "Quitar frecuencias innecesarias"},
            "cut_1": {"freq": "1-3kHz", "gain": "-2dB", "why": "Si suena metalico agresivo"},
            "boost_1": {"freq": "8-12kHz", "gain": "+1-2dB", "type": "shelf", "why": "Brillo"},
            "low_pass": {"freq": "14-16kHz", "why": "Quitar ultrasonica innecesaria"},
        },
        "trap": {
            "high_pass": {"freq": "300Hz", "slope": "24dB/oct", "why": "Son PURO agudo"},
            "cut_1": {"freq": "2-4kHz", "gain": "-1 a -2dB", "why": "Si son chillones"},
            "boost_1": {"freq": "10-14kHz", "gain": "+2-3dB", "type": "shelf", "why": "Crispy"},
        },
    },
    "bass": {
        "boom_bap": {
            "high_pass": {"freq": "25-30Hz", "slope": "18dB/oct", "why": "Quitar sub-frecuencias inutiles"},
            "cut_1": {"freq": "300-500Hz", "gain": "-2dB", "why": "Quitar mud SI lo necesita"},
            "boost_1": {"freq": "60-80Hz", "gain": "+2-3dB", "why": "PESO del bajo"},
            "boost_2": {"freq": "700Hz-1kHz", "gain": "+1-2dB", "why": "Articulacion/dedo (bajo real)"},
            "low_pass": {"freq": "5-8kHz", "why": "Quitar ruido de high end innecesario"},
        },
    },
    "808": {
        "trap": {
            "pre_distortion": {
                "high_pass": {"freq": "28Hz", "slope": "24dB/oct", "why": "Limpiar sub-sub ANTES de distorsionar"},
            },
            "post_distortion": {
                "high_pass": {"freq": "30Hz", "why": "Limpiar artefactos de distorsion"},
                "boost_1": {"freq": "55-70Hz", "gain": "+2-3dB", "why": "Peso que sientes en el pecho"},
                "boost_2": {"freq": "150-250Hz", "gain": "+2-3dB", "why": "Cuerpo del rugido"},
                "cut_1": {"freq": "400-600Hz", "gain": "-2dB", "why": "Zona carton"},
                "boost_3": {"freq": "1-3kHz", "gain": "+1-2dB", "why": "Presencia del crack"},
                "low_pass": {"freq": "8-10kHz", "why": "Quitar ruido de distorsion"},
            },
        },
    },
    "sample": {
        "boom_bap": {
            "high_pass": {"freq": "40-60Hz", "slope": "18dB/oct", "why": "Quitar rumble del vinilo"},
            "cut_1": {"freq": "200-400Hz", "gain": "-2 a -3dB", "why": "Quitar mud del sample viejo"},
            "boost_1": {"freq": "1-3kHz", "gain": "+2dB", "why": "Sacar los detalles del sample"},
            "high_shelf": {"freq": "8-12kHz", "gain": "+2-3dB", "why": "Abrir el sample, que respire"},
            "note": "Si el sample ya es brillante, NO anadir mas brillo",
        },
    },
    "melody": {
        "trap": {
            "high_pass": {"freq": "80-120Hz", "slope": "24dB/oct", "why": "Dejar espacio al 808"},
            "cut_1": {"freq": "200-400Hz", "gain": "-2dB", "why": "Quitar mud"},
            "boost_1": {"freq": "2-5kHz", "gain": "+2dB", "why": "Presencia"},
            "high_shelf": {"freq": "10kHz", "gain": "+2-3dB", "why": "Brillo/aire"},
        },
    },
    "pads": {
        "both": {
            "high_pass": {"freq": "100-200Hz", "why": "Dejar espacio a kick/bajo"},
            "low_pass": {"freq": "8-12kHz", "why": "No competir con voz/hats"},
            "cut_mid": {"freq": "1-3kHz", "gain": "-2dB", "why": "Dejar espacio a la voz"},
        },
    },
    "vocal_main": {
        "boom_bap": {
            "subtractive": {
                "high_pass": {"freq": "80-100Hz", "slope": "24dB/oct", "why": "Obligatorio"},
                "sweep_1": {"freq": "200-400Hz", "gain": "-2 a -3dB", "why": "Mud"},
                "sweep_2": {"freq": "400-800Hz", "gain": "-1 a -2dB", "why": "Boxiness"},
                "sweep_3": {"freq": "2-4kHz", "gain": "-1 a -2dB", "why": "Harshness"},
            },
            "additive": {
                "boost_1": {"freq": "2.5-4kHz", "gain": "+2-3dB", "Q": 1, "why": "PRESENCIA"},
                "boost_2": {"freq": "8-12kHz", "gain": "+2-3dB", "type": "high shelf", "why": "AIRE"},
                "boost_3": {"freq": "200-300Hz", "gain": "+1dB", "why": "Calidez (solo si suena fina)"},
            },
            "de_esser": {
                "band": "5-8kHz", "mode": "dinamico",
                "reduction": "-3 a -6dB",
                "note": "Solo actua en las S",
            },
        },
        "trap": {
            "subtractive": {
                "high_pass": {"freq": "90-110Hz", "slope": "24dB/oct", "why": "Limpieza"},
                "cut_1": {"freq": "250Hz", "gain": "-2dB", "why": "Mud"},
                "cut_2": {"freq": "500Hz", "gain": "-1.5dB", "why": "Boxiness"},
                "sweep_destroy": "Buscar y cortar resonancias",
            },
            "additive": {
                "boost_1": {"freq": "3-5kHz", "gain": "+3dB", "why": "Presencia agresiva"},
                "high_shelf": {"freq": "10-14kHz", "gain": "+3-4dB", "why": "AIRE, el brillo del trap"},
            },
            "de_esser": {
                "band": "5-9kHz", "mode": "Dynamic EQ del Pro-Q 3",
                "note": "Especialmente necesario despues de tanto boost en agudos",
            },
        },
    },
    "master": {
        "boom_bap": {
            "high_pass": {"freq": "25Hz", "slope": "18dB/oct", "why": "Limpiar sub-sub"},
            "cut_1": {"freq": "300Hz", "gain": "-1dB", "why": "Si hay acumulacion de mud"},
            "boost_1": {"freq": "100Hz", "gain": "+1dB", "why": "Si falta peso"},
            "boost_2": {"freq": "12kHz", "gain": "+1dB", "type": "high shelf", "why": "Si falta aire"},
            "max_adjustment": "+/- 1.5dB",
        },
        "trap": {
            "high_pass": {"freq": "25Hz", "slope": "24dB/oct", "why": "Limpieza de sub-sub"},
            "cut_1": {"freq": "200-350Hz", "gain": "-1dB", "why": "Si hay mud"},
            "boost_1": {"freq": "50-70Hz", "gain": "+1dB", "why": "Si falta peso del 808"},
            "boost_2": {"freq": "12-14kHz", "gain": "+1-2dB", "type": "high shelf", "why": "Brillo/aire moderno"},
            "max_adjustment": "+/-2dB",
        },
    },
}


# ---------------------------------------------------------------------------
# 9. SOUNDTOYS_GUIDE -- which plugin for which purpose
# ---------------------------------------------------------------------------

SOUNDTOYS_GUIDE = {
    "Decapitator": {
        "use_on": "EVERYWHERE - kick, snare, bajo, voz, samples, buses, master",
        "purpose": "Saturacion/distorsion con caracter analogico",
        "styles": {
            "T": "Tape - boom bap, cinta, calor",
            "A": "American - agresivo, 808, voces",
            "N": "Neve - calido, musical",
            "E": "Ampex - trap agresivo, voces trap",
        },
    },
    "EchoBoy": {
        "use_on": "Voz, melodias, sends de delay",
        "purpose": "Delay con saturacion y caracter",
    },
    "MicroShift": {
        "use_on": "Dobles, coros, hats, melodias",
        "purpose": "Abrir estereo sutil",
    },
    "Devil-Loc Deluxe": {
        "use_on": "Bus drums (paralelo), 808 trap",
        "purpose": "Compresion destructiva",
    },
    "Radiator": {
        "use_on": "Samples boom bap, bus melodias",
        "purpose": "Calor de consola Altec",
    },
    "Little AlterBoy": {
        "use_on": "Voz (efecto), ad-libs",
        "purpose": "Pitch/formant shift",
    },
    "FilterFreak": {
        "use_on": "Samples, melodias, transiciones",
        "purpose": "Filtro con caracter",
    },
    "Crystallizer": {
        "use_on": "Pads, ad-libs, texturas",
        "purpose": "Delay granular/pitch",
    },
    "Tremolator": {
        "use_on": "Pads, melodias trap",
        "purpose": "Tremolo sincronizado",
    },
    "PrimalTap": {
        "use_on": "Percs boom bap, efectos",
        "purpose": "Delay lo-fi vintage",
    },
    "PanMan": {
        "use_on": "Hi-hats, percs, ad-libs",
        "purpose": "Auto-pan creativo",
    },
    "Little Radiator": {
        "use_on": "Donde Radiator es demasiado",
        "purpose": "Calor sutil rapido",
    },
    "Sie-Q": {
        "use_on": "Voces, buses",
        "purpose": "EQ pasivo con color",
    },
    "Little Plate": {
        "use_on": "Send de reverb voces/snare",
        "purpose": "Plate reverb con calor",
    },
}


# ---------------------------------------------------------------------------
# WORKFLOW -- complete step-by-step order of work
# ---------------------------------------------------------------------------

WORKFLOW = {
    "fase_1_preparacion": [
        "Organizar canales en el mixer (routing, nombres, colores)",
        "Gain staging de TODOS los canales (-18 a -12dBFS)",
        "Limpieza con iZotope RX (voces, samples si lo necesitan)",
        "Configurar buses (drums, melodias, voces)",
        "Configurar sends (reverb, delay)",
        "Importar track de referencia (silenciado, solo para A/B)",
    ],
    "fase_2_mezcla_individual": [
        "Kick - EQ + comp + saturacion",
        "Snare - EQ + comp + saturacion",
        "Hi-hats - EQ + procesamiento",
        "Percs - EQ + delay",
        "Bajo/808 - EQ + distorsion + comp + sidechain",
        "Samples/melodias - limpieza + EQ + saturacion + comp",
        "Pads/texturas - EQ + efectos",
        "Voz principal - cadena completa",
        "Dobles - EQ + comp + estereo",
        "Ad-libs - EQ + comp + efectos",
        "Sends de reverb y delay - ajustar niveles",
    ],
    "fase_3_buses": [
        "Bus drums - glue comp + saturacion",
        "Bus melodias - EQ(espacio voz) + glue comp",
        "Bus voces - glue comp + saturacion cohesion",
    ],
    "fase_4_balances": [
        "Volumen relativo de cada grupo",
        "Voz 2-4dB por encima de la instrumental",
        "Escuchar a volumen bajo - se entiende la voz?",
        "Escuchar en mono - algo desaparece?",
        "A/B con referencia profesional",
    ],
    "fase_5_master": [
        "EQ correctivo sutil (Pro-Q 3)",
        "Saturacion de master (Decapitator, solo si aplica)",
        "Ozone 12 - Dynamic EQ",
        "Ozone 12 - Compresion/Dynamics",
        "Ozone 12 - Tape (boom bap) / Exciter (trap)",
        "Ozone 12 - Imager (bajo a MONO)",
        "Ozone 12 - Maximizer (limiter final)",
        "Verificar LUFS (-10 a -12 para streaming)",
        "Verificar que no clipea",
        "Escuchar en multiples sistemas (auriculares, telefono, altavoz)",
        "Exportar: WAV 44.1kHz/24bit (para distribucion)",
        "Exportar: WAV 48kHz/24bit (para video/YouTube)",
    ],
    "fase_6_exportacion": [
        "File > Export > WAV",
        "Bit depth: 24-bit",
        "Sample rate: 44100 Hz (musica) o 48000 Hz (video)",
        "Dithering: activar en Ozone Maximizer si bajas a 16-bit",
        "Escuchar el archivo exportado de principio a fin",
        "Escuchar en el telefono, en el coche, con auriculares baratos",
    ],
}


# ---------------------------------------------------------------------------
# COMMON_MISTAKES -- things to avoid
# ---------------------------------------------------------------------------

COMMON_MISTAKES = [
    {
        "mistake": "Demasiados plugins",
        "fix": "Si no mejora el sonido, QUITALO. A/B constantemente. "
               "5 plugins bien puestos > 15 al azar.",
    },
    {
        "mistake": "No hacer gain staging",
        "fix": "Si la senal entra al plugin a +6dB, va a distorsionar. "
               "Si entra a -30dB, va a sonar con ruido. "
               "SIEMPRE calibrar niveles ANTES de meter plugins.",
    },
    {
        "mistake": "Mezclar a volumen alto",
        "fix": "Mezcla a volumen BAJO-MEDIO. Si suena bien bajito, suena increible alto. "
               "Protege tus oidos.",
    },
    {
        "mistake": "No usar referencias",
        "fix": "Pon una cancion PRO del genero en un canal del mixer. Compara constantemente.",
    },
    {
        "mistake": "Arreglar en el master lo que se arregla en la mezcla",
        "fix": "Si el 808 tiene mud, arreglalo en el canal del 808. "
               "El master solo REALZA, no arregla.",
    },
    {
        "mistake": "Ignorar la mono-compatibilidad",
        "fix": "Baja a mono periodicamente. Si algo desaparece, hay problemas de fase. "
               "Clubs, telefonos y muchos altavoces son mono o casi mono.",
    },
    {
        "mistake": "Over-compresion en el master",
        "fix": "Si el Ozone Maximizer esta reduciendo mas de -6dB, es demasiado. "
               "Baja los niveles en la mezcla.",
    },
    {
        "mistake": "No descansar los oidos",
        "fix": "Cada 30-45 minutos, descansa 5-10 minutos. "
               "Fatiga auditiva = malas decisiones.",
    },
]


# ---------------------------------------------------------------------------
# GENRE_DIFFERENCES -- key contrasts between boom bap and trap
# ---------------------------------------------------------------------------

GENRE_DIFFERENCES = {
    "boom_bap": {
        "drums": "Samples de vinilo, sucios, con caracter",
        "bass": "Sub limpio o bajo de sample (contrabajo, Rhodes bass)",
        "texture": "Lo-fi, cinta, polvo, calor analogico",
        "dynamics": "MAS dinamica, menos compresion, respira",
        "references": ["DJ Premier", "Pete Rock", "J Dilla", "9th Wonder", "Havoc"],
    },
    "trap": {
        "drums": "808 sintetico, hi-hats rapidos, snares electronicas",
        "bass": "808 largo con distorsion y slide",
        "texture": "Limpia y moderna, pero con peso",
        "dynamics": "Mas comprimida, mas fuerte, mas 'in your face'",
        "references": ["Metro Boomin", "Southside", "Zaytoven", "Lex Luger"],
    },
}


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def get_chain(element: str, genre: str) -> str:
    """Return a formatted string describing the plugin chain for an element/genre.

    Args:
        element: One of kick, snare, hihats, percs, bass, 808, sample, melody,
                 pads, vocal_main, doubles, adlibs, bus_drums, bus_melody,
                 bus_vocals, master.
        genre: 'boom_bap' or 'trap'.

    Returns:
        A human-readable multiline string with the full chain details.
    """
    key = (element, genre)
    chain = PLUGIN_CHAINS.get(key)
    if chain is None:
        return f"No chain found for element='{element}', genre='{genre}'."

    lines = [f"=== Plugin Chain: {element.upper()} ({genre.upper()}) ===", ""]
    for slot_info in chain:
        slot_num = slot_info.get("slot", "?")
        plugin = slot_info.get("plugin_name", "Unknown")
        purpose = slot_info.get("purpose", "")
        settings = slot_info.get("settings", {})

        lines.append(f"SLOT {slot_num} -> {plugin}")
        lines.append(f"  Purpose: {purpose}")
        if settings:
            for k, v in settings.items():
                lines.append(f"  {k}: {v}")

        # Check for Ozone modules (master chain)
        modules = slot_info.get("modules")
        if modules:
            for mod in modules:
                lines.append(f"  --- {mod['name']} ---")
                for k, v in mod.get("settings", {}).items():
                    lines.append(f"    {k}: {v}")

        # Check for alternative
        alt = slot_info.get("alternative")
        if alt:
            lines.append(f"  ALTERNATIVA: {alt.get('plugin_name', '')}")
            lines.append(f"    Purpose: {alt.get('purpose', '')}")
            for k, v in alt.get("settings", {}).items():
                lines.append(f"    {k}: {v}")

        lines.append("")

    return "\n".join(lines)


def get_mix_levels(genre: str) -> str:
    """Return a formatted string with relative mix levels for the given genre.

    Args:
        genre: 'boom_bap' or 'trap'.

    Returns:
        Formatted multiline string with level and panning per element.
    """
    levels = MIX_LEVELS.get(genre)
    if levels is None:
        return f"No mix levels found for genre='{genre}'."

    lines = [f"=== Mix Levels: {genre.upper()} ===", ""]
    for element, info in levels.items():
        level = info.get("level", "")
        pan = info.get("pan", "")
        notes = info.get("notes", "")
        lines.append(f"{element.upper():20s}  Level: {level}")
        lines.append(f"{'':20s}  Pan: {pan}")
        if notes:
            lines.append(f"{'':20s}  Notes: {notes}")
        lines.append("")

    return "\n".join(lines)


def get_mastering_chain(genre: str) -> str:
    """Return a formatted string with the complete mastering chain for the genre.

    Args:
        genre: 'boom_bap' or 'trap'.

    Returns:
        Formatted multiline string with every mastering slot and settings.
    """
    master = MASTERING_CHAINS.get(genre)
    if master is None:
        return f"No mastering chain found for genre='{genre}'."

    lines = [
        f"=== Mastering Chain: {genre.upper()} ===",
        "",
        f"Philosophy: {master['philosophy']}",
        f"Prerequisite: {master['prerequisite']}",
        "",
    ]

    for step in master["chain"]:
        slot = step.get("slot", "?")
        plugin = step.get("plugin", "Unknown")
        purpose = step.get("purpose", "")
        settings = step.get("settings", {})

        lines.append(f"SLOT {slot} -> {plugin}")
        lines.append(f"  Purpose: {purpose}")
        for k, v in settings.items():
            lines.append(f"  {k}: {v}")
        lines.append("")

    export = master.get("export", {})
    if export:
        lines.append("--- Export Settings ---")
        for k, v in export.items():
            lines.append(f"  {k}: {v}")
        lines.append("")

    return "\n".join(lines)


def get_eq_guide(element: str) -> str:
    """Return a formatted EQ frequency guide for the given element.

    Args:
        element: e.g. 'kick', 'snare', 'hihats', 'bass', '808', 'sample',
                 'melody', 'pads', 'vocal_main', 'master'.

    Returns:
        Formatted multiline string with frequencies, gains, and reasons.
    """
    guide = EQ_FREQUENCY_GUIDE.get(element)
    if guide is None:
        return f"No EQ guide found for element='{element}'."

    lines = [f"=== EQ Frequency Guide: {element.upper()} ===", ""]

    def _format_band(name, info):
        if isinstance(info, dict):
            parts = [f"  {name}:"]
            for k, v in info.items():
                parts.append(f"    {k}: {v}")
            return "\n".join(parts)
        return f"  {name}: {info}"

    for genre_or_section, data in guide.items():
        lines.append(f"--- {genre_or_section} ---")
        if isinstance(data, dict):
            for band_name, band_info in data.items():
                if isinstance(band_info, dict):
                    # Could be nested (e.g., 808 pre/post or vocal subtractive/additive)
                    first_val = next(iter(band_info.values()), None)
                    if isinstance(first_val, dict):
                        lines.append(f"  [{band_name}]")
                        for sub_name, sub_info in band_info.items():
                            lines.append(_format_band(sub_name, sub_info))
                    else:
                        lines.append(_format_band(band_name, band_info))
                else:
                    lines.append(f"  {band_name}: {band_info}")
        else:
            lines.append(f"  {data}")
        lines.append("")

    return "\n".join(lines)


def get_send_config(genre: str) -> str:
    """Return a formatted string with the send effect configuration for the genre.

    Args:
        genre: 'boom_bap' or 'trap'.

    Returns:
        Formatted multiline string with reverb, delay, and parallel compression sends.
    """
    config = SEND_CONFIGS.get(genre)
    if config is None:
        return f"No send config found for genre='{genre}'."

    lines = [f"=== Send Configuration: {genre.upper()} ===", ""]

    for send_name, send_info in config.items():
        insert = send_info.get("insert", "")
        plugin = send_info.get("plugin_name", send_info.get("note", ""))
        wet = send_info.get("wet", "")
        settings = send_info.get("settings", {})

        header = f"{send_name.upper()}"
        if insert:
            header += f" (Insert {insert})"
        lines.append(header)
        if plugin:
            lines.append(f"  Plugin: {plugin}")
        if wet:
            lines.append(f"  Wet: {wet}")
        for k, v in settings.items():
            lines.append(f"  {k}: {v}")
        lines.append("")

    return "\n".join(lines)


def get_gain_staging_guide() -> str:
    """Return the complete gain staging guide as a formatted string."""
    g = GAIN_STAGING_GUIDE
    lines = [
        f"=== {g['title']} ===",
        "",
        f"Rule: {g['rule']}",
        f"Reason: {g['reason']}",
        "",
        "Steps:",
    ]
    for step in g["steps"]:
        lines.append(f"  {step}")

    lines.append("")
    lines.append(f"Channel target: {g['channel_target']}")
    lines.append(f"Master target (pre-mastering): {g['master_target_pre_mastering']}")
    lines.append("")
    lines.append("Common mistakes:")
    for m in g["common_mistakes"]:
        lines.append(f"  - {m}")

    return "\n".join(lines)


def get_mixer_template() -> str:
    """Return the recommended FL Studio mixer layout as a formatted string."""
    t = MIXER_TEMPLATE
    lines = ["=== Recommended FL Studio Mixer Template ===", ""]

    lines.append("--- Inserts ---")
    for insert_num, info in sorted(t["inserts"].items()):
        lines.append(f"  Insert {insert_num:3d}: {info['name']}  ({info['group']})")
    lines.append("")

    lines.append("--- Buses ---")
    for insert_num, info in sorted(t["buses"].items()):
        receives = ", ".join(str(r) for r in info["receives_from"])
        lines.append(f"  Insert {insert_num}: {info['name']}  (receives from: {receives})")
    lines.append("")

    lines.append("--- Sends ---")
    for insert_num, info in sorted(t["sends"].items()):
        lines.append(f"  Insert {insert_num}: {info['name']}  (wet: {info['wet']})")
    lines.append("")

    lines.append("--- Master ---")
    lines.append(f"  {t['master']['name']}: {t['master']['note']}")

    return "\n".join(lines)


def get_lufs_targets() -> str:
    """Return LUFS targets per platform as a formatted string."""
    lines = ["=== LUFS Targets per Platform ===", ""]
    for platform, info in LUFS_TARGETS.items():
        if platform == "recommendation":
            lines.append("--- Recommendations ---")
            for k, v in info.items():
                lines.append(f"  {k}: {v}")
        else:
            lufs = info.get("lufs", "N/A")
            note = info.get("note", "")
            lines.append(f"  {platform.upper():15s}  LUFS: {lufs}  ({note})")
    lines.append("")
    return "\n".join(lines)


def get_workflow() -> str:
    """Return the complete mixing/mastering workflow as a formatted string."""
    lines = ["=== Complete Mixing & Mastering Workflow ===", ""]
    for fase, steps in WORKFLOW.items():
        lines.append(f"--- {fase.replace('_', ' ').upper()} ---")
        for step in steps:
            lines.append(f"  [ ] {step}")
        lines.append("")
    return "\n".join(lines)


def get_soundtoys_guide() -> str:
    """Return a formatted guide of which Soundtoys plugin to use where."""
    lines = ["=== Soundtoys Plugin Guide ===", ""]
    for plugin, info in SOUNDTOYS_GUIDE.items():
        lines.append(f"{plugin}")
        lines.append(f"  Use on: {info['use_on']}")
        lines.append(f"  Purpose: {info['purpose']}")
        styles = info.get("styles")
        if styles:
            for style_key, style_desc in styles.items():
                lines.append(f"    Style {style_key}: {style_desc}")
        lines.append("")
    return "\n".join(lines)
