"""Conocimiento de iZotope Ozone 12 para mastering en FL Studio MCP.

Cadenas de mastering por género, módulos con parámetros detallados,
LUFS targets por plataforma y quick chains simplificadas.
"""

from typing import Dict, List, Optional


# ============================================================================
# 1. MÓDULOS OZONE 12
# ============================================================================

OZONE_MODULES: Dict[str, Dict] = {
    "equalizer": {
        "name": "Ozone 12 Equalizer",
        "vst3": "Ozone 12 Equalizer.vst3",
        "description": "EQ paramétrico de alta calidad con modo analógico y digital. 8 bandas.",
        "parameters": {
            "bands": {"range": "1-8", "desc": "Número de bandas"},
            "frequency": {"range": "20-20000 Hz", "desc": "Frecuencia central por banda"},
            "gain": {"range": "-15 a +15 dB", "desc": "Ganancia por banda"},
            "q": {"range": "0.1-10.0", "desc": "Ancho de banda"},
            "shape": {"options": ["Bell", "Low Shelf", "High Shelf", "Low Cut", "High Cut", "Band Pass"], "desc": "Tipo de filtro"},
            "mode": {"options": ["Digital", "Analog", "Vintage"], "desc": "Carácter del EQ"},
        },
    },
    "dynamic_eq": {
        "name": "Ozone 12 Dynamic EQ",
        "vst3": "Ozone 12 Dynamic EQ.vst3",
        "description": "EQ que actúa solo cuando la señal cruza un umbral. Ideal para problemas intermitentes.",
        "parameters": {
            "frequency": {"range": "20-20000 Hz"},
            "gain": {"range": "-15 a +15 dB"},
            "threshold": {"range": "-60 a 0 dB", "desc": "Umbral de activación"},
            "attack": {"range": "0.1-100 ms"},
            "release": {"range": "10-1000 ms"},
            "ratio": {"range": "1:1 a inf:1"},
        },
    },
    "dynamics": {
        "name": "Ozone 12 Dynamics",
        "vst3": "Ozone 12 Dynamics.vst3",
        "description": "Compresor/limiter multibanda. Hasta 4 bandas con crossovers ajustables.",
        "parameters": {
            "bands": {"range": "1-4", "desc": "Número de bandas"},
            "threshold": {"range": "-60 a 0 dB"},
            "ratio": {"range": "1:1 a 20:1"},
            "attack": {"range": "0.1-100 ms"},
            "release": {"range": "10-1000 ms"},
            "knee": {"range": "0-10 dB"},
            "makeup_gain": {"range": "0-20 dB"},
        },
    },
    "maximizer": {
        "name": "Ozone 12 Maximizer",
        "vst3": "Ozone 12 Maximizer.vst3",
        "description": "Limiter final para loudness. El módulo más importante del mastering.",
        "parameters": {
            "threshold": {"range": "-20 a 0 dB", "desc": "Umbral del limiter. Más bajo = más loud."},
            "ceiling": {"range": "-3 a 0 dB", "desc": "Techo de salida. -1dB para streaming."},
            "character": {"options": ["IRC I", "IRC II", "IRC III", "IRC IV"], "desc": "Algoritmo. IRC IV = más transparente."},
            "transient_emphasis": {"range": "0-100%", "desc": "Preservar transientes del limiter."},
            "stereo_independence": {"range": "0-100%", "desc": "Procesamiento estéreo independiente."},
        },
    },
    "exciter": {
        "name": "Ozone 12 Exciter",
        "vst3": "Ozone 12 Exciter.vst3",
        "description": "Generador de armónicos multibanda. Añade brillo, calidez o agresión.",
        "parameters": {
            "amount": {"range": "0-100%", "desc": "Cantidad de excitación por banda"},
            "mode": {"options": ["Warm", "Retro", "Tape", "Tube", "Triode", "Dual Triode"], "desc": "Tipo de saturación"},
            "mix": {"range": "0-100%"},
            "bands": {"range": "1-4"},
        },
    },
    "imager": {
        "name": "Ozone 12 Imager",
        "vst3": "Ozone 12 Imager.vst3",
        "description": "Control de ancho estéreo multibanda. Estrechar bajos, ensanchar agudos.",
        "parameters": {
            "width": {"range": "-100 a +300%", "desc": "Ancho estéreo por banda. 0=mono, 100=original, >100=ensanchado"},
            "bands": {"range": "1-4"},
            "crossover": {"desc": "Frecuencias de cruce entre bandas"},
        },
    },
    "vintage_tape": {
        "name": "Ozone 12 Vintage Tape",
        "vst3": "Ozone 12 Vintage Tape.vst3",
        "description": "Emulación de cinta magnética. Saturación, compresión y color analógico.",
        "parameters": {
            "drive": {"range": "0-10 dB", "desc": "Saturación de cinta"},
            "tape_speed": {"options": ["15 ips", "30 ips"], "desc": "Velocidad. 15=más color, 30=más limpio"},
            "low_emphasis": {"range": "-5 a +5 dB", "desc": "Realce de graves de la cinta"},
            "high_emphasis": {"range": "-5 a +5 dB", "desc": "Realce de agudos de la cinta"},
            "bias": {"range": "0-100%", "desc": "Bias de cinta. Más alto=menos distorsión"},
        },
    },
    "vintage_eq": {
        "name": "Ozone 12 Vintage EQ",
        "vst3": "Ozone 12 Vintage EQ.vst3",
        "description": "EQ con carácter vintage. Modelado de hardware clásico (Pultec, Neve).",
        "parameters": {
            "low_gain": {"range": "-10 a +10 dB"},
            "low_freq": {"options": ["20", "30", "60", "100 Hz"]},
            "mid_gain": {"range": "-10 a +10 dB"},
            "mid_freq": {"range": "200-8000 Hz"},
            "high_gain": {"range": "-10 a +10 dB"},
            "high_freq": {"options": ["4k", "8k", "12k", "16k Hz"]},
        },
    },
    "vintage_compressor": {
        "name": "Ozone 12 Vintage Compressor",
        "vst3": "Ozone 12 Vintage Compressor.vst3",
        "description": "Compresor con carácter vintage. Tres modos: Sharp, Balanced, Smooth.",
        "parameters": {
            "threshold": {"range": "-40 a 0 dB"},
            "ratio": {"range": "1:1 a 20:1"},
            "attack": {"range": "0.1-100 ms"},
            "release": {"range": "10-1000 ms"},
            "mode": {"options": ["Sharp", "Balanced", "Smooth"], "desc": "Sharp=rápido/agresivo, Smooth=lento/musical"},
            "makeup_gain": {"range": "0-20 dB"},
        },
    },
    "vintage_limiter": {
        "name": "Ozone 12 Vintage Limiter",
        "vst3": "Ozone 12 Vintage Limiter.vst3",
        "description": "Limiter con carácter vintage. Más colorido que el Maximizer.",
        "parameters": {
            "threshold": {"range": "-20 a 0 dB"},
            "mode": {"options": ["Analog", "Tube"], "desc": "Analog=limpio, Tube=saturado"},
            "character": {"range": "0-10", "desc": "Más carácter vintage"},
        },
    },
    "spectral_shaper": {
        "name": "Ozone 12 Spectral Shaper",
        "vst3": "Ozone 12 Spectral Shaper.vst3",
        "description": "Control de harshness espectral. Doma picos de frecuencia sin EQ estático.",
        "parameters": {
            "threshold": {"range": "-30 a 0 dB"},
            "tone": {"range": "-100 a +100", "desc": "Negativo=más oscuro, positivo=más brillante"},
            "speed": {"options": ["Slow", "Medium", "Fast"], "desc": "Velocidad de reacción"},
        },
    },
    "stabilizer": {
        "name": "Ozone 12 Stabilizer",
        "vst3": "Ozone 12 Stabilizer.vst3",
        "description": "Corrección de balance tonal automática basada en AI.",
        "parameters": {
            "amount": {"range": "0-100%", "desc": "Cantidad de corrección"},
            "style": {"options": ["Smooth", "Tight"], "desc": "Estilo de corrección"},
        },
    },
    "bass_control": {
        "name": "Ozone 12 Bass Control",
        "vst3": "Ozone 12 Bass Control.vst3",
        "description": "Manejo inteligente de sub/low-end. Mono-ifica graves y limpia sub.",
        "parameters": {
            "frequency": {"range": "40-300 Hz", "desc": "Frecuencia de corte para mono"},
            "gain": {"range": "-10 a +10 dB", "desc": "Ganancia del sub"},
            "contour": {"range": "0-100%", "desc": "Shaping del low-end"},
        },
    },
    "clarity": {
        "name": "Ozone 12 Clarity",
        "vst3": "Ozone 12 Clarity.vst3",
        "description": "Mejora de claridad y definición en el rango medio-alto.",
        "parameters": {
            "amount": {"range": "0-100%"},
            "style": {"options": ["Natural", "Presence", "Detail"]},
        },
    },
    "impact": {
        "name": "Ozone 12 Impact",
        "vst3": "Ozone 12 Impact.vst3",
        "description": "Control de transientes y punch en el master.",
        "parameters": {
            "amount": {"range": "-100 a +100%", "desc": "Negativo=suaviza, positivo=más punch"},
            "frequency": {"range": "20-8000 Hz", "desc": "Rango de frecuencia afectado"},
        },
    },
    "low_end_focus": {
        "name": "Ozone 12 Low End Focus",
        "vst3": "Ozone 12 Low End Focus.vst3",
        "description": "Enfoque del low-end. Tightens o loosens los graves.",
        "parameters": {
            "amount": {"range": "-100 a +100%", "desc": "Negativo=tight, positivo=loose"},
            "frequency": {"range": "40-300 Hz"},
            "mode": {"options": ["Punchy", "Smooth"]},
        },
    },
    "match_eq": {
        "name": "Ozone 12 Match EQ",
        "vst3": "Ozone 12 Match EQ.vst3",
        "description": "Iguala el balance tonal de tu master a un track de referencia.",
        "parameters": {
            "amount": {"range": "0-100%", "desc": "Cantidad de matching"},
            "smoothing": {"range": "0-100%", "desc": "Suavizado de la curva"},
        },
    },
    "master_rebalance": {
        "name": "Ozone 12 Master Rebalance",
        "vst3": "Ozone 12 Master Rebalance.vst3",
        "description": "Ajuste de volumen de vocals/drums/bass en un master terminado (AI).",
        "parameters": {
            "vocals": {"range": "-12 a +12 dB"},
            "bass": {"range": "-12 a +12 dB"},
            "drums": {"range": "-12 a +12 dB"},
        },
    },
    "unlimiter": {
        "name": "Ozone 12 Unlimiter",
        "vst3": "Ozone 12 Unlimiter.vst3",
        "description": "Reversa de limiting. Restaura dinámica a masters muy comprimidos.",
        "parameters": {
            "amount": {"range": "0-100%", "desc": "Cantidad de restauración dinámica"},
        },
    },
    "stem_eq": {
        "name": "Ozone 12 Stem EQ",
        "vst3": "Ozone 12 Stem EQ.vst3",
        "description": "EQ por stems (vocals, drums, bass, other) dentro del master.",
        "parameters": {
            "stem": {"options": ["Vocals", "Drums", "Bass", "Other"]},
            "frequency": {"range": "20-20000 Hz"},
            "gain": {"range": "-15 a +15 dB"},
        },
    },
}


