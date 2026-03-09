"""Bass production knowledge, processing chains, and bassline generation for FL Studio MCP.

Encodes all bass production knowledge from plugins_bajos_fl_studio.txt including
bass types per genre, processing chains, growl techniques, distortion plugin
comparisons, multiband techniques, golden rules, and production tricks.
"""

from typing import List, Dict, Optional
import random

from .constants import note_to_midi, NOTE_NAMES, SEMITONE_TO_NAME


# ============================================================================
# 1. BASS TYPES PER GENRE
# ============================================================================

BASS_TYPES: Dict[str, Dict] = {
    "boom_bap": {
        "name": "Boom Bap Bass",
        "types": ["electric_sampled", "sub", "upright", "moog"],
        "description": "Sampled from vinyl, round and warm. Often from funk/soul records.",
        "key_characteristics": [
            "Sampled bass from vinyl records",
            "Round, warm tone",
            "Short to medium sustain",
            "Minimal processing, natural feel",
        ],
        "common_plugins": ["3x Osc (seno)", "Kontakt (bass libraries)", "DirectWave (samples)"],
        "eq_focus": "40-80Hz body, 800-1.5kHz string character",
        "distortion": "none_or_subtle",
        "sidechain": "subtle",
    },
    "trap": {
        "name": "Trap / Drill 808",
        "types": ["808_distorted", "808_slide"],
        "description": "808 largo con slide (glide/portamento). Distorsion media-alta.",
        "key_characteristics": [
            "808 largo con slide (glide/portamento)",
            "Distorsion media-alta (Camel Crusher o Saturn)",
            "Mucho sustain",
            "Sidechain sutil con el kick",
        ],
        "common_plugins": ["Serum", "Vital", "3x Osc", "808 samples"],
        "eq_focus": "boost 60Hz + 200Hz",
        "distortion": "medium_high",
        "sidechain": "subtle",
        "bpm_range": (130, 160),
    },
    "phonk": {
        "name": "Phonk Bass",
        "types": ["808_heavily_distorted"],
        "description": "808 MUY distorsionado. Suena 'roto' a proposito.",
        "key_characteristics": [
            "808 MUY distorsionado",
            "Camel Crusher al maximo o Decapitator",
            "Clip duro (Fruity Soft Clipper con drive)",
            "Suena 'roto' a proposito",
        ],
        "common_plugins": ["808 samples", "Camel Crusher", "Decapitator"],
        "eq_focus": "corte bajo agresivo en 40Hz, boost 100-200Hz",
        "distortion": "extreme",
        "sidechain": "none",
    },
    "reggaeton": {
        "name": "Reggaeton / Dembow Bass",
        "types": ["sub_clean"],
        "description": "Sub bass limpio (seno puro). Poca o nula distorsion.",
        "key_characteristics": [
            "Sub bass limpio (seno puro)",
            "Poca o nula distorsion",
            "Compresion fuerte para que sea consistente",
            "Sidechain MUY marcado con el kick (bombo y bajo 'bailan')",
        ],
        "common_plugins": ["3x Osc (seno puro)", "Vital", "Serum"],
        "eq_focus": "40-60Hz dominante",
        "distortion": "none",
        "sidechain": "heavy",
    },
    "dubstep": {
        "name": "Dubstep / Bass Music",
        "types": ["wavetable", "fm_synthesis", "resampled"],
        "description": "Serum o Vital con wavetables. FM synthesis + distorsion + filtros automatizados.",
        "key_characteristics": [
            "Serum o Vital con wavetables",
            "FM synthesis + distorsion + filtros automatizados",
            "Multiband distorsion OBLIGATORIA",
            "LFOs en el cutoff del filtro = el 'wub wub'",
            "Sound design puro, no solo plugins de efecto",
        ],
        "common_plugins": ["Serum", "Vital", "Sytrus (FM)"],
        "eq_focus": "full spectrum, multiband processing",
        "distortion": "multiband_heavy",
        "sidechain": "moderate",
    },
    "uk_drill": {
        "name": "UK Drill / Dark Trap Bass",
        "types": ["808_slide", "808_subtle_distortion"],
        "description": "808 con slide largo. Distorsion sutil pero presente. Sensacion oscura y profunda.",
        "key_characteristics": [
            "808 con slide largo",
            "Distorsion sutil pero presente",
            "Reverb MUY corto en el bajo (room tiny)",
            "Sensacion oscura y profunda",
        ],
        "common_plugins": ["808 samples", "Serum", "Vital"],
        "eq_focus": "boost 80Hz, corte todo arriba de 3kHz",
        "distortion": "subtle",
        "sidechain": "subtle",
    },
}


# ============================================================================
# 2. BASS PROCESSING CHAIN (recommended order)
# ============================================================================

