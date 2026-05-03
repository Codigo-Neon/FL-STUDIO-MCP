"""Advanced mixing and mastering knowledge for FL Studio.

Covers gain staging, mixer layout, mixing order, genre differences,
parallel processing, bus processing, referencing, common mistakes,
and complete mixing checklists.
Extracted from GUIA_MEZCLA_MASTER_COMPLETA.txt.
"""

from typing import Dict, List, Optional


# ============================================================================
# 1. GAIN STAGING - Workflow completo con niveles en dB
# ============================================================================

GAIN_STAGING: Dict[str, Dict] = {
    "philosophy": {
        "name": "Filosofia del Gain Staging",
        "description": (
            "Antes de poner UN SOLO plugin, cada canal del mixer debe piquear entre "
            "-18 y -12 dBFS. Esto garantiza que los plugins trabajen en su rango optimo."
        ),
        "why": [
            "Si la senal entra al plugin a +6dB, va a distorsionar",
            "Si entra a -30dB, va a sonar con ruido",
            "SIEMPRE calibrar niveles ANTES de meter plugins",
        ],
    },
    "workflow": {
        "name": "Como hacer gain staging",
        "steps": [
            "1. Reproduce el proyecto sin plugins",
            "2. Cada canal individual: ajusta el fader para que piquee a -12dBFS",
            "3. El master debe quedar entre -6 y -3dBFS ANTES de mastering",
            "4. Si el master clipea, baja TODOS los faders proporcionalmente",
        ],
    },
    "target_levels": {
        "name": "Niveles objetivo por elemento",
        "levels": {
            "canal_individual": "-18 a -12 dBFS (pico)",
            "master_pre_mastering": "-6 a -3 dBFS (pico)",
            "master_post_mastering_ceiling": "-1.0 dB (boom bap) / -0.5 dB (trap)",
        },
    },
    "relative_levels": {
        "name": "Niveles relativos (kick = referencia 0dB)",
        "levels": {
            "kick": "0dB (referencia)",
            "snare": "-1 a +1dB",
            "hi_hats": "-8 a -5dB",
            "percusion": "-10 a -7dB",
            "bajo": "-3 a 0dB",
            "sample_melodia": "-6 a -3dB",
            "vinyl_crackle": "-20 a -12dB",
            "scratches": "-8 a -5dB",
            "voz_principal": "+2 a +4dB sobre el sample",
            "dobles_voz": "-6 a -10dB debajo de la voz principal",
            "ad_libs": "-8 a -12dB debajo de la principal",
        },
    },
}


# ============================================================================
# 2. MIXER LAYOUT - Layout recomendado del mixer de FL Studio
# ============================================================================

MIXER_LAYOUT: Dict[str, Dict] = {
    "inserts": {
        "name": "Estructura de Inserts del Mixer",
        "layout": {
            "1-2": "KICKS (kick principal + capa)",
            "3": "SNARE / CLAP",
            "4": "HI-HATS / SHAKERS / RIDES",
            "5": "PERCS (congas, bongos, rims, etc.)",
            "6-7": "BAJO / 808",
            "8-9": "SAMPLES / MELODIAS / CHOPS",
            "10": "PADS / TEXTURAS / ATMOSFERAS",
            "11": "VOZ PRINCIPAL",
            "12": "DOBLES / COROS",
            "13": "AD-LIBS",
            "14": "--- (reserva) ---",
        },
    },
    "buses": {
        "name": "Buses (grupos)",
        "layout": {
            "100": "BUS DRUMS (recibe sends de 1-5)",
            "101": "BUS MELODIAS (recibe sends de 8-10)",
            "102": "BUS VOCES (recibe sends de 11-13)",
            "103": "VOX REVERB (send, 100% wet)",
            "104": "VOX DELAY (send, 100% wet)",
            "105": "DRUM REVERB (send, 100% wet)",
        },
    },
    "master": {
        "name": "Master",
        "description": "Cadena de mastering final. Recibe la suma de todos los buses.",
    },
    "panning": {
        "name": "Panning (boom bap = estrecho, como estudio de los 90s)",
        "positions": {
            "centro_0": ["Kick", "Snare", "Bajo", "Voz principal"],
            "sutil_10_25": {
                "hi_hat": "15-20% Right",
                "ride": "15-20% Left",
                "sample_principal": "5-10% (muy sutil)",
            },
            "medio_25_50": {
                "open_hat": "25% Right",
                "shaker": "25% Left",
                "percusion_secundaria": "variado",
                "scratches": "variado",
            },
            "ancho_50_70": {
                "dobles_voz": "30-70% L y R (una copia a cada lado)",
                "strings_pads": "estereo natural",
                "elementos_ambientales": "variado",
            },
        },
        "rules": [
            "Nunca nada a 100% L/R en boom bap puro",
            "El boom bap suena ESTRECHO comparado con musica moderna",
            "Trap puede ser mas ancho: melodias y hats mas separados",
        ],
    },
}