# ============================================================================
# 2. CADENAS DE MASTERING POR GÉNERO
# ============================================================================

MASTERING_CHAINS: Dict[str, Dict] = {
    "boom_bap": {
        "name": "Mastering Boom Bap",
        "description": "Cálido, dinámico, sensación de vinyl. No over-compress.",
        "target_lufs": -14,
        "chain": [
            {
                "module": "vintage_tape",
                "settings": {"drive": "2.5 dB", "tape_speed": "15 ips", "low_emphasis": "+1 dB", "high_emphasis": "-1 dB", "bias": "60%"},
                "nota": "Color de cinta sutil. 15 ips para más warmth.",
            },
            {
                "module": "equalizer",
                "settings": {"mode": "Analog", "band1": "Low Shelf +1.5dB @ 80Hz", "band2": "Bell -1dB @ 300Hz Q=1.5", "band3": "High Shelf -0.5dB @ 10kHz"},
                "nota": "Realzar cuerpo, limpiar mud, roll off agudos levemente.",
            },
            {
                "module": "vintage_compressor",
                "settings": {"threshold": "-18 dB", "ratio": "2:1", "attack": "30 ms", "release": "150 ms", "mode": "Smooth", "makeup_gain": "1.5 dB"},
                "nota": "Compresión suave para glue. 2-3dB de GR máximo.",
            },
            {
                "module": "imager",
                "settings": {"band1_width": "80% (bajo 200Hz)", "band2_width": "110% (200-2kHz)", "band3_width": "120% (arriba 2kHz)"},
                "nota": "Bajos casi mono, medios levemente anchos, agudos más anchos.",
            },
            {
                "module": "maximizer",
                "settings": {"threshold": "-6 dB", "ceiling": "-1 dB", "character": "IRC IV", "transient_emphasis": "40%"},
                "nota": "Limiting suave. -14 LUFS target. IRC IV más transparente.",
            },
        ],
    },
    "trap": {
        "name": "Mastering Trap",
        "description": "Loud, agresivo, 808 potente, hi-hats definidos.",
        "target_lufs": -8,
        "chain": [
            {
                "module": "bass_control",
                "settings": {"frequency": "80 Hz", "gain": "+2 dB", "contour": "60%"},
                "nota": "Mono-ificar y realzar sub para que el 808 pegue parejo.",
            },
            {
                "module": "dynamic_eq",
                "settings": {"band1": "Cut -3dB @ 250Hz cuando supera -15dB", "band2": "Cut -2dB @ 3.5kHz cuando supera -12dB"},
                "nota": "Control dinámico de mud y harshness. Solo actúa cuando hay exceso.",
            },
            {
                "module": "exciter",
                "settings": {"band1_mode": "Warm", "band1_amount": "10% (bajo 200Hz)", "band3_mode": "Retro", "band3_amount": "25% (arriba 5kHz)"},
                "nota": "Armónicos en sub para parlantes chicos. Brillo en hi-hats.",
            },
            {
                "module": "dynamics",
                "settings": {"bands": 3, "band1_threshold": "-12dB ratio 3:1", "band2_threshold": "-15dB ratio 2:1", "band3_threshold": "-18dB ratio 2:1"},
                "nota": "Compresión multibanda. Controlar sub independiente de mids y highs.",
            },
            {
                "module": "imager",
                "settings": {"band1_width": "50% (bajo 100Hz)", "band2_width": "100%", "band3_width": "140% (arriba 5kHz)"},
                "nota": "Sub MONO, hi-hats anchos. Contraste espacial.",
            },
            {
                "module": "maximizer",
                "settings": {"threshold": "-3 dB", "ceiling": "-0.5 dB", "character": "IRC III", "transient_emphasis": "60%"},
                "nota": "Limiting agresivo. -8 a -10 LUFS. Preservar transientes de hi-hat.",
            },
        ],
    },
    "phonk": {
        "name": "Mastering Phonk",
        "description": "Crushed, distorsionado, vintage y agresivo.",
        "target_lufs": -7,
        "chain": [
            {
                "module": "vintage_tape",
                "settings": {"drive": "5 dB", "tape_speed": "15 ips", "low_emphasis": "+2 dB", "high_emphasis": "-2 dB", "bias": "40%"},
                "nota": "Saturación de cinta FUERTE. Bias bajo = más distorsión.",
            },
            {
                "module": "exciter",
                "settings": {"band1_mode": "Tube", "band1_amount": "30%", "band2_mode": "Tape", "band2_amount": "20%", "band3_mode": "Retro", "band3_amount": "15%"},
                "nota": "Excitación agresiva en todas las bandas. Tube en graves para growl.",
            },
            {
                "module": "spectral_shaper",
                "settings": {"threshold": "-15 dB", "tone": "-20", "speed": "Medium"},
                "nota": "Domar harshness excesiva de la distorsión sin perder agresión.",
            },
            {
                "module": "dynamics",
                "settings": {"bands": 2, "band1_threshold": "-10dB ratio 4:1", "band2_threshold": "-12dB ratio 3:1"},
                "nota": "Compresión agresiva. Aplasta la dinámica intencionalmente.",
            },
            {
                "module": "maximizer",
                "settings": {"threshold": "-2 dB", "ceiling": "-0.3 dB", "character": "IRC II", "transient_emphasis": "30%"},
                "nota": "Limiting extremo. -6 a -8 LUFS. IRC II más agresivo.",
            },
        ],
    },
    "lofi": {
        "name": "Mastering Lo-Fi",
        "description": "Suave, cálido, rolled-off highs, sensación vintage.",
        "target_lufs": -14,
        "chain": [
            {
                "module": "vintage_tape",
                "settings": {"drive": "4 dB", "tape_speed": "15 ips", "low_emphasis": "+1.5 dB", "high_emphasis": "-3 dB", "bias": "50%"},
                "nota": "Cinta con roll-off de agudos natural. El módulo clave del lo-fi.",
            },
            {
                "module": "vintage_eq",
                "settings": {"low_gain": "+2 dB", "low_freq": "60 Hz", "mid_gain": "-1 dB", "mid_freq": "2000 Hz", "high_gain": "-2 dB", "high_freq": "8k Hz"},
                "nota": "EQ vintage para color. Calidez en graves, cortar agudos.",
            },
            {
                "module": "vintage_compressor",
                "settings": {"threshold": "-20 dB", "ratio": "2:1", "attack": "20 ms", "release": "100 ms", "mode": "Smooth"},
                "nota": "Compresión suave, musical. Glue vintage.",
            },
            {
                "module": "maximizer",
                "settings": {"threshold": "-8 dB", "ceiling": "-1 dB", "character": "IRC IV", "transient_emphasis": "20%"},
                "nota": "Limiting suave. No buscar loudness excesiva. -14 LUFS.",
            },
        ],
    },
    "jazz_hiphop": {
        "name": "Mastering Jazz Hip-Hop",
        "description": "Dinámico, limpio, respeta la instrumentación acústica.",
        "target_lufs": -14,
        "chain": [
            {
                "module": "match_eq",
                "settings": {"amount": "50%", "smoothing": "70%"},
                "nota": "Match con referencia (Robert Glasper, Nujabes). Sutil.",
            },
            {
                "module": "equalizer",
                "settings": {"mode": "Analog", "band1": "HPF @ 30Hz", "band2": "Bell +1dB @ 100Hz Q=1", "band3": "Bell +0.5dB @ 5kHz Q=1.5"},
                "nota": "Limpieza mínima. Respetar la mezcla.",
            },
            {
                "module": "vintage_compressor",
                "settings": {"threshold": "-15 dB", "ratio": "1.5:1", "attack": "40 ms", "release": "200 ms", "mode": "Balanced"},
                "nota": "Compresión muy suave. 1-2dB GR máximo. Preservar dinámica.",
            },
            {
                "module": "imager",
                "settings": {"band1_width": "85% (bajo 150Hz)", "band2_width": "105%", "band3_width": "115%"},
                "nota": "Imagen estéreo natural, no exagerada.",
            },
            {
                "module": "maximizer",
                "settings": {"threshold": "-7 dB", "ceiling": "-1 dB", "character": "IRC IV", "transient_emphasis": "50%"},
                "nota": "Limiting transparente. -14 LUFS. Dinámica es clave.",
            },
        ],
    },
}


