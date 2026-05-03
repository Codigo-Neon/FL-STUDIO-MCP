"""Sampling knowledge for boom bap production in FL Studio.

Covers sampling sources, chopping techniques, pitch/time manipulation,
layering, sample processing, drum machine emulation, and legal tips.
Extracted from GUIA_BOOM_BAP_90s_COMPLETA.txt.
"""

from typing import Dict, List, Optional


# ============================================================================
# 1. SAMPLING SOURCES - Generos y artistas para samplear
# ============================================================================

SAMPLING_SOURCES: Dict[str, Dict] = {
    "vinyl": {
        "name": "Vinilo / Crate Digging",
        "description": "La fuente original y mas autentica del boom bap. Tiendas de discos, mercadillos, herencias.",
        "genres": {
            "soul_60s_70s": {
                "name": "Soul 60s-70s (EL genero #1 del boom bap)",
                "artists": [
                    "Curtis Mayfield", "Marvin Gaye", "Al Green", "Stevie Wonder",
                    "Isaac Hayes", "Barry White", "Bill Withers", "Donny Hathaway",
                    "The Isley Brothers", "The Temptations", "Smokey Robinson",
                    "Dionne Warwick", "Aretha Franklin", "Gladys Knight",
                    "Bobby Womack", "Sam Cooke", "Otis Redding",
                ],
            },
            "jazz": {
                "name": "Jazz (el segundo pilar)",
                "artists": [
                    "Miles Davis", "John Coltrane", "Herbie Hancock",
                    "Horace Silver", "Art Blakey", "Wes Montgomery",
                    "Ahmad Jamal", "Donald Byrd", "Lee Morgan",
                    "Thelonious Monk", "Bill Evans", "Oscar Peterson",
                    "Roy Ayers", "Lonnie Liston Smith", "Bob James",
                ],
            },
            "funk": {
                "name": "Funk",
                "artists": [
                    "James Brown", "Sly & The Family Stone", "Parliament/Funkadelic",
                    "Ohio Players", "The Meters", "Tower of Power",
                    "Kool & The Gang", "Earth Wind & Fire", "Mandrill",
                ],
            },
            "gospel": {
                "name": "Gospel",
                "artists": [
                    "Mahalia Jackson", "The Staple Singers",
                    "Edwin Hawkins Singers", "Andrae Crouch",
                ],
            },
            "bossa_latin": {
                "name": "Bossa Nova / Latin",
                "artists": [
                    "Antonio Carlos Jobim", "Marcos Valle",
                    "Jorge Ben", "Edu Lobo", "Gal Costa",
                ],
            },
            "soundtracks": {
                "name": "Soundtracks / Library Music",
                "artists": [
                    "Lalo Schifrin", "David Axelrod", "Quincy Jones",
                    "Isaac Hayes (Shaft)", "Curtis Mayfield (Superfly)",
                    "Ennio Morricone", "Piero Umiliani",
                ],
                "libraries": ["KPM", "Bruton", "De Wolfe"],
            },
        },
        "tips": [
            "Buscar en secciones de soul, jazz, funk de tiendas de segunda mano",
            "Los discos baratos y desconocidos suelen tener los mejores samples",
            "Escuchar intros, breaks instrumentales y outros - ahi estan los samples",
            "Buscar cambios de seccion donde los instrumentos suenan solos",
            "WhoSampled.com para investigar que discos samplearon los clasicos",
        ],
        "producer_preferences": {
            "dj_premier": "Soul 60s-70s, cortes CORTOS (1/4 a 1 compas)",
            "pete_rock": "Jazz, soul smooth, mucho Rhodes y saxo",
            "rza": "Soul oscuro, kung-fu movies, clasica, industrial",
            "j_dilla": "Todo. Soul, jazz, bossa nova, electronica, pop 80s",
            "9th_wonder": "Soul 70s limpio, Motown, R&B",
            "madlib": "Jazz raro, world music, prog rock, OSTs raros",
            "large_professor": "Funk, soul, jazz, breaks clasicos",
            "havoc": "Soul oscuro, piano clasico, strings",
            "hi_tek": "Soul 70s, gospel, funk",
            "buckwild": "Soul 60s-70s, jazz",
            "lord_finesse": "Funk, soul, jazz",
        },
    },
    "youtube": {
        "name": "YouTube / Internet",
        "description": "Fuente accesible para encontrar samples. Buscar grabaciones originales, no remasters.",
        "tips": [
            "Buscar 'full album' de artistas de soul/jazz/funk de los 60s-70s",
            "Canales como 'Dust-to-Digital', 'Numero Group', 'Soul/Jazz compilations'",
            "Preferir versiones ORIGINALES, no remasterizadas (menos compresion)",
            "Usar yt-dlp para descargar en maxima calidad disponible",
            "Buscar library music y soundtracks oscuros - menos sampleados",
        ],
    },
    "streaming": {
        "name": "Streaming (Spotify, Tidal, etc.)",
        "description": "Para descubrimiento y referencia. NO samplear directo por calidad y DRM.",
        "tips": [
            "Usar para DESCUBRIR musica, luego buscar el vinilo o comprar digital",
            "Las playlists de 'sample sources' en Spotify son buen punto de partida",
            "La calidad de streaming (OGG/AAC) NO es ideal para samplear",
            "Si samplas de streaming, la calidad se notara en la mezcla final",
            "Preferir siempre WAV/FLAC o vinilo real",
        ],
    },
    "drum_breaks": {
        "name": "Drum Breaks clasicos",
        "description": "Los breaks mas sampleados de la historia del hip-hop.",
        "breaks": {
            "amen_break": {
                "track": "The Winstons - 'Amen, Brother' (1969)",
                "bpm_original": 138,
                "bpm_boom_bap": "85-95 (ralentizado)",
                "character": "Ride abierto, snare con mucho crack, kick contundente",
                "usage": "EL break mas sampleado de la HISTORIA",
            },
            "funky_drummer": {
                "track": "James Brown - 'Funky Drummer' (1970)",
                "bpm_original": 100,
                "character": "Hi-hat sincopado, ghost notes en snare, kick con bounce",
                "used_by": ["Public Enemy", "Eric B & Rakim", "Gang Starr", "EPMD"],
            },
            "impeach_president": {
                "track": "The Honeydrippers - 'Impeach the President' (1973)",
                "bpm_original": 103,
                "character": "Break seco, directo, snare ENORME",
                "used_by": ["Nas (N.Y. State of Mind)", "LL Cool J", "EPMD"],
            },
            "think_about_it": {
                "track": "Lyn Collins - 'Think (About It)' (1972)",
                "bpm_original": 110,
                "character": "Hi-hats abiertos, groove bouncy",
                "used_by": ["Rob Base (It Takes Two)", "Ultramagnetic MCs"],
            },
            "apache": {
                "track": "Incredible Bongo Band - 'Apache' (1973)",
                "character": "Congas, bongos, snare con ring, kick deep",
                "note": "El himno nacional del hip-hop (Kool Herc lo usaba)",
                "used_by": ["Nas", "Beastie Boys", "Grandmaster Flash"],
            },
            "synthetic_substitution": {
                "track": "Melvin Bliss - 'Synthetic Substitution' (1973)",
                "character": "Snare seca perfecta con crack, kick con punch",
                "used_by": ["EPMD", "Black Moon", "Big Daddy Kane", "Mobb Deep"],
            },
            "skull_snaps": {
                "track": "Skull Snaps - 'It's a New Day' (1973)",
                "bpm_original": 97,
                "note": "Ya en rango boom bap. Biggie 'Juicy' samplea este break",
            },
            "when_levee_breaks": {
                "track": "Led Zeppelin - 'When the Levee Breaks' (1971)",
                "bpm_original": 70,
                "character": "John Bonham. EL kick mas gordo de la historia",
                "used_by": ["Beastie Boys", "Dr. Dre", "Eminem"],
            },
            "ashleys_roachclip": {
                "track": "The Soul Searchers - 'Ashley's Roachclip' (1974)",
                "used_by": ["Eric B & Rakim", "EPMD", "N.W.A."],
            },
            "hot_pants": {
                "track": "Bobby Byrd - 'Hot Pants' (1971)",
                "used_by": ["A Tribe Called Quest", "De La Soul", "Beastie Boys"],
            },
        },
    },
    "sample_packs": {
        "name": "Drum Kits / Sample Packs",
        "description": "Kits listos para usar, ideales para complementar samples de vinilo.",
        "recommended": [
            "Goldbaby SP-1200 y MPC60 Kits (de pago, los mejores)",
            "BeatButcha Boom Bap Kits",
            "!llmind Blap Kits",
            "Marco Polo Drum Kits",
            "MSX Audio kits",
            "Drum Broker (colecciones de samples de vinilo)",
            "Reddit r/drumkits (buscar 'boom bap' o 'vinyl drums')",
        ],
    },
}