BASS_PROCESSING_CHAIN: List[Dict[str, str]] = [
    {
        "step": 1,
        "name": "Generator",
        "description": "Generador del sonido base del bajo",
        "plugins": "Sytrus, 3x Osc, Serum, Vital, o sample 808",
        "purpose": "Crear la onda base (seno para sub, saw/square para mid bass)",
    },
    {
        "step": 2,
        "name": "Pitch / Glide",
        "description": "Portamento y afinacion",
        "plugins": "Portamento en el plugin o Piano Roll slide notes",
        "purpose": "808 slides, glide entre notas (100-300ms portamento para trap clasico)",
    },
    {
        "step": 3,
        "name": "Saturation / Distortion",
        "description": "Saturacion y distorsion para caracter y armonicos",
        "plugins": "Camel Crusher, FabFilter Saturn 2, Blood Overdrive, Soundtoys Decapitator",
        "purpose": "Agregar armonicos, 'rugido', caracter. AQUI esta la magia del bajo.",
    },
    {
        "step": 4,
        "name": "EQ",
        "description": "Ecualizacion post-distorsion",
        "plugins": "Parametric EQ 2, FabFilter Pro-Q 3",
        "purpose": "Limpiar frecuencias indeseadas generadas por la distorsion, reforzar cuerpo",
    },
    {
        "step": 5,
        "name": "Compression",
        "description": "Compresion para controlar dinamica",
        "plugins": "Fruity Limiter (nativo), Waves CLA-76, FabFilter Pro-C 2",
        "purpose": "Controlar picos y mantener energia constante del bajo",
    },
    {
        "step": 6,
        "name": "Soft Clipper",
        "description": "Soft clipping para controlar picos sin distorsion fea",
        "plugins": "Fruity Soft Clipper",
        "purpose": "Redondear picos. Sube volumen del bajo hasta que clipee, el clipper lo redondea.",
    },
    {
        "step": 7,
        "name": "Limiter",
        "description": "Limitador como proteccion final",
        "plugins": "Fruity Limiter, FabFilter Pro-L 2",
        "purpose": "Proteccion final. Ningun pico pasa de aqui. Ceiling a -0.3dB.",
    },
]


# ============================================================================
# 3. BASS GROWL TECHNIQUES (4-step process)
# ============================================================================

BASS_GROWL_TECHNIQUES: Dict[str, Dict] = {
    "step_1_base": {
        "name": "Paso 1: El Bajo Base",
        "description": "Usa un 808 limpio o un sub bass (seno puro)",
        "plugins": {
            "3x_osc": {
                "name": "3x Osc (nativo FL)",
                "type": "Synth basico",
                "waveform": "Sine (seno)",
                "use_case": "Sub bass limpio",
            },
            "sytrus": {
                "name": "Sytrus (nativo FL)",
                "type": "FM Synthesis",
                "use_case": "Bajos agresivos con FM synthesis",
            },
            "serum": {
                "name": "Serum (Xfer)",
                "type": "Wavetable Synth",
                "use_case": "EL REY de los bajos modernos",
                "price": "$189",
            },
            "vital": {
                "name": "Vital (Matt Tytel)",
                "type": "Wavetable Synth",
                "use_case": "Alternativa brutal a Serum",
                "price": "GRATIS",
            },
        },
    },
    "step_2_distortion": {
        "name": "Paso 2: Distorsion (AQUI ESTA LA MAGIA)",
        "description": "Esto es lo que hace que 'ruja'",
        "options": {
            "camel_crusher": {
                "name": "Camel Crusher",
                "price": "GRATIS",
                "label": "El clasico",
                "settings": {
                    "distortion": "60-80%",
                    "filter": "LP, Cutoff al gusto",
                    "compressor": "ON, al maximo",
                },
                "notes": "Esto solo ya suena BRUTAL en un 808",
            },
            "fabfilter_saturn_2": {
                "name": "FabFilter Saturn 2",
                "price": "$$$",
                "label": "El profesional",
                "settings": {
                    "band_split": {
                        "sub": {"range": "0-80Hz", "distortion": "SIN distorsion (mantener limpio)"},
                        "mid": {"range": "80-500Hz", "distortion": "Tube o Tape saturation al 40-70%"},
                        "high": {"range": "500Hz+", "distortion": "Clip o Destroy al 30-50%"},
                    },
                },
                "notes": "La clave: distorsionar ARRIBA pero mantener el sub LIMPIO",
            },
            "soundtoys_decapitator": {
                "name": "Soundtoys Decapitator",
                "price": "$$",
                "label": "Caracter analogico",
                "settings": {
                    "style": "A (American) o T (Tape) para 808s",
                    "drive": "4-7 (de 10)",
                    "tone": "medio-alto",
                    "mix": "50-80%",
                },
                "notes": "Caracter analogico, suena a vinilo roto",
            },
            "blood_overdrive": {
                "name": "Blood Overdrive (nativo FL)",
                "price": "GRATIS",
                "label": "Nativo FL Studio",
                "settings": {
                    "preband": "30-50%",
                    "color": "50-70%",
                    "preamp": "60-80%",
                    "x100": "ON para mas agresividad",
                },
                "notes": "Nativo de FL, decente para empezar",
            },
            "fruity_waveshaper": {
                "name": "Fruity Waveshaper (nativo FL)",
                "price": "GRATIS",
                "label": "Control total de waveshaping",
                "settings": {
                    "curve": "Dibuja curva con 'clips' (esquinas duras)",
                    "mix": "40-60%",
                },
                "notes": "Cuanto mas agresiva la curva = mas rugido. Requiere saber usarlo.",
            },
            "distructor": {
                "name": "Distructor (nativo FL)",
                "price": "GRATIS",
                "label": "Multibanda nativo",
                "settings": {
                    "pre": "Medio-alto",
                    "bands": "Enciende varias bandas de distorsion",
                    "mix": "Ajusta el mix por banda",
                },
                "notes": "Interfaz confusa pero potente para multiband distortion",
            },
        },
    },
    "step_3_post_eq": {
        "name": "Paso 3: EQ Post-Distorsion",
        "description": "Limpiar y reforzar despues de la distorsion",
        "settings": {
            "high_pass": {"freq": "30Hz", "purpose": "Quitar sub-frecuencias inaudibles"},
            "boost_sub": {"freq": "60-80Hz", "gain": "+3dB", "purpose": "Sentir el golpe en el pecho"},
            "boost_body": {"freq": "150-300Hz", "gain": "+2-4dB", "purpose": "El 'cuerpo' del rugido"},
            "cut_cardboard": {"freq": "400-600Hz", "gain": "-2dB", "purpose": "Zona 'carton' - cortar"},
            "boost_presence": {"freq": "1-3kHz", "gain": "+2dB", "purpose": "El 'crack' y presencia"},
            "low_pass": {"freq": "8-10kHz", "purpose": "Quitar ruido de la distorsion"},
        },
    },
    "step_4_compression": {
        "name": "Paso 4: Compresion",
        "description": "Controlar dinamica y mantener energia",
        "settings": {
            "ratio": "4:1 a 8:1",
            "attack": "LENTO (20-50ms) - deja pasar el transiente/golpe",
            "release": "RAPIDO (50-100ms) - mantiene la energia",
            "gain_reduction": "3-6dB",
        },
        "plugins": [
            "Fruity Limiter (nativo)",
            "Waves CLA-76",
            "FabFilter Pro-C 2",
        ],
    },
}