# ============================================================================
# 3. TIPS POR MÓDULO
# ============================================================================

MODULE_TIPS: Dict[str, List[str]] = {
    "maximizer": [
        "IRC IV es el más transparente, usarlo por defecto",
        "IRC II es más agresivo, bueno para trap/phonk",
        "Ceiling -1dB para streaming, -0.3dB para máximo loudness",
        "Transient emphasis >50% preserva kick y snare del limiting",
        "Siempre el ÚLTIMO módulo de la cadena",
    ],
    "vintage_tape": [
        "15 ips = más color y saturación, ideal para boom bap y lo-fi",
        "30 ips = más limpio y definido, mejor para trap y EDM",
        "Bias bajo = más distorsión armónica",
        "El módulo más útil para dar 'analogness' al digital",
        "Usarlo PRIMERO en la cadena para que todo se sature parejo",
    ],
    "exciter": [
        "Warm y Tape son los más sutiles, buenos para mastering",
        "Tube y Triode son más agresivos, para phonk y trap",
        "Añadir excitación al sub (30-100Hz) hace que se escuche en parlantes chicos",
        "No exceder 20-30% por banda en mastering",
    ],
    "imager": [
        "SIEMPRE bajos mono o casi mono (debajo de 150Hz)",
        "Ensanchar agudos (>5kHz) da sensación de amplitud sin ensuciar",
        "No ensanchar medios (300-3kHz) excesivamente — ahí vive la vocal",
        "Width >200% puede causar problemas de fase en mono",
    ],
    "dynamic_eq": [
        "Mejor que EQ estático para problemas intermitentes",
        "Ideal para controlar resonancias del 808 sin afectar todo el tiempo",
        "Attack rápido para sibilancia, lento para resonancias tonales",
    ],
    "spectral_shaper": [
        "Mejor que de-esser para master, actúa en todo el espectro",
        "Tone negativo = más oscuro (ideal después de excitación agresiva)",
        "No reemplaza al EQ, complementa controlando picos dinámicos",
    ],
}