# ============================================================================
# 2. CHOPPING TECHNIQUES - Metodos de chop en FL Studio
# ============================================================================

CHOPPING_TECHNIQUES: Dict[str, Dict] = {
    "edison": {
        "name": "Chopping con Edison",
        "description": "Editor de audio nativo de FL Studio. Bueno para chops manuales y precision.",
        "steps": [
            "1. Abrir Edison en un mixer track",
            "2. Grabar o importar el sample",
            "3. Seleccionar las secciones que quieres",
            "4. Right-click > 'Send to Piano Roll as audio clip'",
            "5. O 'Drag selection' al Channel Rack",
            "6. Reorganizar los chops en el Piano Roll / Playlist",
        ],
        "pros": ["Precision manual", "Integrado en FL Studio", "Bueno para limpieza previa"],
        "cons": ["Proceso mas lento", "Menos automatizacion"],
        "best_for": "Chops manuales precisos, limpieza de samples",
    },
    "slicex": {
        "name": "Chopping con SliceX (el mas potente)",
        "description": "Slicer avanzado nativo. Auto-detecta transientes, reasigna a notas MIDI.",
        "steps": [
            "1. Cargar sample en SliceX",
            "2. Auto-detect markers (transient detection)",
            "3. Ajustar markers manualmente si es necesario",
            "4. Cada slice = una nota en Piano Roll",
            "5. Reorganizar slices en orden diferente = FLIP",
        ],
        "pros": ["Auto-deteccion de transientes", "Cada slice mapeada a nota MIDI", "Mas control que Fruity Slicer"],
        "cons": ["Curva de aprendizaje", "Puede necesitar ajuste manual de markers"],
        "best_for": "Flips complejos, reorganizar samples completamente",
    },
    "fruity_slicer": {
        "name": "Fruity Slicer (version simple)",
        "description": "Version simplificada de SliceX. Rapido para chops basicos.",
        "steps": [
            "1. Cargar sample",
            "2. Auto-slice por beats/transients",
            "3. Cada slice mappeada a una nota",
            "4. Programar en Piano Roll",
        ],
        "pros": ["Muy rapido", "Simple de usar"],
        "cons": ["Menos control que SliceX", "Sin ajuste fino de markers"],
        "best_for": "Chops rapidos, prototipos, loops simples",
    },
    "directwave": {
        "name": "DirectWave Sampler",
        "description": "Sampler que permite tocar samples en diferentes notas/tonalidades.",
        "steps": [
            "1. Cargar un one-shot o chord",
            "2. Mapearlo al teclado",
            "3. Permite tocar el sample en diferentes notas",
            "4. Ideal para chord stabs y one-shots melodicos",
        ],
        "pros": ["Tocar samples cromaticamente", "Bueno para stabs y one-shots"],
        "cons": ["No ideal para loops largos", "Time-stretch basico"],
        "best_for": "Chord stabs, one-shots melodicos, tocar samples como instrumento",
    },
    "manual_playlist": {
        "name": "Chop Manual en Playlist",
        "description": "Cortar audio directamente en la Playlist de FL Studio.",
        "steps": [
            "1. Importar audio a la Playlist",
            "2. Usar la herramienta Slice (C) para cortar",
            "3. Mover y reorganizar los clips",
            "4. Ajustar fade-in/out en cada clip",
        ],
        "pros": ["Visual e intuitivo", "Facil de reorganizar"],
        "cons": ["Menos flexible para MIDI triggering", "No tan preciso como SliceX"],
        "best_for": "Loops largos, arreglos rapidos",
    },
}