# ============================================================================
# 4. BASS GOLDEN RULES
# ============================================================================

BASS_GOLDEN_RULES: List[Dict[str, str]] = [
    {
        "rule": "El bajo sigue la armonia pero NO es copia exacta",
        "description": (
            "El bajo debe seguir las notas raiz de los acordes pero con ritmo "
            "y movimiento propio. No duplicar la melodia exacta."
        ),
    },
    {
        "rule": "Dejar espacio - menos es mas",
        "description": (
            "El bajo no necesita tocar en cada beat. Los silencios dan impacto "
            "a las notas que SI suenan. En boom bap especialmente, el espacio es clave."
        ),
    },
    {
        "rule": "Kick y bajo NO simultaneos (o con sidechain)",
        "description": (
            "Si el kick y el bajo suenan exactamente al mismo tiempo sin sidechain, "
            "compiten por las mismas frecuencias y el mix se enturbia. Usa sidechain "
            "o desplaza el bajo ligeramente."
        ),
    },
    {
        "rule": "Rango optimo: C1 a C2 (MIDI 24-48)",
        "description": (
            "El bajo vive entre C1 y C2. Mas abajo se pierde en altavoces pequenos. "
            "Mas arriba deja de ser 'bajo' y entra en territorio de mid-range."
        ),
    },
    {
        "rule": "MONO por debajo de 200Hz (IMPORTANTISIMO)",
        "description": (
            "TODO lo que este debajo de 200Hz debe ser MONO. Si el bajo es estereo "
            "abajo pierde potencia en altavoces. Usar Fruity Stereo Enhancer con "
            "'Stereo Sep' en 0 para bajas freq, o Maximus con banda LOW en mono."
        ),
    },
    {
        "rule": "Armonicos para compatibilidad con telefonos",
        "description": (
            "Los telefonos NO reproducen frecuencias debajo de ~80Hz. Anadir "
            "armonicos (2do y 3er armonico) con saturacion sutil para que el "
            "bajo 'se sienta' incluso en audifonos malos."
        ),
    },
]


# ============================================================================
# 5. BASS TRICKS (Production hacks)
# ============================================================================