# ============================================================================
# 4. LUFS TARGETS POR PLATAFORMA Y GÉNERO
# ============================================================================

LUFS_TARGETS: Dict[str, Dict] = {
    "spotify": {
        "normalization": -14,
        "note": "Normaliza a -14 LUFS. Si está más loud, baja el volumen.",
        "by_genre": {
            "boom_bap": {"target": -14, "note": "Match con normalización. Dinámica completa."},
            "trap": {"target": -10, "note": "Spotify baja 4dB. El track suena competitivo."},
            "phonk": {"target": -8, "note": "Spotify baja 6dB. Aún suena agresivo."},
            "lofi": {"target": -14, "note": "Match perfecto. Lo-fi no necesita loudness."},
            "jazz_hiphop": {"target": -14, "note": "Dinámica respetada."},
        },
    },
    "youtube": {
        "normalization": -14,
        "note": "Normaliza a -14 LUFS (similar a Spotify).",
        "by_genre": {
            "boom_bap": -14, "trap": -10, "phonk": -8, "lofi": -14, "jazz_hiphop": -14,
        },
    },
    "apple_music": {
        "normalization": -16,
        "note": "Normaliza a -16 LUFS. Más conservador que Spotify.",
        "by_genre": {
            "boom_bap": -14, "trap": -10, "phonk": -8, "lofi": -14, "jazz_hiphop": -14,
        },
    },
    "soundcloud": {
        "normalization": "No normaliza",
        "note": "SoundCloud NO normaliza. El loudness queda como lo subís.",
        "by_genre": {
            "boom_bap": -14, "trap": -8, "phonk": -6, "lofi": -14, "jazz_hiphop": -14,
        },
    },
}