# ============================================================================
# 3. PITCH TECHNIQUES - Manipulacion de pitch
# ============================================================================

PITCH_TECHNIQUES: Dict[str, Dict] = {
    "pitch_down": {
        "name": "Bajar Pitch (oscurecer)",
        "range": "2-5 semitonos abajo",
        "effect": "Sonido oscuro, lento, gordo. Clasico del SP-1200.",
        "why": (
            "El SP-1200 bajaba pitch para ahorrar memoria (menos sample rate = mas tiempo). "
            "Esa limitacion creo el sonido 'oscuro' y 'sucio' clasico del boom bap."
        ),
        "fl_studio": [
            "Channel Rack > Pitch knob (girar a la izquierda)",
            "Edison > Tools > Time/Pitch",
            "Piano Roll: seleccionar notas y transpose",
        ],
        "producers": ["RZA", "Havoc", "Madlib"],
        "tip": "Bajar 3-5 semitonos + bit-crush = sonido SP-1200 instantaneo",
    },
    "pitch_up": {
        "name": "Subir Pitch (chipmunk soul)",
        "range": "1-3 semitonos arriba",
        "effect": "Sonido bright, 'chipmunk soul'. Popularizado por Kanye West.",
        "fl_studio": [
            "Channel Rack > Pitch knob (girar a la derecha)",
            "Edison > Tools > Time/Pitch",
        ],
        "producers": ["Kanye West", "Just Blaze", "9th Wonder"],
        "tip": "Subir 2-3 semitonos convierte una voz masculina en algo casi femenino/infantil",
    },
    "key_matching": {
        "name": "Key Matching (ajustar tonalidad)",
        "description": "Ajustar el sample a la tonalidad del beat.",
        "fl_studio": [
            "Detectar tonalidad: Edison > Tools > Detect pitch regions",
            "O usar Pitcher/NewTone para analisis de pitch",
            "Ajustar con pitch knob en Channel Rack (por semitonos)",
            "Para ajustes finos: pitch knob en cents (+/- 100 cents = 1 semitono)",
        ],
        "tip": "Si el sample esta entre dos notas, usar fine-tuning en cents para afinar exacto",
    },
    "detuning_vintage": {
        "name": "Detuning Vintage (efecto tocadiscos)",
        "description": "Desafinar ligeramente para efecto de vinilo viejo o cinta degradada.",
        "fl_studio": [
            "Channel Rack: pitch +/- 5-15 cents",
            "Para efecto 'dos tocadiscos': duplicar, una capa +7 cents, otra -7 cents",
        ],
        "effect": "Suena a dos tocadiscos desincronizados. Lo-fi autentico.",
    },
}


# ============================================================================
# 4. TIME STRETCH - Modos de time-stretching en FL Studio
# ============================================================================

TIME_STRETCH: Dict[str, Dict] = {
    "e3_generic": {
        "name": "e3 generic (elastique)",
        "description": "Algoritmo de alta calidad. El mas transparente para cambios de tempo.",
        "when_to_use": "Cambios de tempo donde quieres sonido LIMPIO. Samples melodicos, voces.",
        "quality": "Alta",
        "artifacts": "Minimos",
    },
    "e3_mono": {
        "name": "e3 mono",
        "description": "Version mono del e3. Mejor para fuentes monofonicas.",
        "when_to_use": "Instrumentos solistas, voces individuales, bajo.",
        "quality": "Alta para mono",
        "artifacts": "Minimos en fuentes mono",
    },
    "slice_stretch": {
        "name": "Slice Stretch",
        "description": "Corta el audio en slices y las estira/comprime individualmente.",
        "when_to_use": "Loops ritmicos, drum breaks. Preserva transientes.",
        "quality": "Buena para ritmos",
        "artifacts": "Posibles gaps o overlaps en tempos muy diferentes",
    },
    "slice_map": {
        "name": "Slice/Map",
        "description": "Crea markers automaticos y mapea cada slice. Para chops ritmicos.",
        "when_to_use": "Drum breaks que quieres reorganizar. Cada slice se convierte en nota.",
        "quality": "Buena",
        "artifacts": "Depende de la deteccion de transientes",
    },
    "resample": {
        "name": "Resample",
        "description": "Cambia velocidad Y pitch juntos (como un tocadiscos).",
        "when_to_use": (
            "Cuando QUIERES el efecto vintage. Ralentizar = pitch baja. "
            "Acelerar = pitch sube. Sonido clasico de SP-1200/MPC."
        ),
        "quality": "N/A - es un efecto deseado",
        "artifacts": "El cambio de pitch ES el efecto buscado",
        "tip": "El modo mas 'autentico' para boom bap. Asi funcionaban los samplers clasicos.",
    },
    "gross_beat": {
        "name": "Gross Beat (efectos de cinta)",
        "description": "Plugin nativo para efectos de tape stop, speed up, half-speed, reverse.",
        "when_to_use": "Fills, transiciones, efectos creativos. NO para time-stretch permanente.",
        "presets_utiles": ["Tape stop", "Half-speed", "Reverse", "Scratch"],
        "tip": "Automatizar en momentos clave: fills, transiciones entre secciones.",
    },
}