BASS_TRICKS: List[Dict[str, object]] = [
    {
        "id": "soft_clipper",
        "name": "Soft Clipper = Tu Mejor Amigo",
        "description": (
            "Fruity Soft Clipper al final de la cadena del bajo. "
            "Sube el volumen del bajo hasta que clipee. El soft clipper "
            "'redondea' los picos = bajo mas alto sin distorsion fea."
        ),
        "steps": [
            "Insertar Fruity Soft Clipper al final de la cadena de FX",
            "Subir volumen del bajo hasta que empiece a clipear",
            "El clipper redondea los picos automaticamente",
            "TRUCO: Sube el threshold del clipper y baja post-gain",
        ],
        "plugin": "Fruity Soft Clipper",
    },
    {
        "id": "808_layering",
        "name": "808 Que Pega Mas Fuerte",
        "description": (
            "Capa un kick corto (transiente) + 808 largo (cuerpo). "
            "El kick da el 'punch', el 808 da el 'boom'."
        ),
        "steps": [
            "Usar un kick corto (solo transiente, 2-5kHz dominante)",
            "Usar un 808 largo (cuerpo, 40-80Hz dominante)",
            "Alinear el inicio de ambos perfectamente",
            "EQ: el kick domina 2-5kHz, el 808 domina 40-80Hz",
        ],
        "plugin": "Mixer routing + Parametric EQ 2",
    },
    {
        "id": "sidechain",
        "name": "Sidechain Perfecto",
        "description": (
            "Fruity Limiter en el bajo, sidechain desde el kick. "
            "El bajo 'desaparece' cuando pega el kick = limpieza total."
        ),
        "steps": [
            "Insertar Fruity Limiter en el canal del bajo",
            "Configurar sidechain desde el canal del kick",
            "Attack: 0.5ms (instantaneo)",
            "Release: 100-200ms (ajustar al tempo)",
            "Ratio: al maximo",
        ],
        "plugin": "Fruity Limiter",
        "settings": {
            "attack_ms": 0.5,
            "release_ms": "100-200",
            "ratio": "max",
        },
    },
    {
        "id": "glide_slide",
        "name": "Glide/Slide del 808",
        "description": (
            "En el Piano Roll: herramienta slide (triangulo). "
            "El 808 'resbala' entre notas (sonido trap clasico)."
        ),
        "steps": [
            "En el Piano Roll: seleccionar herramienta slide (triangulo)",
            "Poner una nota slide encima de la nota principal",
            "Ajustar portamento en el sampler: 100-300ms",
            "El 808 'resbala' entre notas",
        ],
        "plugin": "Piano Roll + Sampler settings",
        "settings": {
            "portamento_ms": "100-300",
        },
    },
    {
        "id": "mono_bass",
        "name": "Mono Bass (IMPORTANTISIMO)",
        "description": (
            "TODO lo que este debajo de 200Hz debe ser MONO. "
            "Si el bajo es estereo abajo pierde potencia en altavoces."
        ),
        "steps": [
            "Fruity Stereo Enhancer: 'Stereo Sep' en 0 para bajas freq",
            "O usar Maximus: banda LOW en mono",
            "Verificar en mono (boton mono en el master mixer)",
        ],
        "plugin": "Fruity Stereo Enhancer o Maximus",
        "settings": {
            "stereo_sep_low": 0,
            "freq_crossover": "200Hz",
        },
    },
    {
        "id": "harmonics_boost",
        "name": "Boost de Harmonicos (Bajo que se oye en telefonos)",
        "description": (
            "Los telefonos NO reproducen frecuencias debajo de ~80Hz. "
            "Anadir armonicos para que el bajo 'se sienta' incluso en audifonos malos."
        ),
        "steps": [
            "Opcion A: Waves MaxxBass o Waves LoAir",
            "Opcion B: Duplicar el bajo, subir una octava, bajar volumen -12dB, distorsionar ligeramente",
            "La saturacion sutil genera 2do y 3er armonico",
            "Ahora el bajo 'se siente' incluso en audifonos malos",
        ],
        "plugin": "Waves MaxxBass / Waves LoAir / Saturacion manual",
        "settings": {
            "duplicate_octave_offset": "+1 octava",
            "duplicate_volume_db": -12,
            "duplicate_distortion": "leve",
        },
    },
    {
        "id": "drive_automation",
        "name": "Automatizar el Drive",
        "description": (
            "Crear automation clip en el knob de distorsion. "
            "Sube la distorsion en el climax/drop, baja en las partes suaves."
        ),
        "steps": [
            "Click derecho en el knob de distorsion -> 'Create automation clip'",
            "Dibujar curva: bajo en verso, alto en climax/drop",
            "Esto da dinamica y emocion al bajo",
            "Atajo: Ctrl + T para crear automation clip",
        ],
        "plugin": "Cualquier plugin con drive/distorsion",
    },
    {
        "id": "bass_layering",
        "name": "Layering de Bajos (3 Capas)",
        "description": (
            "3 capas de bajo, cada una con su rango de frecuencias. "
            "Bajo ENORME que suena bien en todo sistema."
        ),
        "steps": [
            "Capa 1 (Sub): Seno puro, 0-80Hz - el peso",
            "Capa 2 (Mid bass): Saw/square, 80-300Hz - el cuerpo",
            "Capa 3 (Top bass): Con distorsion, 300Hz+ - el caracter",
            "EQ cada capa para que no se pisen",
        ],
        "layers": {
            "sub": {
                "waveform": "sine",
                "freq_range": "0-80Hz",
                "purpose": "El peso",
                "distortion": "none",
            },
            "mid": {
                "waveform": "saw/square",
                "freq_range": "80-300Hz",
                "purpose": "El cuerpo",
                "distortion": "moderate",
            },
            "top": {
                "waveform": "any + distortion",
                "freq_range": "300Hz+",
                "purpose": "El caracter",
                "distortion": "heavy",
            },
        },
        "plugin": "Multiple instances + Parametric EQ 2",
    },
]


# ============================================================================
# 6. DISTORTION PLUGINS COMPARISON
# ============================================================================