# ============================================================================
# 3. MIXING ORDER - Orden paso a paso de mezcla
# ============================================================================

MIXING_ORDER: Dict[str, Dict] = {
    "fase_1_preparacion": {
        "name": "FASE 1: Preparacion",
        "order": 1,
        "tasks": [
            "Organizar canales en el mixer (routing, nombres, colores)",
            "Gain staging de TODOS los canales (-18 a -12dBFS)",
            "Limpieza con iZotope RX (voces, samples si lo necesitan)",
            "Configurar buses (drums, melodias, voces)",
            "Configurar sends (reverb, delay)",
            "Importar track de referencia (silenciado, solo para A/B)",
        ],
    },
    "fase_2_mezcla_individual": {
        "name": "FASE 2: Mezcla Individual (abajo hacia arriba)",
        "order": 2,
        "tasks": [
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
    },
    "fase_3_buses": {
        "name": "FASE 3: Buses (grupos)",
        "order": 3,
        "tasks": [
            "Bus drums - glue comp + saturacion",
            "Bus melodias - EQ(espacio voz) + glue comp",
            "Bus voces - glue comp + saturacion cohesion",
        ],
    },
    "fase_4_balances": {
        "name": "FASE 4: Balances",
        "order": 4,
        "tasks": [
            "Volumen relativo de cada grupo",
            "Voz 2-4dB por encima de la instrumental",
            "Escuchar a volumen bajo - se entiende la voz?",
            "Escuchar en mono - algo desaparece?",
            "A/B con referencia profesional",
        ],
    },
    "fase_5_master": {
        "name": "FASE 5: Master",
        "order": 5,
        "tasks": [
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
        ],
    },
    "fase_6_exportacion": {
        "name": "FASE 6: Exportacion",
        "order": 6,
        "tasks": [
            "File > Export > WAV",
            "Bit depth: 24-bit",
            "Sample rate: 44100 Hz (musica) o 48000 Hz (video)",
            "Dithering: activar en Ozone Maximizer si bajas a 16-bit",
            "Escuchar el archivo exportado de principio a fin",
            "Escuchar en el telefono, en el coche, con auriculares baratos",
        ],
    },
}


# ============================================================================
# 4. GENRE DIFFERENCES - Diferencias entre boom bap, trap y phonk
# ============================================================================

GENRE_DIFFERENCES: Dict[str, Dict] = {
    "boom_bap": {
        "name": "Boom Bap (90s)",
        "drums": "Samples de vinilo, sucios, con caracter",
        "bajo": "Sub limpio o bajo de sample (contrabajo, Rhodes bass)",
        "textura": "Lo-fi, cinta, polvo, calor analogico",
        "dinamica": "MAS dinamica, menos compresion, respira",
        "referencia": ["DJ Premier", "Pete Rock", "J Dilla", "9th Wonder", "Havoc"],
        "master_target_lufs": "-10 a -12 LUFS",
        "master_ceiling": "-1.0dB",
        "master_max_gr": "-3 a -4dB",
        "saturacion_master": "Decapitator Style T, SIEMPRE (el sonido de los 90s)",
        "imager_low": "MONO o casi mono (0-10% width)",
        "imager_high": "110-130% (sutil)",
        "cadena_completa": {
            "kick": "Pro-Q > Decapitator(T) > Limiter > Soft Clipper",
            "snare": "Pro-Q > Decapitator(A/N) > Limiter",
            "hihats": "Pro-Q > Decapitator(T) sutil > [Limiter]",
            "percs": "Pro-Q > [PrimalTap/EchoBoy]",
            "bajo": "Pro-Q > Decapitator(T) > Limiter > Stereo Enh > Soft Clipper",
            "samples": "RX > Pro-Q > Decapitator(T)/Radiator > [FilterFreak] > Limiter",
            "pads": "Pro-Q > [Crystallizer] > Reeverb 2",
            "voz": "RX > [Autotune sutil] > Pro-Q sub > Limiter x2 > Pro-Q add > Decapitator(A) > Pro-Q de-ess > Limiter",
            "bus_drums": "Pro-Q > Limiter(glue) > Decapitator(T) > Devil-Loc(paralelo)",
            "bus_melodias": "Pro-Q(sidechain voz) > Limiter > Radiator",
            "bus_voces": "Pro-Q > Limiter > Decapitator sutil",
            "master": "Pro-Q > Decapitator(T) > Ozone(DynEQ > VintageComp > Tape > Imager > Maximizer)",
        },
        "reference_albums": {
            "illmatic": {"artist": "Nas", "year": 1994, "lufs": "-12/-13", "character": "Seco, intimo, drums prominentes, voz clara"},
            "36_chambers": {"artist": "Wu-Tang", "year": 1993, "lufs": "-13/-15", "character": "Lo-fi, sucio, SP-1200, crudo, reverb en snare"},
            "moment_of_truth": {"artist": "Gang Starr", "year": 1998, "lufs": "-11/-13", "character": "Equilibrado, LA referencia boom bap perfecta"},
            "the_infamous": {"artist": "Mobb Deep", "year": 1995, "lufs": "-12/-14", "character": "Oscuro, duro, snare protagonista, minimalista"},
            "donuts": {"artist": "J Dilla", "year": 2006, "lufs": "-12/-14", "character": "Swing extremo, sample protagonista, lo-fi calido"},
            "ready_to_die": {"artist": "Biggie", "year": 1994, "lufs": "-11/-12", "character": "Mezcla mas comercial, graves potentes, voz al frente"},
            "midnight_marauders": {"artist": "ATCQ", "year": 1993, "lufs": "-12/-14", "character": "Jazzy, espacioso, bajo profundo, clean"},
        },
    },
    "trap": {
        "name": "Trap",
        "drums": "808 sintetico, hi-hats rapidos, snares electronicas",
        "bajo": "808 largo con distorsion y slide",
        "textura": "Limpia y moderna, pero con peso",
        "dinamica": "Mas comprimida, mas fuerte, mas 'in your face'",
        "referencia": ["Metro Boomin", "Southside", "Zaytoven", "Lex Luger"],
        "master_target_lufs": "-8 a -10 LUFS",
        "master_ceiling": "-0.5dB",
        "master_max_gr": "-4 a -6dB",
        "saturacion_master": "Decapitator OPCIONAL, Style A/N, mas sutil",
        "imager_low": "MONO (0-5% width) - CRITICO para 808",
        "imager_high": "120-140% (mas ancho que boom bap)",
        "cadena_completa": {
            "kick": "Pro-Q > Limiter > Soft Clipper",
            "snare": "Pro-Q > Limiter > [Radiator]",
            "hihats": "Pro-Q > [MicroShift] > Limiter",
            "percs": "Pro-Q > [Delay 3]",
            "808": "Pro-Q pre > Decapitator(A) growl > Pro-Q post > Limiter > Stereo Enh > Soft Clipper + SIDECHAIN",
            "melodias": "Pro-Q > MicroShift > EchoBoy > Limiter",
            "pads": "Pro-Q > [Tremolator] > Reeverb 2",
            "voz": "RX > Autotune(0-20ms) > Pro-Q sub > Limiter fuerte > Pro-Q add > Decapitator(E) > Pro-Q de-ess > [Little AlterBoy] > Limiter",
            "bus_drums": "Pro-Q > Limiter(glue) > Decapitator(A) sutil",
            "bus_melodias": "Pro-Q(sidechain voz) > Limiter",
            "bus_voces": "Pro-Q > Limiter > Decapitator sutil",
            "master": "Pro-Q > [Decapitator opcional] > Ozone(DynEQ > Dynamics > [Exciter] > Imager > Maximizer)",
        },
    },
    "phonk": {
        "name": "Phonk",
        "drums": "808 MUY distorsionado, cowbells, Memphis samples",
        "bajo": "808 extremadamente distorsionado, suena 'roto'",
        "textura": "Dark, distorsionada, VHS aesthetic",
        "dinamica": "Comprimida y distorsionada a proposito",
        "referencia": ["DJ Smokey", "Soudiere", "Phonk revival producers"],
        "master_target_lufs": "-8 a -10 LUFS",
        "master_ceiling": "-0.5dB",
        "saturacion_master": "Agresiva - Decapitator Drive alto o Devil-Loc",
        "tip": "En phonk las 'reglas' de mezcla se rompen a proposito. La distorsion ES el estetica.",
    },
}


# ============================================================================
# 5. PARALLEL PROCESSING - Compresion paralela y tecnicas NY
# ============================================================================

PARALLEL_PROCESSING: Dict[str, Dict] = {
    "ny_compression": {
        "name": "Compresion NY (New York) / Paralela",
        "description": (
            "Mezclar la senal original (seca) con una copia MUY comprimida. "
            "Resultado: punch + densidad sin perder dinamica."
        ),
        "method_1_devil_loc": {
            "name": "Metodo rapido: Devil-Loc Deluxe",
            "plugin": "Soundtoys Devil-Loc Deluxe",
            "settings": {
                "crush": "40-60%",
                "crunch": "50-70%",
                "mix": "15-25% (mezcla paralela integrada)",
                "darkness": "40-60%",
            },
            "tip": "La forma MAS rapida de conseguir punch en drums",
        },
        "method_2_bus": {
            "name": "Metodo clasico: Bus paralelo",
            "steps": [
                "1. Duplicar bus de drums (send a un bus nuevo)",
                "2. En la copia: Maximus con ratio 10:1, attack 1ms (APLASTAR)",
                "3. Bajar la copia a -10/-15dB",
                "4. Mezclar = punch + densidad sin perder dinamica",
            ],
            "tip": "El bus paralelo solo anade, nunca quita. Seguro de usar.",
        },
        "where_to_use": [
            "Bus de drums (el uso clasico)",
            "Voz principal (para presencia constante)",
            "Bajo (para que se escuche en altavoces pequenos)",
        ],
    },
    "parallel_saturation": {
        "name": "Saturacion paralela",
        "description": "Mezclar senal limpia con copia saturada. Mas armonicos sin destruir el original.",
        "method": [
            "1. Send a bus de saturacion",
            "2. Decapitator con Drive alto (6-8)",
            "3. Nivel del send: -10 a -6dB",
            "4. La senal original se mantiene limpia, la saturacion solo anade",
        ],
    },
    "parallel_reverb": {
        "name": "Reverb paralela (siempre en send)",
        "description": "La reverb SIEMPRE va en send, nunca en insert al 100%.",
        "tip": "EQ despues del reverb en el send: HP 200Hz, LP 6-8kHz (reverb sin graves ni agudos = NO ensucia)",
    },
}


# ============================================================================
# 6. BUS PROCESSING - Procesamiento de buses por grupo
# ============================================================================

BUS_PROCESSING: Dict[str, Dict] = {
    "bus_drums": {
        "name": "BUS DRUMS (Insert 100)",
        "receives": "kick, snare, hats, percs (via sends o routing)",
        "boom_bap": {
            "chain": [
                "Pro-Q 3: ajustes sutiles para balancear el grupo",
                "Fruity Limiter (glue): Ratio 2-3:1, Attack 20-30ms, Release 100-150ms, GR -1 a -3dB, Knee soft",
                "Decapitator: Style T, Drive 2-4, Mix 30-50% (TODO suena a SP-1200 por cinta)",
                "Devil-Loc Deluxe (paralelo): Crush 30-50%, Mix 15-25%, Darkness 40-60%",
            ],
            "result": "Los drums suenan ENORMES, como tocados en un gym de concreto",
        },
        "trap": {
            "chain": [
                "Pro-Q 3: ajustes sutiles",
                "Fruity Limiter (glue): Ratio 3-4:1, Attack 10-20ms, Release 60-100ms, GR -2 a -4dB",
                "Decapitator: Style A/N, Drive 2-3, Mix 20-35% (mas sutil en trap)",
            ],
        },
    },
    "bus_melodias": {
        "name": "BUS MELODIAS (Insert 101)",
        "receives": "samples, melodias, pads",
        "chain": [
            "Pro-Q 3: sidechain EQ desde la voz, corte dinamico 2-5kHz (cuando voz suena, melodias bajan)",
            "  Alternativa: corte estatico sutil en 2-4kHz, -2dB",
            "Fruity Limiter (glue): Ratio 2-3:1, GR -2 a -3dB",
            "Radiator o Decapitator Style T sutil, Mix 20-30% (calor global, boom bap)",
        ],
        "result": "Todo el bloque melodico suena unificado y calido",
    },
    "bus_voces": {
        "name": "BUS VOCES (Insert 102)",
        "receives": "voz principal, dobles, ad-libs",
        "chain": [
            "Pro-Q 3: ajustes finos tras escuchar todo junto",
            "Fruity Limiter (glue): Ratio 2:1, Attack 15ms, Release 80ms, GR -1 a -2dB (MUY SUAVE)",
            "Decapitator: Drive 2-3, Mix 20-30% (SUTIL, para cohesion del grupo vocal)",
        ],
        "result": "Todas las voces suenan del 'mismo mundo'",
    },
    "send_vox_reverb": {
        "name": "VOX REVERB (Insert 103, send 100% wet)",
        "boom_bap": {
            "plugin": "Fruity Reeverb 2",
            "type": "Room o Plate",
            "decay": "1.0-1.5s (CORTO para boom bap, la voz es seca)",
            "pre_delay": "20-30ms",
            "damping": "5-7kHz",
            "send_level": "15-25% (el reverb acompana, no domina)",
        },
        "trap": {
            "plugin": "Fruity Reeverb 2",
            "type": "Plate",
            "decay": "1.2-2.0s (mas largo que boom bap)",
            "pre_delay": "25-40ms",
            "damping": "5-8kHz",
            "send_level": "20-35%",
        },
    },
    "send_vox_delay": {
        "name": "VOX DELAY (Insert 104, send 100% wet)",
        "boom_bap": {
            "plugin": "Soundtoys EchoBoy",
            "style": "Studio Tape (calor analogico en las repeticiones)",
            "sync": "ON, 1/4 o 3/8",
            "feedback": "20-30%",
            "send_level": "15-25%",
            "post_eq": "Pro-Q despues: cortar <200Hz y >6kHz del delay",
        },
        "trap": {
            "plugin": "Soundtoys EchoBoy",
            "style": "Digital o Studio Tape",
            "sync": "ON, 1/4",
            "feedback": "25-35%",
            "send_level": "20-30%",
        },
    },
    "send_drum_reverb": {
        "name": "DRUM REVERB (Insert 105, send 100% wet)",
        "plugin": "Fruity Reeverb 2 o LuxeVerb",
        "type": "Room",
        "decay": "0.5-1.0s",
        "damping": "5kHz",
        "tip": "Solo para snare y percs. NUNCA enviar kick o bajo al reverb.",
    },
}


# ============================================================================
# 7. REFERENCING - A/B comparison workflow
# ============================================================================

REFERENCING: Dict[str, Dict] = {
    "workflow": {
        "name": "Workflow de referencia A/B",
        "steps": [
            "1. Importar track de referencia profesional en un canal del mixer",
            "2. Rutear directo al master (bypass todos los buses)",
            "3. Igualar volumen percibido (LUFS) con tu mezcla",
            "4. Comparar constantemente durante toda la mezcla",
            "5. NO copiar, pero COMPARAR: niveles, brillo, peso, espacio",
        ],
        "what_to_compare": [
            "Balance de graves vs agudos",
            "Nivel relativo de la voz vs instrumental",
            "Ancho estereo",
            "Cantidad de reverb/delay",
            "Nivel de compresion (dinamica)",
            "Brillo general",
        ],
    },
    "reference_tracks": {
        "boom_bap": {
            "name": "Referencias Boom Bap",
            "tracks": {
                "illmatic": {"artist": "Nas", "year": 1994, "lufs": "-12/-13", "why": "Seco, intimo, LA referencia"},
                "36_chambers": {"artist": "Wu-Tang", "year": 1993, "lufs": "-13/-15", "why": "Lo-fi crudo, SP-1200"},
                "moment_of_truth": {"artist": "Gang Starr", "year": 1998, "lufs": "-11/-13", "why": "Equilibrado PERFECTO"},
                "the_infamous": {"artist": "Mobb Deep", "year": 1995, "lufs": "-12/-14", "why": "Oscuro, duro, minimalista"},
                "donuts": {"artist": "J Dilla", "year": 2006, "lufs": "-12/-14", "why": "Lo-fi calido, swing extremo"},
                "ready_to_die": {"artist": "Biggie", "year": 1994, "lufs": "-11/-12", "why": "Comercial, graves potentes"},
                "midnight_marauders": {"artist": "ATCQ", "year": 1993, "lufs": "-12/-14", "why": "Jazzy, espacioso, clean"},
            },
        },
        "trap": {
            "name": "Referencias Trap",
            "tracks": {
                "metro_boomin": {"artist": "Metro Boomin", "why": "808 limpio y potente, mezcla moderna"},
                "southside": {"artist": "Southside / 808 Mafia", "why": "808 agresivo, hi-hats definidos"},
                "zaytoven": {"artist": "Zaytoven", "why": "Piano melodies, 808 clasico"},
            },
        },
    },
    "lufs_targets": {
        "name": "LUFS por plataforma",
        "platforms": {
            "spotify": "-14 LUFS (normaliza a esto)",
            "apple_music": "-16 LUFS",
            "youtube": "-14 LUFS",
            "soundcloud": "No normaliza (puedes ir mas alto)",
            "club_dj": "-6 a -8 LUFS (mucho mas alto)",
        },
        "recommendation": (
            "Masteriza a -10 a -12 LUFS para streaming. "
            "Las plataformas bajaran el volumen pero preservaras dinamica. "
            "Para DJs/club, haz un master separado mas alto."
        ),
    },
}


# ============================================================================
# 8. COMMON MISTAKES - Errores comunes y fixes
# ============================================================================

COMMON_MISTAKES: Dict[str, Dict] = {
    "demasiados_plugins": {
        "name": "Demasiados plugins",
        "mistake": "Poner plugins sin proposito claro",
        "fix": [
            "Si no mejora el sonido, QUITALO",
            "A/B constantemente (bypass)",
            "5 plugins bien puestos > 15 al azar",
        ],
    },
    "no_gain_staging": {
        "name": "No hacer gain staging",
        "mistake": "Empezar a mezclar sin calibrar niveles",
        "fix": [
            "SIEMPRE calibrar niveles ANTES de meter plugins",
            "Cada canal a -12dBFS antes de tocar nada",
            "Si la senal entra al plugin a +6dB, va a distorsionar",
        ],
    },
    "mezclar_alto": {
        "name": "Mezclar a volumen alto",
        "mistake": "Subir el volumen de los monitores para que 'suene mejor'",
        "fix": [
            "Mezcla a volumen BAJO-MEDIO",
            "Si suena bien bajito, suena increible alto",
            "Protege tus oidos, son tu herramienta mas valiosa",
        ],
    },
    "no_referencias": {
        "name": "No usar referencias",
        "mistake": "Mezclar en el vacio sin comparar con musica profesional",
        "fix": [
            "Pon una cancion PRO del genero en un canal del mixer",
            "Compara constantemente",
            "No copies, pero COMPARA niveles, brillo, peso, espacio",
        ],
    },
    "arreglar_en_master": {
        "name": "Arreglar en el master lo que se arregla en la mezcla",
        "mistake": "Intentar 'salvar' una mala mezcla con el mastering",
        "fix": [
            "Si el 808 tiene mud, arreglalo en el canal del 808",
            "Si la voz es oscura, arreglala en el canal de la voz",
            "El master solo REALZA, no arregla",
            "La mezcla tiene que sonar BIEN sin nada en el master",
        ],
    },
    "ignorar_mono": {
        "name": "Ignorar la mono-compatibilidad",
        "mistake": "No verificar como suena la mezcla en mono",
        "fix": [
            "Baja a mono periodicamente y escucha",
            "Si algo desaparece en mono, hay problemas de fase",
            "Los clubs, telefonos y muchos altavoces son mono o casi mono",
        ],
    },
    "over_compression_master": {
        "name": "Over-compresion en el master",
        "mistake": "El Maximizer reduciendo mas de -6dB",
        "fix": [
            "Si el Ozone Maximizer esta reduciendo mas de -6dB, es demasiado",
            "Baja los niveles en la mezcla y deja que el limiter trabaje menos",
            "Mas dinamica = mas impacto emocional",
        ],
    },
    "no_descansar": {
        "name": "No descansar los oidos",
        "mistake": "Sesiones de mezcla de muchas horas sin pausa",
        "fix": [
            "Cada 30-45 minutos, descansa 5-10 minutos",
            "'Fatiga auditiva' te hace tomar malas decisiones",
            "Si ya no sabes si suena bien, para y vuelve manana",
        ],
    },
}


# ============================================================================
# 9. MIXING CHECKLIST - Checklist completo antes de bouncing
# ============================================================================

MIXING_CHECKLIST: Dict[str, Dict] = {
    "pre_mix": {
        "name": "Antes de mezclar",
        "items": [
            "Gain staging completado (-18 a -12dBFS por canal)",
            "Canales organizados y nombrados en el mixer",
            "Buses configurados (drums, melodias, voces)",
            "Sends configurados (reverb, delay)",
            "Track de referencia importado",
            "Limpieza con RX completada (voces, samples)",
        ],
    },
    "during_mix": {
        "name": "Durante la mezcla",
        "items": [
            "EQ substractivo ANTES de aditivo en cada canal",
            "Compresion con attack lento (dejar transientes pasar)",
            "Sidechain kick-bajo configurado",
            "Bajos en MONO debajo de 200Hz",
            "A/B con referencia cada 10-15 minutos",
            "Bypass plugins individualmente para verificar mejora",
            "Escuchar a volumen bajo periodicamente",
        ],
    },
    "pre_master": {
        "name": "Antes de masterizar",
        "items": [
            "La mezcla suena bien SIN nada en el master",
            "El master recibe senal entre -6 y -3dBFS",
            "No hay clipping en ningun canal individual",
            "El balance de volumenes esta correcto",
            "La voz se entiende claramente",
        ],
    },
    "post_master": {
        "name": "Despues de masterizar",
        "items": [
            "HP filter en 25-30Hz en master",
            "LUFS entre -10 y -12 (streaming)",
            "Ceiling del limiter en -1.0dB (boom bap) o -0.5dB (trap)",
            "No clipping (verificar con dB Meter)",
            "Mono compatible (check con Ozone Imager)",
            "Bajos en mono (Ozone Imager band 1)",
            "Comparar con referencia profesional",
            "Exportar en WAV 24-bit, 44.1kHz (musica) o 48kHz (video)",
            "Escuchar en auriculares Y monitores",
            "Escuchar en volumen BAJO",
            "Escuchar en telefono / altavoz barato",
        ],
    },
}


# ============================================================================
# 10. SOUNDTOYS PLUGIN GUIDE - Que plugin para que
# ============================================================================

SOUNDTOYS_GUIDE: Dict[str, Dict] = {
    "decapitator": {
        "name": "Decapitator",
        "use": "EVERYWHERE - kick, snare, bajo, voz, samples, buses, master",
        "purpose": "Saturacion/distorsion con caracter analogico",
        "styles": {
            "T": "Tube - calido, musical. EL clasico para boom bap",
            "A": "Ampex - cinta vintage, para voz boom bap y 808 trap",
            "N": "Neve - consola, punch. Para buses y master",
            "E": "Ampex agresivo - para voz trap",
        },
    },
    "echoboy": {
        "name": "EchoBoy",
        "use": "Voz, melodias, sends de delay",
        "purpose": "Delay con saturacion y caracter",
        "best_styles": ["Studio Tape", "Space Echo", "Digital"],
    },
    "microshift": {
        "name": "MicroShift",
        "use": "Dobles, coros, hats, melodias",
        "purpose": "Abrir estereo sutil",
        "warning": "NO usar en bajo (mantener mono)",
    },
    "devil_loc": {
        "name": "Devil-Loc Deluxe",
        "use": "Bus drums (paralelo), 808 trap",
        "purpose": "Compresion destructiva / paralela",
    },
    "radiator": {
        "name": "Radiator",
        "use": "Samples boom bap, bus melodias",
        "purpose": "Calor de consola Altec",
    },
    "little_alterboy": {
        "name": "Little AlterBoy",
        "use": "Voz (efecto), ad-libs",
        "purpose": "Pitch/formant shift",
    },
    "filterfreak": {
        "name": "FilterFreak",
        "use": "Samples, melodias, transiciones",
        "purpose": "Filtro con caracter",
    },
    "crystallizer": {
        "name": "Crystallizer",
        "use": "Pads, ad-libs, texturas",
        "purpose": "Delay granular/pitch",
    },
    "tremolator": {
        "name": "Tremolator",
        "use": "Pads, melodias trap",
        "purpose": "Tremolo sincronizado",
    },
    "primaltap": {
        "name": "PrimalTap",
        "use": "Percs boom bap, efectos",
        "purpose": "Delay lo-fi vintage",
    },
    "panman": {
        "name": "PanMan",
        "use": "Hi-hats, percs, ad-libs",
        "purpose": "Auto-pan creativo",
    },
    "little_plate": {
        "name": "Little Plate",
        "use": "Send de reverb voces/snare",
        "purpose": "Plate reverb con calor",
    },
    "sie_q": {
        "name": "Sie-Q",
        "use": "Voces, buses",
        "purpose": "EQ pasivo con color",
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mixing_workflow(genre: str = "boom_bap") -> str:
    """Workflow completo de mezcla para un genero especifico.

    Args:
        genre: 'boom_bap', 'trap', o 'phonk'.

    Returns:
        Workflow formateado paso a paso.
    """
    lines = ["=== WORKFLOW DE MEZCLA ===\n"]

    # Genre info
    if genre in GENRE_DIFFERENCES:
        g = GENRE_DIFFERENCES[genre]
        lines.append(f"GENERO: {g['name']}")
        lines.append(f"  Drums: {g['drums']}")
        lines.append(f"  Bajo: {g['bajo']}")
        lines.append(f"  Textura: {g['textura']}")
        lines.append(f"  Dinamica: {g['dinamica']}")
        if "master_target_lufs" in g:
            lines.append(f"  Target LUFS: {g['master_target_lufs']}")
        lines.append("")

    # Mixing order
    for phase_key in sorted(MIXING_ORDER.keys(), key=lambda k: MIXING_ORDER[k]["order"]):
        phase = MIXING_ORDER[phase_key]
        lines.append(f"--- {phase['name']} ---")
        for task in phase["tasks"]:
            lines.append(f"  [ ] {task}")
        lines.append("")

    # Genre-specific chain
    if genre in GENRE_DIFFERENCES and "cadena_completa" in GENRE_DIFFERENCES[genre]:
        lines.append("--- CADENA COMPLETA POR ELEMENTO ---\n")
        for element, chain in GENRE_DIFFERENCES[genre]["cadena_completa"].items():
            lines.append(f"  {element.upper()}: {chain}")
        lines.append("")

    return "\n".join(lines)


def get_gain_staging_guide() -> str:
    """Guia completa de gain staging.

    Returns:
        Guia formateada.
    """
    lines = ["=== GUIA DE GAIN STAGING ===\n"]

    lines.append("FILOSOFIA:")
    lines.append(f"  {GAIN_STAGING['philosophy']['description']}")
    lines.append("")

    lines.append("POR QUE ES IMPORTANTE:")
    for reason in GAIN_STAGING["philosophy"]["why"]:
        lines.append(f"  - {reason}")
    lines.append("")

    lines.append("COMO HACERLO:")
    for step in GAIN_STAGING["workflow"]["steps"]:
        lines.append(f"  {step}")
    lines.append("")

    lines.append("NIVELES OBJETIVO:")
    for name, level in GAIN_STAGING["target_levels"]["levels"].items():
        lines.append(f"  {name}: {level}")
    lines.append("")

    lines.append("NIVELES RELATIVOS (kick = referencia 0dB):")
    for element, level in GAIN_STAGING["relative_levels"]["levels"].items():
        lines.append(f"  {element}: {level}")
    lines.append("")

    lines.append("LAYOUT DEL MIXER RECOMENDADO:")
    for insert, desc in MIXER_LAYOUT["inserts"]["layout"].items():
        lines.append(f"  Insert {insert}: {desc}")
    lines.append("  ---BUSES---")
    for insert, desc in MIXER_LAYOUT["buses"]["layout"].items():
        lines.append(f"  Insert {insert}: {desc}")

    return "\n".join(lines)


def get_bus_setup(genre: str = "boom_bap") -> str:
    """Guia de configuracion de buses para un genero.

    Args:
        genre: 'boom_bap' o 'trap'.

    Returns:
        Guia de buses formateada.
    """
    lines = ["=== CONFIGURACION DE BUSES ===\n"]

    for bus_key, bus in BUS_PROCESSING.items():
        lines.append(f"--- {bus['name']} ---")
        if "receives" in bus:
            lines.append(f"  Recibe: {bus['receives']}")

        if genre == "boom_bap" and "boom_bap" in bus:
            lines.append(f"\n  CADENA ({genre.upper()}):")
            for step in bus["boom_bap"]["chain"]:
                lines.append(f"    - {step}")
            if "result" in bus["boom_bap"]:
                lines.append(f"  RESULTADO: {bus['boom_bap']['result']}")
        elif genre == "trap" and "trap" in bus:
            lines.append(f"\n  CADENA ({genre.upper()}):")
            for step in bus["trap"]["chain"]:
                lines.append(f"    - {step}")
        elif "chain" in bus:
            lines.append("\n  CADENA:")
            for step in bus["chain"]:
                lines.append(f"    - {step}")
            if "result" in bus:
                lines.append(f"  RESULTADO: {bus['result']}")
        elif "plugin" in bus:
            lines.append(f"\n  Plugin: {bus['plugin']}")
            if genre in bus:
                for k, v in bus[genre].items():
                    lines.append(f"    {k}: {v}")
            elif "boom_bap" in bus:
                for k, v in bus["boom_bap"].items():
                    lines.append(f"    {k}: {v}")

        lines.append("")

    return "\n".join(lines)


def get_mixing_checklist() -> str:
    """Checklist completo de mezcla y mastering.

    Returns:
        Checklist formateado.
    """
    lines = ["=== CHECKLIST DE MEZCLA Y MASTERING ===\n"]

    for phase_key, phase in MIXING_CHECKLIST.items():
        lines.append(f"--- {phase['name']} ---")
        for item in phase["items"]:
            lines.append(f"  [ ] {item}")
        lines.append("")

    lines.append("--- ERRORES COMUNES A EVITAR ---\n")
    for err_key, err in COMMON_MISTAKES.items():
        lines.append(f"  {err['name']}:")
        lines.append(f"    Error: {err['mistake']}")
        lines.append(f"    Fix: {err['fix'][0]}")
        lines.append("")

    lines.append("--- LUFS POR PLATAFORMA ---\n")
    for platform, lufs in REFERENCING["lufs_targets"]["platforms"].items():
        lines.append(f"  {platform}: {lufs}")
    lines.append(f"\n  RECOMENDACION: {REFERENCING['lufs_targets']['recommendation']}")

    return "\n".join(lines)