# ============================================================================
# 5. LAYERING - Tecnicas de capas con samples
# ============================================================================

LAYERING: Dict[str, Dict] = {
    "chop_and_flip": {
        "name": "Chop and Flip (estilo DJ Premier / 9th Wonder)",
        "description": "Cortar sample en pedazos y reorganizar en orden completamente diferente.",
        "steps": [
            "1. Cortar el sample en pedazos de 1/4 a 1 compas",
            "2. Reorganizar en un orden completamente diferente",
            "3. Resultado: suena a algo nuevo, irreconocible",
        ],
        "producers": ["DJ Premier", "9th Wonder", "Large Professor"],
        "tip": "Cuanto mas cortos los chops, mas irreconocible el resultado. Premier usa chops de 1-2 beats.",
    },
    "loop": {
        "name": "Loop (estilo Pete Rock / J Dilla)",
        "description": "Encontrar 2-4 compases perfectos y loopearlos como base del beat.",
        "steps": [
            "1. Encontrar 2-4 compases perfectos del sample",
            "2. Loopearlos como base",
            "3. Anadir drums propios, bajo y elementos encima",
            "4. El sample ES la cancion, tu la complementas",
        ],
        "producers": ["Pete Rock", "J Dilla", "Madlib"],
        "tip": "Buscar secciones con pocos instrumentos - intros, breaks, bridges del disco original.",
    },
    "layer_instruments": {
        "name": "Layer con instrumentos (estilo Kanye / Just Blaze)",
        "description": "Sample como base con instrumentos propios encima.",
        "steps": [
            "1. Sample como base (loop o chops)",
            "2. Anadir instrumentos propios encima (bajo, keys, strings)",
            "3. Mezcla de sampled + original",
            "4. El sample da el 'alma', los instrumentos dan el control",
        ],
        "producers": ["Kanye West", "Just Blaze", "Hi-Tek"],
        "tip": "Asegurar que los instrumentos propios esten en la misma tonalidad que el sample.",
    },
    "multi_sample": {
        "name": "Multi-sample (multiples fuentes)",
        "description": "Combinar samples de diferentes discos/fuentes en un solo beat.",
        "steps": [
            "1. Sample melodico de un disco",
            "2. Drums de otro disco o kit",
            "3. Bajo de otra fuente o sintetizado",
            "4. Texturas/pads de otra fuente",
            "5. Mezclar todo en una misma estetica sonora",
        ],
        "producers": ["Pete Rock", "Madlib", "RZA"],
        "tip": "La clave es la cohesion: usar la misma cadena de procesamiento (saturacion, EQ) en todo.",
    },
    "call_response": {
        "name": "Call and Response",
        "description": "Alternar entre dos samples o entre sample y instrumento.",
        "steps": [
            "1. Sample A suena en compases 1-2",
            "2. Sample B (u otro instrumento) responde en compases 3-4",
            "3. Crea dialogo musical y variacion",
        ],
        "producers": ["DJ Premier", "Pete Rock"],
        "tip": "Funciona especialmente bien con horn stabs vs melodia principal.",
    },
    "texture_layer": {
        "name": "Textura / Atmosfera",
        "description": "Anadir capas sutiles que no se escuchan conscientemente pero dan profundidad.",
        "elements": [
            "Vinyl crackle: -20 a -12dB, sample de ruido de vinilo en loop",
            "Pad ambiental: -15 a -10dB, pad largo debajo del sample",
            "Room tone: reverb muy sutil en todo (send compartido)",
            "Cinta: saturacion de cinta sutil en el bus",
        ],
        "tip": "Estas capas son el 'pegamento' que hace que todo suene como un disco, no como un DAW.",
    },
}


# ============================================================================
# 6. SAMPLE PROCESSING - EQ, filtrado, simulacion vintage
# ============================================================================