DISTORTION_PLUGINS: Dict[str, Dict] = {
    "fabfilter_saturn_2": {
        "name": "FabFilter Saturn 2",
        "strength": "Multibanda, versatil, visual",
        "weakness": "Precio alto",
        "price": "$$$",
        "is_free": False,
        "is_native_fl": False,
        "multiband": True,
        "settings": {
            "band_sub": {"range": "0-80Hz", "mode": "BYPASS (sin distorsion)", "amount": 0},
            "band_mid": {"range": "80-500Hz", "mode": "Tube o Tape", "amount": "40-70%"},
            "band_high": {"range": "500Hz+", "mode": "Clip o Destroy", "amount": "30-50%"},
        },
        "best_for": ["Multiband bass processing", "Professional mix", "Versatile saturation"],
        "notes": "La clave: distorsionar ARRIBA pero mantener el sub LIMPIO",
    },
    "soundtoys_decapitator": {
        "name": "Soundtoys Decapitator",
        "strength": "Caracter analogico brutal",
        "weakness": "No es multibanda",
        "price": "$$",
        "is_free": False,
        "is_native_fl": False,
        "multiband": False,
        "settings": {
            "style": "A (American) o T (Tape) para 808s",
            "drive": "4-7 (de 10)",
            "tone": "medio-alto",
            "mix": "50-80%",
        },
        "best_for": ["Analog character", "808 warmth", "Vinyl-like distortion"],
        "notes": "Caracter analogico, suena a vinilo roto",
    },
    "izotope_trash_2": {
        "name": "iZotope Trash 2",
        "strength": "Diseno de distorsion completo",
        "weakness": "Descontinuado (buscar segunda mano)",
        "price": "$$",
        "is_free": False,
        "is_native_fl": False,
        "multiband": True,
        "settings": {},
        "best_for": ["Extreme sound design", "Creative distortion"],
        "notes": "Descontinuado pero muy buscado",
    },
    "camel_crusher": {
        "name": "Camel Crusher",
        "strength": "GRATIS, facil, suena increible",
        "weakness": "Basico, sin updates",
        "price": "GRATIS",
        "is_free": True,
        "is_native_fl": False,
        "multiband": False,
        "settings": {
            "distortion": "60-80%",
            "filter": "LP, Cutoff al gusto",
            "compressor": "ON, al maximo",
        },
        "best_for": ["Quick 808 growl", "Beginners", "Classic distortion"],
        "notes": "Esto solo ya suena BRUTAL en un 808. El clasico gratuito.",
        "comparable_to": "Decapitator + comp",
    },
    "waves_berzerk": {
        "name": "Waves Berzerk",
        "strength": "Creativo, presets locos",
        "weakness": "Puede ser excesivo",
        "price": "$$",
        "is_free": False,
        "is_native_fl": False,
        "multiband": False,
        "settings": {},
        "best_for": ["Creative distortion", "Experimental bass"],
        "notes": "Puede ser excesivo, usar con cuidado",
    },
    "blood_overdrive": {
        "name": "Blood Overdrive",
        "strength": "NATIVO FL, decente",
        "weakness": "Limitado",
        "price": "GRATIS",
        "is_free": True,
        "is_native_fl": True,
        "multiband": False,
        "settings": {
            "preband": "30-50%",
            "color": "50-70%",
            "preamp": "60-80%",
            "x100": "ON para mas agresividad",
        },
        "best_for": ["Quick bass distortion", "FL Studio native workflow"],
        "notes": "Nativo de FL, no necesitas instalar nada. Bueno para empezar.",
    },
    "fruity_waveshaper": {
        "name": "Fruity Waveshaper",
        "strength": "NATIVO FL, control total",
        "weakness": "Requiere saber usarlo",
        "price": "GRATIS",
        "is_free": True,
        "is_native_fl": True,
        "multiband": False,
        "settings": {
            "curve": "Dibujar curva con 'clips' (esquinas duras)",
            "mix": "40-60%",
        },
        "best_for": ["Custom waveshaping", "Precise distortion design"],
        "notes": "Cuanto mas agresiva la curva = mas rugido",
    },
    "distructor": {
        "name": "Distructor",
        "strength": "NATIVO FL, multibanda",
        "weakness": "Interfaz confusa",
        "price": "GRATIS",
        "is_free": True,
        "is_native_fl": True,
        "multiband": True,
        "settings": {
            "pre": "Selecciona 'Pre' en medio-alto",
            "bands": "Enciende varias bandas de distorsion",
            "mix": "Ajustar el mix por banda",
        },
        "best_for": ["Multiband distortion (free)", "FL Studio native"],
        "notes": "Interfaz confusa pero es multiband distortion gratuito",
    },
    "fruity_fast_dist": {
        "name": "Fruity Fast Dist",
        "strength": "NATIVO FL, rapido",
        "weakness": "Muy basico",
        "price": "GRATIS",
        "is_free": True,
        "is_native_fl": True,
        "multiband": False,
        "settings": {
            "amount": "Al gusto",
        },
        "best_for": ["Quick texture", "High frequency crunch"],
        "notes": "Distorsion rapida, buena para la capa HIGH del multiband",
    },
}


# ============================================================================
# 7. MULTIBAND DISTORTION TECHNIQUES
# ============================================================================

MULTIBAND_DISTORTION_TECHNIQUES: Dict[str, Dict] = {
    "saturn_2_method": {
        "name": "Metodo 1: FabFilter Saturn 2",
        "description": "El metodo mas facil. Un solo plugin hace todo.",
        "difficulty": "facil",
        "cost": "$$$ (plugin de pago)",
        "bands": {
            "sub": {
                "range": "0-80Hz",
                "processing": "SIN distorsion. Mantener limpio para que no distorsione el sub.",
                "distortion_type": None,
                "distortion_amount": 0,
            },
            "mid": {
                "range": "80-500Hz",
                "processing": "Tube o Tape saturation. Este es el 'rugido'.",
                "distortion_type": "Tube / Tape",
                "distortion_amount": "40-70%",
            },
            "high": {
                "range": "500Hz+",
                "processing": "Clip o Destroy. Este es el 'crujido'.",
                "distortion_type": "Clip / Destroy",
                "distortion_amount": "30-50%",
            },
        },
        "result": "Bajo que RUGE arriba y PEGA limpio abajo",
    },
    "fl_native_method": {
        "name": "Metodo 2: Plugins Nativos de FL (GRATIS)",
        "description": "Usando sends del mixer para crear multiband manualmente.",
        "difficulty": "intermedio",
        "cost": "GRATIS (todo nativo)",
        "setup_steps": [
            "Mandar el bajo a 3 canales del Mixer usando sends",
        ],
        "bands": {
            "sub": {
                "channel_name": "SUB",
                "range": "Low-pass en 80Hz",
                "plugins": ["Parametric EQ 2: Low-pass en 80Hz"],
                "distortion": "SIN distorsion. Solo el golpe limpio del sub.",
                "volume": "Full",
            },
            "mid_growl": {
                "channel_name": "MID GROWL",
                "range": "Band-pass 80Hz - 500Hz",
                "plugins": [
                    "Parametric EQ 2: Band-pass 80Hz - 500Hz",
                    "Blood Overdrive: PreAmp al 70-90%",
                    "Otro EQ despues para limpiar",
                ],
                "distortion": "Blood Overdrive con PreAmp al 70-90%. Este es el rugido.",
                "volume": "Full",
            },
            "high_crack": {
                "channel_name": "HIGH CRACK",
                "range": "High-pass 500Hz",
                "plugins": [
                    "Parametric EQ 2: High-pass 500Hz",
                    "Fruity Waveshaper: curva agresiva",
                    "Fruity Fast Dist: al gusto",
                ],
                "distortion": "Waveshaper agresivo + Fast Dist. Solo 'textura'.",
                "volume": "Bajo (es solo textura, no debe dominar)",
            },
        },
        "final_step": "Mezclar los 3 canales en un bus 'BASS MASTER'",
        "result": "Bajo que RUGE arriba y PEGA limpio abajo (gratis)",
    },
}