# ============================================================================
# 5. QUICK CHAINS (SIMPLIFICADAS)
# ============================================================================

QUICK_CHAINS: Dict[str, Dict] = {
    "boom_bap": {
        "name": "Quick Master Boom Bap",
        "modules": ["vintage_tape", "vintage_compressor", "maximizer"],
        "settings": {
            "vintage_tape": "Drive 2dB, 15ips, bias 60%",
            "vintage_compressor": "Threshold -18dB, ratio 2:1, Smooth",
            "maximizer": "Threshold -6dB, ceiling -1dB, IRC IV",
        },
    },
    "trap": {
        "name": "Quick Master Trap",
        "modules": ["bass_control", "exciter", "dynamics", "maximizer"],
        "settings": {
            "bass_control": "Freq 80Hz, gain +2dB",
            "exciter": "Sub 10% Warm, Highs 25% Retro",
            "dynamics": "3 bandas, ratios 2:1-3:1",
            "maximizer": "Threshold -3dB, ceiling -0.5dB, IRC III",
        },
    },
    "phonk": {
        "name": "Quick Master Phonk",
        "modules": ["vintage_tape", "exciter", "maximizer"],
        "settings": {
            "vintage_tape": "Drive 5dB, 15ips, bias 40%",
            "exciter": "Todo 20-30% Tube/Tape",
            "maximizer": "Threshold -2dB, ceiling -0.3dB, IRC II",
        },
    },
    "lofi": {
        "name": "Quick Master Lo-Fi",
        "modules": ["vintage_tape", "vintage_eq", "maximizer"],
        "settings": {
            "vintage_tape": "Drive 4dB, 15ips, high emphasis -3dB",
            "vintage_eq": "Low +2dB, High -2dB",
            "maximizer": "Threshold -8dB, ceiling -1dB, IRC IV",
        },
    },
    "jazz_hiphop": {
        "name": "Quick Master Jazz",
        "modules": ["equalizer", "vintage_compressor", "maximizer"],
        "settings": {
            "equalizer": "HPF 30Hz, gentle boost 100Hz y 5kHz",
            "vintage_compressor": "Threshold -15dB, ratio 1.5:1, Balanced",
            "maximizer": "Threshold -7dB, ceiling -1dB, IRC IV",
        },
    },
}