SAMPLE_PROCESSING: Dict[str, Dict] = {
    "vinyl_cleanup": {
        "name": "Limpieza de sample de vinilo",
        "description": "Limpieza con iZotope RX ANTES de procesar. En boom bap, la suciedad es DESEADA.",
        "chain": [
            "iZotope RX De-click: quitar clicks y pops (SUTIL, no eliminar todo)",
            "iZotope RX De-hum: quitar 50/60Hz de hum electrico si lo hay",
            "iZotope RX De-noise: MUY SUTIL (-5 a -10dB). NO matar el ruido del vinilo",
        ],
        "important": "En boom bap, la 'suciedad' es DESEADA. Solo limpiar lo que MOLESTA, no lo que da CARACTER.",
    },
    "eq_sample": {
        "name": "EQ para samples",
        "plugin": "FabFilter Pro-Q 3",
        "settings": {
            "high_pass": "40-60Hz, 18dB/oct (quitar rumble del vinilo)",
            "cut_mud": "200-400Hz, -2 a -3dB (quitar mud del sample viejo)",
            "boost_detail": "1-3kHz, +2dB (sacar los detalles del sample)",
            "high_shelf": "8-12kHz, +2-3dB (abrir el sample, que respire)",
        },
        "tip": "Si el sample ya es brillante, NO anadir mas brillo en high shelf.",
    },
    "tape_saturation": {
        "name": "Saturacion de cinta (EL sonido del boom bap)",
        "options": {
            "decapitator": {
                "plugin": "Soundtoys Decapitator",
                "style": "T (Tape) - EL CLASICO para boom bap",
                "drive": "2-4 (calor, no destruccion)",
                "tone": "50%",
                "mix": "30-50%",
                "result": "Suena a SP-1200 pasado por cinta de 4 pistas",
            },
            "radiator": {
                "plugin": "Soundtoys Radiator",
                "input": "subir hasta que sature ligeramente",
                "bass": "al gusto",
                "treble": "sutil boost",
                "mix": "40-60%",
                "result": "Emulacion de consola Altec. Calido, musical, lo-fi.",
            },
        },
    },
    "filter_vintage": {
        "name": "Filtro vintage (LP para oscurecer)",
        "options": {
            "filterfreak": {
                "plugin": "Soundtoys FilterFreak",
                "type": "Low-pass para simular vinilo sucio",
                "resonance": "sutil (10-20%)",
                "tip": "Automatizar el cutoff para efecto DJ",
            },
            "fruity_filter": {
                "plugin": "Fruity Filter (nativo)",
                "use": "LP cutoff para oscurecer samples rapido",
                "tip": "Automatizar en el Playlist para transiciones",
            },
            "eq_lowpass": {
                "plugin": "Parametric EQ 2 / Pro-Q 3",
                "setting": "LP a 8-12kHz (sutil) o 5-8kHz (agresivo)",
                "tip": "Automatizar: baja en instrumental, sube cuando entra la voz",
            },
        },
    },
    "vinyl_simulation": {
        "name": "Simulacion de vinilo completa",
        "description": "Cadena para que TODO suene como sacado de un disco de 1994.",
        "chain_order": [
            {
                "step": 1,
                "name": "Bit-crushing",
                "plugin": "Fruity Squeeze",
                "settings": "Bits=12, Freq=26040Hz",
            },
            {
                "step": 2,
                "name": "Low-pass filter",
                "plugin": "Parametric EQ 2",
                "settings": "LP a 8-12kHz (sutil) o 5-8kHz (agresivo)",
            },
            {
                "step": 3,
                "name": "Saturacion de cinta",
                "plugin": "Decapitator",
                "settings": "Style T, Drive 2-4, Mix 30-50%",
            },
            {
                "step": 4,
                "name": "Chorus vintage",
                "plugin": "Vintage Chorus",
                "settings": "Rate 0.2-0.5Hz, Depth 20-40%, Mix 30-50%",
            },
            {
                "step": 5,
                "name": "Vinyl crackle",
                "plugin": "Sample de vinyl noise en loop",
                "settings": "Volumen -20 a -12dB. EQ: HP 200Hz, LP 8kHz",
            },
            {
                "step": 6,
                "name": "Detuning sutil",
                "plugin": "Channel Rack pitch",
                "settings": "+/- 5-15 cents. O duplicar: +7 cents y -7 cents",
            },
        ],
    },
    "compression_sample": {
        "name": "Compresion para samples",
        "plugin": "Fruity Limiter",
        "settings": {
            "ratio": "3:1",
            "attack": "15-25ms",
            "release": "100ms",
            "reduction": "-2 a -4dB (suave, no aplastar la dinamica del sample)",
        },
        "tip": "La dinamica original del sample es parte de su caracter. No sobre-comprimir.",
    },
}


# ============================================================================
# 7. DRUM MACHINES - Caracteristicas y emulacion en FL Studio
# ============================================================================

DRUM_MACHINES: Dict[str, Dict] = {
    "mpc_60": {
        "name": "AKAI MPC 60 (1988)",
        "description": "LA maquina que invento el boom bap moderno.",
        "specs": {
            "bits": 12,
            "sample_rate": "40kHz",
            "character": "Granulado y calido por la baja resolucion",
        },
        "sonic_character": [
            "Conversor de 12 bits a 40kHz",
            "Sonido 'granulado' y 'calido' por baja resolucion",
            "Algoritmo de swing unico que ningun DAW replica exactamente",
            "El sampling a 12 bits degrada la senal de forma musical",
            "Reduce rango dinamico, anade armonicos de cuantizacion, recorta agudos naturalmente",
        ],
        "producers": ["DJ Premier", "Pete Rock", "Large Professor", "Q-Tip"],
        "fl_emulation": [
            "El SWING es la clave: 58-62% en FL Studio",
            "Decapitator: Style 'T', Drive 2-3 (menos degradacion que SP-1200)",
            "Saturacion sutil de cinta",
        ],
    },
    "sp_1200": {
        "name": "E-MU SP-1200 (1987)",
        "description": "LA maquina del boom bap crudo de la costa este.",
        "specs": {
            "bits": 12,
            "sample_rate": "26.04kHz (MUY bajo)",
            "max_sample_time": "10 segundos total",
        },
        "sonic_character": [
            "12 bits, sample rate de 26.04kHz (MUY bajo)",
            "Solo 10 segundos de sample time total",
            "Limitacion forzaba creatividad: chops cortos, pitch down para ahorrar memoria",
            "Pitch down daba el sonido 'oscuro' y 'sucio' clasico",
            "Filtros analogicos internos que dan caracter unico",
        ],
        "producers": ["Pete Rock", "Large Professor", "RZA", "Havoc", "Marley Marl"],
        "fl_emulation": [
            "Fruity Squeeze: Bits=12, Freq=26040Hz",
            "Decapitator: Style 'T', Drive 3-5, Mix 40-60%",
            "Parametric EQ 2: LP suave en 12-14kHz (el SP no reproduce agudos)",
            "Saturn 2: modo Warm Tape sutil para mas caracter",
        ],
    },
    "mpc_3000": {
        "name": "AKAI MPC 3000 (1994)",
        "description": "Evolucion de la MPC 60. 16 bits, mas limpia pero con caracter MPC.",
        "specs": {
            "bits": 16,
            "character": "Mas limpia que MPC 60 pero mantiene caracter MPC",
        },
        "sonic_character": [
            "16 bits, mas limpia que MPC 60",
            "Mantiene el swing y feel MPC",
            "J Dilla la usaba como instrumento principal",
            "DJ Premier migro aqui desde la MPC 60",
        ],
        "producers": ["J Dilla", "DJ Premier"],
        "fl_emulation": [
            "Swing 58-65% (Dilla usaba 65-75%)",
            "Decapitator: Style 'T', Drive 1-2, Mix 20-30% (mas sutil)",
            "Menos bit-crushing que SP-1200 (es 16 bits)",
            "El feel viene del SWING y humanizacion, no tanto de la degradacion",
        ],
    },
    "asr_10": {
        "name": "ENSONIQ ASR-10 / EPS-16+",
        "description": "Samplers con filtros analogicos increibles. RZA los usaba para Wu-Tang.",
        "sonic_character": [
            "Filtros LP analogicos dan sonido 'oscuro' y 'turbio' unico",
            "RZA los usaba para Wu-Tang",
        ],
        "producers": ["RZA"],
        "fl_emulation": [
            "Volcano 3 o Fruity Filter: LP con resonancia sutil",
            "Cutoff bajo (3-6kHz) para el sonido turbio",
            "Decapitator: saturacion media",
        ],
    },
}