# ============================================================================
# FREE PLUGINS THAT RIVAL PAID ONES (for bass)
# ============================================================================

FREE_BASS_PLUGINS: List[Dict[str, str]] = [
    {"name": "Camel Crusher", "function": "Distorsion + comp", "comparable_to": "Decapitator + comp"},
    {"name": "Vital", "function": "Sintetizador completo", "comparable_to": "Serum ($189)"},
    {"name": "Softube Saturation Knob", "function": "Saturacion simple", "comparable_to": "Cualquier saturador"},
    {"name": "OTT (Xfer)", "function": "Compresion multibanda", "comparable_to": "Multiband comp pro"},
    {"name": "Frontier (D16)", "function": "Limiter", "comparable_to": "FabFilter Pro-L"},
    {"name": "TDR Nova", "function": "EQ dinamico", "comparable_to": "FabFilter Pro-Q"},
    {"name": "Voxengo SPAN", "function": "Analizador de espectro", "comparable_to": "Ver que hace tu bajo"},
    {"name": "TAL-Filter-2", "function": "Filtro con LFO", "comparable_to": "Efectos de filtro"},
]

FL_NATIVE_BASS_PLUGINS: List[Dict[str, str]] = [
    {"name": "Sytrus", "function": "Synth FM (bajos brutales)"},
    {"name": "3x Osc", "function": "Synth basico (sub bass)"},
    {"name": "Parametric EQ 2", "function": "EQ (excelente)"},
    {"name": "Blood Overdrive", "function": "Distorsion"},
    {"name": "Fruity Waveshaper", "function": "Waveshaping"},
    {"name": "Distructor", "function": "Distorsion multibanda"},
    {"name": "Fruity Soft Clipper", "function": "Soft clipping"},
    {"name": "Fruity Limiter", "function": "Compresor + limiter"},
    {"name": "Fruity Fast Dist", "function": "Distorsion rapida"},
    {"name": "Maximus", "function": "Multiband comp/limit"},
    {"name": "Fruity Stereo Enhancer", "function": "Control estereo"},
]


# ============================================================================
# RECOMMENDED SETUPS
# ============================================================================

RECOMMENDED_SETUPS: Dict[str, Dict] = {
    "beginner_free": {
        "name": "Para Empezar (gratis)",
        "plugins": [
            "Vital (sintetizador - genera los bajos)",
            "Camel Crusher (distorsion - hace que rujan)",
            "OTT (compresion multibanda)",
            "Softube Saturation Knob (saturacion extra)",
            "+ TODO lo nativo de FL que ya tienes",
        ],
    },
    "professional": {
        "name": "Setup Profesional",
        "plugins": [
            "Serum (Xfer) - el synth de bajos #1",
            "FabFilter Saturn 2 - distorsion multibanda pro",
            "FabFilter Pro-Q 3 - EQ",
            "FabFilter Pro-C 2 - compresion",
            "Soundtoys Decapitator - saturacion con caracter",
        ],
    },
    "quick_growl": {
        "name": "Respuesta Rapida: Como hago que el bajo ruja",
        "steps": [
            "1. Pon un 808 o sub bass",
            "2. Mete Camel Crusher (gratis) con distorsion al 60-80%",
            "3. Pon un EQ despues: corta lo feo, sube 60Hz y 200Hz",
            "4. Fruity Soft Clipper al final",
            "5. LISTO - ya ruge",
        ],
    },
}


# ============================================================================
# BASSLINE GENERATION FUNCTION
# ============================================================================

# Scale intervals used internally for walking bass
_SCALE_INTERVALS = {
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic_minor": [0, 3, 5, 7, 10],
}


def _nearest_scale_tone(midi_note: int, root_midi: int, scale: List[int]) -> int:
    """Find the nearest note that belongs to the scale."""
    best = midi_note
    best_dist = 128
    for octave_offset in range(-1, 2):
        for interval in scale:
            candidate = root_midi + octave_offset * 12 + interval
            dist = abs(candidate - midi_note)
            if dist < best_dist:
                best_dist = dist
                best = candidate
    return max(0, min(127, best))


def _get_bpm_style_recommendation(bpm: float) -> str:
    """Get bassline style recommendation based on BPM."""
    if bpm >= 130:
        return "sub_808 (recomendado para tempos rapidos: el 808 largo es el estandar en trap/phonk/drill)"
    elif bpm >= 95:
        return "root_follow o syncopated (tempo medio: ambos funcionan bien)"
    else:
        return "walking o syncopated (tempos lentos: hay espacio para mas notas y groove)"