# ============================================================================
# 6. HELPER FUNCTIONS
# ============================================================================

def get_mastering_chain(genre: str) -> str:
    """Devuelve cadena de mastering completa para un género."""
    chain = MASTERING_CHAINS.get(genre)
    if not chain:
        available = ", ".join(MASTERING_CHAINS.keys())
        return f"Género no encontrado. Disponibles: {available}"

    lines = [
        f"## Ozone 12: {chain['name']}",
        f"{chain['description']}",
        f"Target: {chain['target_lufs']} LUFS\n",
    ]

    for i, step in enumerate(chain["chain"], 1):
        module = OZONE_MODULES.get(step["module"], {})
        lines.append(f"### Paso {i}: {module.get('name', step['module'])}")
        lines.append(f"  {step['nota']}")
        lines.append("  Settings:")
        for k, v in step["settings"].items():
            lines.append(f"    - {k}: {v}")
        lines.append("")

    return "\n".join(lines)


def get_module_guide(module_name: str) -> str:
    """Devuelve guía detallada de un módulo Ozone."""
    module = OZONE_MODULES.get(module_name)
    if not module:
        available = ", ".join(OZONE_MODULES.keys())
        return f"Módulo no encontrado. Disponibles: {available}"

    lines = [
        f"## {module['name']}",
        f"VST3: {module.get('vst3', 'N/A')}",
        f"{module['description']}\n",
        "### Parámetros:",
    ]

    for param, info in module["parameters"].items():
        if "range" in info:
            lines.append(f"  - **{param}**: {info.get('desc', '')} (rango: {info['range']})")
        elif "options" in info:
            lines.append(f"  - **{param}**: {info.get('desc', '')} ({', '.join(info['options'])})")

    tips = MODULE_TIPS.get(module_name, [])
    if tips:
        lines.append("\n### Tips:")
        for tip in tips:
            lines.append(f"  - {tip}")

    return "\n".join(lines)