# ============================================================================
# 8. LEGAL TIPS - Aspectos legales del sampling
# ============================================================================

LEGAL_TIPS: Dict[str, Dict] = {
    "clearance_basics": {
        "name": "Conceptos basicos de clearance",
        "points": [
            "Toda grabacion tiene DOS copyrights: composicion (publishing) y grabacion (master)",
            "Para samplear legalmente necesitas permiso de AMBOS",
            "Los costos varian enormemente: desde gratis hasta cientos de miles de dolares",
            "Samples cortos NO estan exentos automaticamente (mito comun)",
        ],
    },
    "safe_options": {
        "name": "Opciones seguras para evitar problemas",
        "options": [
            "Usar samples libres de royalties (Splice, Tracklib, Loopcloud)",
            "Tracklib: plataforma legal para samplear musica real con licencia",
            "Samplear musica pre-1927 (dominio publico en la mayoria de paises)",
            "Recrear el sample tu mismo (re-play/interpolation) - solo necesitas clearance de composicion",
            "Usar samples tan manipulados que sean irreconocibles (riesgo: subjetivo)",
            "Producir con samples propios o de session musicians",
        ],
    },
    "risk_levels": {
        "name": "Niveles de riesgo",
        "levels": {
            "bajo": "Samples muy cortos (<1 segundo), muy manipulados, de artistas desconocidos",
            "medio": "Loops reconocibles de artistas poco conocidos, distribucion limitada",
            "alto": "Cualquier sample reconocible de artista conocido, distribucion comercial",
            "muy_alto": "Melodias iconicas, hooks vocales, artistas con sellos grandes",
        },
    },
    "practical_advice": {
        "name": "Consejo practico",
        "points": [
            "Para beats en SoundCloud/YouTube sin monetizacion: riesgo bajo pero existe",
            "Para distribucion comercial (Spotify, Apple Music): SIEMPRE clearear",
            "Mantener documentacion de todas las fuentes usadas",
            "Si el beat despega, tendras que clearear retroactivamente (mas caro)",
            "WhoSampled.com para investigar si alguien ya sampleo lo mismo",
        ],
    },
}


# ============================================================================
# 9. ICONIC SAMPLES - Samples mas famosos de la historia del boom bap
# ============================================================================