def generate_bassline_notes(
    root_notes: List[str],
    style: str = "root_follow",
    bars: int = 4,
    octave: int = 1,
    velocity: int = 100,
    bpm: float = 0.0,
) -> str:
    """Generate a bassline as note data compatible with send_melody().

    Produces notes in "note,velocity,length,position" format, one per line.
    When BPM is provided, note lengths and rhythmic patterns adapt to the tempo.

    Args:
        root_notes: List of root note names for each chord/bar, e.g. ["A", "G", "F", "E"].
                    If fewer roots than bars, the list cycles.
        style: Bassline style. One of:
               - "root_follow"  : Root notes on the beat, simple and solid.
               - "walking"      : Passing tones between roots (jazz/boom-bap).
               - "syncopated"   : Boom bap bounce with offbeat accents.
               - "sub_808"      : Long sustained 808 notes (trap/phonk).
        bars: Number of bars to generate (4/4 time, 4 beats per bar).
        octave: MIDI octave for the bass (default 1, C1-C2 range per golden rules).
        velocity: Base MIDI velocity (0-127).
        bpm: Current tempo in BPM. When > 0, adjusts note lengths and patterns:
             - sub_808 at fast BPM (130+): full sustain, no gaps
             - walking at slow BPM (<90): adds extra passing tones
             - syncopated: adjusts ghost note density based on tempo

    Returns:
        Multi-line string with "midi_note,velocity,length,position" per line.
    """
    if not root_notes:
        raise ValueError("root_notes must contain at least one note name")

    if style not in ("root_follow", "walking", "syncopated", "sub_808"):
        raise ValueError(
            f"Unknown style '{style}'. Choose from: root_follow, walking, syncopated, sub_808"
        )

    lines: List[str] = []
    beats_per_bar = 4.0

    # BPM-aware adjustments
    is_fast = bpm >= 130 if bpm > 0 else False
    is_slow = bpm <= 85 if bpm > 0 else False

    for bar in range(bars):
        root_name = root_notes[bar % len(root_notes)]
        root_midi = note_to_midi(root_name, octave)
        bar_start = bar * beats_per_bar

        # Determine next root for passing tones
        next_root_name = root_notes[(bar + 1) % len(root_notes)]
        next_root_midi = note_to_midi(next_root_name, octave)

        # Minor scale from the current root for walking/passing tones
        scale = _SCALE_INTERVALS["minor"]

        if style == "root_follow":
            if is_fast:
                # Fast tempo: longer sustain on root, simpler pattern
                lines.append(f"{root_midi},{velocity},{2.5},{bar_start:.2f}")
                fifth = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{fifth},{int(velocity * 0.8)},{1.25},{bar_start + 2.5:.2f}")
            else:
                # Standard: root on beats 1 and 3
                lines.append(f"{root_midi},{velocity},{1.5},{bar_start:.2f}")
                fifth = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{fifth},{int(velocity * 0.85)},{1.5},{bar_start + 2.0:.2f}")

        elif style == "walking":
            if is_fast:
                # Fast tempo: half notes instead of quarters (less busy)
                lines.append(f"{root_midi},{velocity},{1.8},{bar_start:.2f}")
                passing_2 = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{passing_2},{int(velocity * 0.85)},{1.8},{bar_start + 2.0:.2f}")
            elif is_slow:
                # Slow tempo: 8th note walking (more space to fill)
                lines.append(f"{root_midi},{velocity},{0.9},{bar_start:.2f}")
                # Extra passing tone on the "and" of 1
                passing_half = _nearest_scale_tone(root_midi + 2, root_midi, scale)
                lines.append(f"{passing_half},{int(velocity * 0.65)},{0.4},{bar_start + 0.5:.2f}")
                # Beat 2: third
                passing_1 = _nearest_scale_tone(root_midi + 3, root_midi, scale)
                lines.append(f"{passing_1},{int(velocity * 0.8)},{0.9},{bar_start + 1.0:.2f}")
                # "and" of 2
                passing_1b = _nearest_scale_tone(root_midi + 5, root_midi, scale)
                lines.append(f"{passing_1b},{int(velocity * 0.65)},{0.4},{bar_start + 1.5:.2f}")
                # Beat 3: fifth
                passing_2 = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{passing_2},{int(velocity * 0.85)},{0.9},{bar_start + 2.0:.2f}")
                # "and" of 3
                passing_2b = _nearest_scale_tone(root_midi + 8, root_midi, scale)
                lines.append(f"{passing_2b},{int(velocity * 0.6)},{0.4},{bar_start + 2.5:.2f}")
                # Beat 4: chromatic approach
                if next_root_midi > root_midi:
                    approach = next_root_midi - 1
                elif next_root_midi < root_midi:
                    approach = next_root_midi + 1
                else:
                    approach = _nearest_scale_tone(root_midi + 10, root_midi, scale)
                approach = max(0, min(127, approach))
                lines.append(f"{approach},{int(velocity * 0.75)},{0.9},{bar_start + 3.0:.2f}")
            else:
                # Standard walking
                lines.append(f"{root_midi},{velocity},{0.9},{bar_start:.2f}")
                passing_1 = _nearest_scale_tone(root_midi + 3, root_midi, scale)
                lines.append(f"{passing_1},{int(velocity * 0.8)},{0.9},{bar_start + 1.0:.2f}")
                passing_2 = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{passing_2},{int(velocity * 0.85)},{0.9},{bar_start + 2.0:.2f}")
                if next_root_midi > root_midi:
                    approach = next_root_midi - 1
                elif next_root_midi < root_midi:
                    approach = next_root_midi + 1
                else:
                    approach = _nearest_scale_tone(root_midi + 10, root_midi, scale)
                approach = max(0, min(127, approach))
                lines.append(f"{approach},{int(velocity * 0.75)},{0.9},{bar_start + 3.0:.2f}")

        elif style == "syncopated":
            if is_fast:
                # Fast tempo: simpler syncopation, fewer ghost notes
                lines.append(f"{root_midi},{velocity},{1.5},{bar_start:.2f}")
                fifth = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{fifth},{int(velocity * 0.9)},{1.0},{bar_start + 1.5:.2f}")
                lines.append(f"{root_midi},{int(velocity * 0.8)},{1.0},{bar_start + 3.0:.2f}")
            else:
                # Standard syncopated
                lines.append(f"{root_midi},{velocity},{1.0},{bar_start:.2f}")
                fifth = _nearest_scale_tone(root_midi + 7, root_midi, scale)
                lines.append(f"{fifth},{int(velocity * 0.9)},{0.75},{bar_start + 1.5:.2f}")
                octave_note = root_midi + 12 if root_midi + 12 <= 127 else root_midi
                lines.append(f"{octave_note},{int(velocity * 0.6)},{0.5},{bar_start + 2.5:.2f}")
                lines.append(f"{root_midi},{int(velocity * 0.8)},{0.75},{bar_start + 3.25:.2f}")

        elif style == "sub_808":
            if is_fast:
                # Fast BPM (trap/phonk/drill): full bar sustain, no gap
                # At 140 BPM each bar is ~1.7 seconds - the 808 needs to fill it completely
                note_length = beats_per_bar
                lines.append(f"{root_midi},{velocity},{note_length:.2f},{bar_start:.2f}")
            else:
                # Slower tempos: leave a small gap for the next hit to breathe
                note_length = beats_per_bar - 0.25
                lines.append(f"{root_midi},{velocity},{note_length:.2f},{bar_start:.2f}")

    return "\n".join(lines)