def get_quick_master(genre: str) -> str:
    """Devuelve cadena simplificada de 3-4 módulos."""
    qc = QUICK_CHAINS.get(genre)
    if not qc:
        available = ", ".join(QUICK_CHAINS.keys())
        return f"Género no encontrado. Disponibles: {available}"

    lines = [
        f"## {qc['name']} (Quick)\n",
        f"Módulos: {' → '.join(qc['modules'])}\n",
    ]

    for mod in qc["modules"]:
        module = OZONE_MODULES.get(mod, {})
        name = module.get("name", mod)
        settings = qc["settings"].get(mod, "")
        lines.append(f"  **{name}**: {settings}")

    return "\n".join(lines)


def get_lufs_targets(genre: str = "", platform: str = "") -> str:
    """Devuelve targets de LUFS por plataforma y género."""
    lines = ["## LUFS Targets\n"]

    platforms = [platform] if platform else LUFS_TARGETS.keys()
    for plat in platforms:
        data = LUFS_TARGETS.get(plat)
        if not data:
            continue
        lines.append(f"### {plat.title()}")
        lines.append(f"  Normalización: {data['normalization']} LUFS")
        lines.append(f"  {data['note']}")

        by_genre = data.get("by_genre", {})
        if genre and genre in by_genre:
            val = by_genre[genre]
            if isinstance(val, dict):
                lines.append(f"  {genre}: {val['target']} LUFS — {val['note']}")
            else:
                lines.append(f"  {genre}: {val} LUFS")
        elif not genre:
            for g, val in by_genre.items():
                if isinstance(val, dict):
                    lines.append(f"  {g}: {val['target']} LUFS")
                else:
                    lines.append(f"  {g}: {val} LUFS")
        lines.append("")

    return "\n".join(lines)


def list_ozone_modules() -> str:
    """Lista todos los módulos Ozone 12."""
    lines = ["## Módulos iZotope Ozone 12\n"]
    for key, mod in OZONE_MODULES.items():
        lines.append(f"  - **{key}**: {mod['name']} — {mod['description'][:60]}...")
    return "\n".join(lines)