ICONIC_SAMPLES: Dict[str, Dict] = {
    "ny_state_of_mind": {
        "track": "N.Y. State of Mind (Nas)",
        "sample": "Mind Rain - Joe Chambers",
        "producer": "DJ Premier",
    },
    "troy": {
        "track": "T.R.O.Y. (Pete Rock & CL Smooth)",
        "sample": "Today - Tom Scott",
        "producer": "Pete Rock",
    },
    "cream": {
        "track": "C.R.E.A.M. (Wu-Tang)",
        "sample": "As Long As I've Got You - The Charmels",
        "producer": "RZA",
    },
    "shook_ones": {
        "track": "Shook Ones Pt. II (Mobb Deep)",
        "sample": "Kitty With the Bent Frame (Quincy Jones) + Jessica (Herbie Hancock)",
        "producer": "Havoc",
    },
    "juicy": {
        "track": "Juicy (Biggie)",
        "sample": "Juicy Fruit - Mtume",
        "producer": "Poke (Trackmasters)",
    },
    "mass_appeal": {
        "track": "Mass Appeal (Gang Starr)",
        "sample": "Lonesome Road - Grant Green",
        "producer": "DJ Premier",
    },
    "electric_relaxation": {
        "track": "Electric Relaxation (ATCQ)",
        "sample": "Mystic Brew - Ronnie Foster",
        "producer": "A Tribe Called Quest",
    },
    "hard_knock_life": {
        "track": "Hard Knock Life (Jay-Z)",
        "sample": "Annie (musical)",
        "producer": "The 45 King",
    },
    "i_used_to_love_her": {
        "track": "I Used to Love H.E.R. (Common)",
        "sample": "The Jungle Line - Joni Mitchell",
        "producer": "No I.D.",
    },
    "devil_new_dress": {
        "track": "Devil in a New Dress (Kanye West)",
        "sample": "Will You Still Love Me Tomorrow - Smokey Robinson",
        "producer": "Kanye West / Bink!",
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_chopping_guide(method: str = "") -> str:
    """Guia de chopping. Si no se especifica metodo, muestra todos.

    Args:
        method: Clave de CHOPPING_TECHNIQUES (edison, slicex, etc.) o vacio para todos.

    Returns:
        Guia formateada en texto.
    """
    lines = ["=== GUIA DE CHOPPING EN FL STUDIO ===\n"]

    if method and method in CHOPPING_TECHNIQUES:
        techniques = {method: CHOPPING_TECHNIQUES[method]}
    elif method:
        lines.append(f"Metodo '{method}' no encontrado. Mostrando todos.\n")
        techniques = CHOPPING_TECHNIQUES
    else:
        techniques = CHOPPING_TECHNIQUES

    for key, tech in techniques.items():
        lines.append(f"--- {tech['name']} ---")
        lines.append(f"  {tech['description']}")
        lines.append(f"  Mejor para: {tech['best_for']}")
        lines.append("")
        lines.append("  PASOS:")
        for step in tech["steps"]:
            lines.append(f"    {step}")
        lines.append("")
        if "pros" in tech:
            lines.append("  VENTAJAS: " + ", ".join(tech["pros"]))
        if "cons" in tech:
            lines.append("  DESVENTAJAS: " + ", ".join(tech["cons"]))
        lines.append("")

    lines.append("TECNICAS DE FLIP:")
    lines.append("  - Chop and Flip (Premier/9th): cortar y reorganizar, irreconocible")
    lines.append("  - Loop (Pete Rock/Dilla): encontrar 2-4 compases perfectos y loopear")
    lines.append("  - Layer (Kanye/Just Blaze): sample + instrumentos propios encima")
    lines.append("  - Multi-sample: combinar samples de diferentes fuentes")

    return "\n".join(lines)


def get_sampling_workflow(source_type: str = "vinyl") -> str:
    """Workflow completo de sampling segun el tipo de fuente.

    Args:
        source_type: Tipo de fuente (vinyl, youtube, streaming, drum_breaks).

    Returns:
        Workflow formateado paso a paso.
    """
    lines = ["=== WORKFLOW DE SAMPLING ===\n"]

    if source_type in SAMPLING_SOURCES:
        src = SAMPLING_SOURCES[source_type]
        lines.append(f"Fuente: {src['name']}")
        lines.append(f"  {src['description']}")
        lines.append("")
        if "tips" in src:
            lines.append("TIPS:")
            for tip in src["tips"]:
                lines.append(f"  - {tip}")
            lines.append("")

    lines.append("--- WORKFLOW PASO A PASO ---\n")
    lines.append("PASO 1 - ENCONTRAR EL SAMPLE:")
    lines.append("  Buscar soul/jazz/funk de los 60s-70s")
    lines.append("  Escuchar intros, breaks instrumentales, outros")
    lines.append("  Buscar secciones con pocos instrumentos")
    lines.append("")
    lines.append("PASO 2 - IMPORTAR Y LIMPIAR:")
    lines.append("  Importar a Edison o directamente al Channel Rack")
    lines.append("  Si viene de vinilo: limpieza con iZotope RX (sutil)")
    lines.append("  Detectar tonalidad con Edison o Pitcher")
    lines.append("")
    lines.append("PASO 3 - CHOPPING:")
    lines.append("  SliceX: para flips complejos (auto-detect transientes)")
    lines.append("  Edison: para chops manuales precisos")
    lines.append("  Fruity Slicer: para chops rapidos y simples")
    lines.append("")
    lines.append("PASO 4 - PITCH/TEMPO:")
    lines.append("  Ajustar pitch si necesitas cambiar tonalidad")
    lines.append("  Ajustar tempo con time-stretch o resample")
    lines.append("  Modo 'resample' = sonido clasico (pitch cambia con tempo)")
    lines.append("")
    lines.append("PASO 5 - PROCESAMIENTO:")
    lines.append("  EQ: HP 40-60Hz, cortar mud 200-400Hz, boost presencia 1-3kHz")
    lines.append("  Saturacion: Decapitator Style T, Drive 2-4, Mix 30-50%")
    lines.append("  Compresion: Fruity Limiter, Ratio 3:1, suave")
    lines.append("  Lo-fi (opcional): Fruity Squeeze 12-bit + LP filter")
    lines.append("")
    lines.append("PASO 6 - ARREGLO:")
    lines.append("  Organizar chops en Piano Roll o Playlist")
    lines.append("  Anadir drums, bajo, y elementos encima")
    lines.append("  Anadir vinyl crackle (-15 a -12dB)")

    if source_type == "drum_breaks" and "breaks" in SAMPLING_SOURCES.get("drum_breaks", {}):
        lines.append("\n--- BREAKS CLASICOS ---\n")
        for key, brk in SAMPLING_SOURCES["drum_breaks"]["breaks"].items():
            lines.append(f"  {brk['track']}")
            if "bpm_original" in brk:
                lines.append(f"    BPM original: {brk['bpm_original']}")
            if "character" in brk:
                lines.append(f"    Caracter: {brk['character']}")
            lines.append("")

    return "\n".join(lines)


def get_drum_machine_emulation(machine: str = "") -> str:
    """Guia para emular drum machines clasicas en FL Studio.

    Args:
        machine: Clave de DRUM_MACHINES (mpc_60, sp_1200, mpc_3000, asr_10) o vacio para todos.

    Returns:
        Guia de emulacion formateada.
    """
    lines = ["=== EMULACION DE DRUM MACHINES EN FL STUDIO ===\n"]

    if machine and machine in DRUM_MACHINES:
        machines = {machine: DRUM_MACHINES[machine]}
    elif machine:
        lines.append(f"Maquina '{machine}' no encontrada.")
        lines.append(f"Disponibles: {', '.join(DRUM_MACHINES.keys())}\n")
        machines = DRUM_MACHINES
    else:
        machines = DRUM_MACHINES

    for key, m in machines.items():
        lines.append(f"--- {m['name']} ---")
        lines.append(f"  {m['description']}")
        lines.append("")
        if "specs" in m:
            lines.append("  SPECS:")
            for spec_k, spec_v in m["specs"].items():
                lines.append(f"    {spec_k}: {spec_v}")
            lines.append("")
        lines.append("  CARACTER SONICO:")
        for char in m["sonic_character"]:
            lines.append(f"    - {char}")
        lines.append("")
        lines.append(f"  PRODUCTORES: {', '.join(m['producers'])}")
        lines.append("")
        lines.append("  COMO EMULAR EN FL STUDIO:")
        for step in m["fl_emulation"]:
            lines.append(f"    - {step}")
        lines.append("")

    return "\n".join(lines)


def get_sample_processing_chain(style: str = "standard") -> str:
    """Cadena de procesamiento para samples segun el estilo.

    Args:
        style: 'standard', 'lofi', 'clean', o 'aggressive'.

    Returns:
        Cadena de procesamiento formateada.
    """
    lines = ["=== CADENA DE PROCESAMIENTO DE SAMPLES ===\n"]

    if style == "lofi":
        lines.append("ESTILO: Lo-Fi (SP-1200 / RZA / Madlib)\n")
        lines.append("CADENA:")
        lines.append("  1. iZotope RX: limpieza MUY sutil (preservar suciedad)")
        lines.append("  2. Fruity Squeeze: Bits=12, Freq=26040Hz")
        lines.append("  3. Parametric EQ 2: LP a 8-10kHz (agresivo)")
        lines.append("  4. Decapitator: Style T, Drive 4-6, Mix 50-70%")
        lines.append("  5. Pitch DOWN 2-5 semitonos (sonido oscuro)")
        lines.append("  6. Fruity Limiter: Ratio 3:1, leve")
        lines.append("  7. Vinyl crackle encima: -15 a -10dB")

    elif style == "clean":
        lines.append("ESTILO: Limpio (9th Wonder / Hi-Tek)\n")
        lines.append("CADENA:")
        lines.append("  1. iZotope RX: limpieza mas agresiva")
        lines.append("  2. Pro-Q 3: HP 60Hz, cortar mud 300Hz -2dB")
        lines.append("  3. Pro-Q 3: boost 2-4kHz +2dB (presencia)")
        lines.append("  4. Fruity Limiter: Ratio 2:1, suave")
        lines.append("  5. Sin bit-crushing ni saturacion fuerte")
        lines.append("  6. Stereo Enhancer sutil si es mono")

    elif style == "aggressive":
        lines.append("ESTILO: Agresivo (RZA / Wu-Tang)\n")
        lines.append("CADENA:")
        lines.append("  1. Fruity Squeeze: Bits=10-12, Freq=20000-26040Hz")
        lines.append("  2. Decapitator: Style T, Drive 5-7, Mix 60-80%")
        lines.append("  3. Parametric EQ 2: LP a 5-8kHz (MUY oscuro)")
        lines.append("  4. Fruity Filter: LP cutoff bajo, automatizar")
        lines.append("  5. Fruity Limiter: Ratio 4:1, compresion agresiva")
        lines.append("  6. Devil-Loc Deluxe: Crush 30-40%, Mix 20-30%")
        lines.append("  7. Reverb larga en send (LuxeVerb 1.5-2.5s)")

    else:  # standard
        lines.append("ESTILO: Standard Boom Bap (Premier / Pete Rock)\n")
        lines.append("CADENA:")
        lines.append("  1. iZotope RX: De-click sutil, De-hum si necesario")
        lines.append("     IMPORTANTE: NO eliminar todo el ruido. La suciedad es caracter.")
        lines.append("  2. Pro-Q 3: HP 40-60Hz, cortar 200-400Hz -2dB")
        lines.append("     Boost 1-3kHz +2dB, High shelf 8-12kHz +2dB")
        lines.append("  3. Decapitator: Style T, Drive 2-4, Mix 30-50%")
        lines.append("     (suena a SP-1200 pasado por cinta)")
        lines.append("  4. FilterFreak (opcional): LP para efecto DJ")
        lines.append("  5. Fruity Limiter: Ratio 3:1, Attack 15-25ms")
        lines.append("     Release 100ms, Reduccion -2 a -4dB")
        lines.append("  6. Stereo Enhancer: si es mono, abrir 20-30%")

    lines.append("\n--- TIPS GENERALES ---")
    lines.append("  - SIEMPRE A/B (bypass) para verificar que el procesamiento mejora")
    lines.append("  - La dinamica original del sample es parte de su caracter")
    lines.append("  - Menos es mas: 4 plugins bien puestos > 10 al azar")
    lines.append("  - El sample debe sonar como 'sacado de un disco', no como 'procesado en DAW'")
    lines.append("  - Recurso: WhoSampled.com para investigar samples clasicos")

    return "\n".join(lines)