# ============================================================================
# HELPER / FORMATTING FUNCTIONS
# ============================================================================

def format_bass_type_info(genre: str) -> str:
    """Format bass type information for a given genre as a readable string."""
    if genre not in BASS_TYPES:
        available = ", ".join(BASS_TYPES.keys())
        return f"Unknown genre '{genre}'. Available: {available}"

    info = BASS_TYPES[genre]
    lines = [
        f"=== {info['name']} ===",
        f"Tipos: {', '.join(info['types'])}",
        f"Descripcion: {info['description']}",
        "Caracteristicas:",
    ]
    for char in info["key_characteristics"]:
        lines.append(f"  - {char}")
    lines.append(f"Plugins: {', '.join(info['common_plugins'])}")
    lines.append(f"EQ: {info['eq_focus']}")
    lines.append(f"Distorsion: {info['distortion']}")
    lines.append(f"Sidechain: {info['sidechain']}")
    return "\n".join(lines)


def format_processing_chain() -> str:
    """Format the bass processing chain as a readable string."""
    lines = ["=== CADENA DE PROCESAMIENTO DE BAJO ===\n"]
    for step in BASS_PROCESSING_CHAIN:
        lines.append(f"{step['step']}. {step['name']}")
        lines.append(f"   Plugins: {step['plugins']}")
        lines.append(f"   Proposito: {step['purpose']}")
        lines.append("")
    return "\n".join(lines)


def format_growl_guide() -> str:
    """Format the complete bass growl technique as a readable string."""
    lines = ["=== COMO HACER QUE EL BAJO 'RUJA' (BASS GROWL) ===\n"]

    # Step 1
    s1 = BASS_GROWL_TECHNIQUES["step_1_base"]
    lines.append(f"--- {s1['name']} ---")
    lines.append(f"{s1['description']}")
    for pid, pinfo in s1["plugins"].items():
        lines.append(f"  * {pinfo['name']} - {pinfo['use_case']}")
    lines.append("")

    # Step 2
    s2 = BASS_GROWL_TECHNIQUES["step_2_distortion"]
    lines.append(f"--- {s2['name']} ---")
    for opt_id, opt in s2["options"].items():
        lines.append(f"  OPCION: {opt['name']} ({opt['price']}) - {opt['label']}")
        if isinstance(opt["settings"], dict):
            for k, v in opt["settings"].items():
                if isinstance(v, dict):
                    for bk, bv in v.items():
                        lines.append(f"    {bk}: {bv}")
                else:
                    lines.append(f"    {k}: {v}")
        lines.append(f"    >>> {opt['notes']}")
        lines.append("")

    # Step 3
    s3 = BASS_GROWL_TECHNIQUES["step_3_post_eq"]
    lines.append(f"--- {s3['name']} ---")
    for eq_id, eq_setting in s3["settings"].items():
        freq = eq_setting.get("freq", "")
        gain = eq_setting.get("gain", "")
        purpose = eq_setting.get("purpose", "")
        gain_str = f" ({gain})" if gain else ""
        lines.append(f"  {freq}{gain_str}: {purpose}")
    lines.append("")

    # Step 4
    s4 = BASS_GROWL_TECHNIQUES["step_4_compression"]
    lines.append(f"--- {s4['name']} ---")
    for k, v in s4["settings"].items():
        lines.append(f"  {k}: {v}")
    lines.append(f"  Plugins: {', '.join(s4['plugins'])}")

    return "\n".join(lines)


def format_golden_rules() -> str:
    """Format golden rules as a readable string."""
    lines = ["=== REGLAS DE ORO DEL BAJO ===\n"]
    for i, rule in enumerate(BASS_GOLDEN_RULES, 1):
        lines.append(f"{i}. {rule['rule']}")
        lines.append(f"   {rule['description']}")
        lines.append("")
    return "\n".join(lines)


def list_distortion_plugins(free_only: bool = False, native_only: bool = False) -> str:
    """List distortion plugins with their settings, optionally filtered."""
    lines = ["=== PLUGINS DE DISTORSION PARA BAJO ===\n"]

    for pid, plugin in DISTORTION_PLUGINS.items():
        if free_only and not plugin["is_free"]:
            continue
        if native_only and not plugin["is_native_fl"]:
            continue

        lines.append(f"ID: {pid}")
        lines.append(f"  Nombre: {plugin['name']}")
        lines.append(f"  Fortaleza: {plugin['strength']}")
        lines.append(f"  Debilidad: {plugin['weakness']}")
        lines.append(f"  Precio: {plugin['price']}")
        lines.append(f"  Multibanda: {'Si' if plugin['multiband'] else 'No'}")
        if plugin["settings"]:
            lines.append("  Settings:")
            for k, v in plugin["settings"].items():
                if isinstance(v, dict):
                    lines.append(f"    {k}:")
                    for sk, sv in v.items():
                        lines.append(f"      {sk}: {sv}")
                else:
                    lines.append(f"    {k}: {v}")
        lines.append(f"  Notas: {plugin['notes']}")
        lines.append("")

    return "\n".join(lines)
