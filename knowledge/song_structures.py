"""Song structure templates and arrangement guides."""

from typing import List, Dict


STRUCTURES = {
    "boom_bap_standard": {
        "name": "Boom Bap Standard",
        "description": "Estructura clasica de boom bap. Intro(4) > Verso(16) > Hook(8) > Verso(16) > Hook(8) > Outro(4)",
        "total_bars": 56,
        "genre": "boom_bap",
        "sections": [
            {
                "name": "Intro",
                "bars": 4,
                "description": "Sample solo o drums filtrados. Puede ser un sample a capela o con LP filter. Establece el mood.",
                "tips": [
                    "Solo sample sin drums",
                    "O drums filtrados (LP bajo)",
                    "Vinyl crackle mas prominente",
                    "Puede incluir dialogo/skit",
                ],
            },
            {
                "name": "Verso 1",
                "bars": 16,
                "description": "Todos los elementos: drums completos + sample + bajo + vinyl crackle.",
                "tips": [
                    "Drums completos desde bar 1 del verso",
                    "Sample/melodia principal",
                    "Bajo siguiendo la armonia",
                    "Vinyl crackle sutil de fondo",
                    "Voz principal (si hay MC)",
                ],
            },
            {
                "name": "Hook",
                "bars": 8,
                "description": "Contraste con el verso. Anadir o quitar un elemento para diferenciarlo.",
                "tips": [
                    "Cambiar un elemento (quitar/anadir)",
                    "Sample diferente o filtrado distinto",
                    "Scratches o vocal hook",
                    "Puede ser solo instrumental",
                    "Open hat en vez de closed hat",
                ],
            },
            {
                "name": "Verso 2",
                "bars": 16,
                "description": "Mismo patron que verso 1 pero con variaciones sutiles.",
                "tips": [
                    "Misma base que verso 1",
                    "Variacion sutil: kick extra, fill de snare",
                    "Puede anadir un pad o textura nueva",
                    "Cambio de patron de bajo sutil",
                ],
            },
            {
                "name": "Hook",
                "bars": 8,
                "description": "Repeticion del hook.",
                "tips": [
                    "Mismo que primer hook",
                    "Puede tener un build sutil hacia el final",
                ],
            },
            {
                "name": "Outro",
                "bars": 4,
                "description": "Elementos se van quitando uno a uno. Fade out o corte seco.",
                "tips": [
                    "Quitar drums y dejar sample solo",
                    "Fade out gradual",
                    "O corte seco despues del ultimo hit",
                    "Vinyl crackle puede quedar sola al final",
                ],
            },
        ],
    },

    "boom_bap_extended": {
        "name": "Boom Bap Extendido (3 versos)",
        "description": "Version extendida con bridge. Intro(4) > V1(16) > Hook(8) > V2(16) > Hook(8) > Bridge(8) > V3(16) > Hook(8) > Outro(4)",
        "total_bars": 88,
        "genre": "boom_bap",
        "sections": [
            {"name": "Intro", "bars": 4, "description": "Sample solo o filtrado", "tips": []},
            {"name": "Verso 1", "bars": 16, "description": "Beat completo", "tips": []},
            {"name": "Hook", "bars": 8, "description": "Contraste", "tips": []},
            {"name": "Verso 2", "bars": 16, "description": "Variacion sutil", "tips": []},
            {"name": "Hook", "bars": 8, "description": "Repeticion", "tips": []},
            {
                "name": "Bridge",
                "bars": 8,
                "description": "Seccion contrastante. Puede ser solo sample, o un cambio de progresion.",
                "tips": [
                    "Quitar drums y dejar melodia",
                    "O cambiar completamente el sample",
                    "Filtro LP que sube gradualmente",
                    "Build hacia verso 3",
                ],
            },
            {"name": "Verso 3", "bars": 16, "description": "Ultimo verso, puede tener elementos extra", "tips": []},
            {"name": "Hook", "bars": 8, "description": "Hook final", "tips": []},
            {"name": "Outro", "bars": 4, "description": "Cierre", "tips": []},
        ],
    },

    "trap_standard": {
        "name": "Trap Standard",
        "description": "Estructura trap moderna. Intro(4) > Verso(8) > Hook(8) > Verso(8) > Hook(8) > Bridge(4) > Hook(8) > Outro(4)",
        "total_bars": 52,
        "genre": "trap",
        "sections": [
            {"name": "Intro", "bars": 4, "description": "808 intro o melodia sola", "tips": [
                "Melodia sola o con 808 sutil",
                "Build gradual de hi-hats",
            ]},
            {"name": "Verso 1", "bars": 8, "description": "Beat completo, versos mas cortos que boom bap", "tips": []},
            {"name": "Hook/Chorus", "bars": 8, "description": "Hook con melodia vocal y beat mas lleno", "tips": [
                "808 pattern puede cambiar",
                "Hi-hat rolls mas intensos",
                "Pads o synths adicionales",
            ]},
            {"name": "Verso 2", "bars": 8, "description": "Variacion", "tips": []},
            {"name": "Hook/Chorus", "bars": 8, "description": "Repeticion", "tips": []},
            {"name": "Bridge", "bars": 4, "description": "Drop o breakdown", "tips": [
                "Quitar 808 y dejar melodia",
                "O 808 solo con poca melodia",
                "Build de hi-hats hacia el drop",
            ]},
            {"name": "Hook/Chorus", "bars": 8, "description": "Hook final", "tips": []},
            {"name": "Outro", "bars": 4, "description": "Fade o corte", "tips": []},
        ],
    },

    "instrumental_loop": {
        "name": "Instrumental (Beat tape / Loop)",
        "description": "Para beat tapes o instrumentales sin voz. Intro(4) > A(8) > B(8) > A(8) > B(8) > Outro(4)",
        "total_bars": 40,
        "genre": "boom_bap",
        "sections": [
            {"name": "Intro", "bars": 4, "description": "Sample solo", "tips": []},
            {"name": "Seccion A", "bars": 8, "description": "Beat principal completo", "tips": []},
            {"name": "Seccion B", "bars": 8, "description": "Variacion: quitar o anadir elemento", "tips": [
                "Quitar sample, dejar drums + bajo",
                "O anadir segundo sample/melodia",
                "Cambiar patron de drums",
            ]},
            {"name": "Seccion A", "bars": 8, "description": "Vuelta al principal", "tips": []},
            {"name": "Seccion B", "bars": 8, "description": "Variacion", "tips": []},
            {"name": "Outro", "bars": 4, "description": "Cierre", "tips": []},
        ],
    },
}

# Fills and transitions
TRANSITIONS = {
    "drum_fill": {
        "description": "Fill de bateria en el ultimo compas antes del cambio de seccion",
        "techniques": [
            "Snare roll: semicorcheas ascendentes en velocity (70-80-90-100-110-120)",
            "Kick roll: kick en cada semicorchea del ultimo beat",
            "Hi-hat open: open hat en el ultimo beat",
            "Crash al inicio de la nueva seccion",
            "Quitar TODOS los drums en el ultimo beat (silencio dramatico)",
        ],
    },
    "filter_sweep": {
        "description": "Automatizar un filtro LP para transicionar",
        "techniques": [
            "LP filter baja gradualmente en los ultimos 2 compases",
            "LP filter sube en los primeros 2 compases de la nueva seccion",
            "HP filter sube para 'vaciar' el sonido antes del drop",
        ],
    },
    "vinyl_stop": {
        "description": "Efecto de tocadiscos parando",
        "techniques": [
            "Gross Beat: preset 'Tape Stop' o 'Half Speed' en el ultimo beat",
            "Automatizar pitch bend hacia abajo",
        ],
    },
    "reverse": {
        "description": "Reversa de un elemento",
        "techniques": [
            "Reversa del crash cymbal antes de la nueva seccion",
            "Reversa del sample como build-up",
            "Reversa de la snare en el ultimo beat",
        ],
    },
}

# Quick start reference
QUICK_START_10_STEPS = """
=== RESUMEN RAPIDO: BEAT BOOM BAP EN 10 PASOS ===

PASO 1 - TEMPO: 88-95 BPM. Sweet spot: 90 BPM.

PASO 2 - SAMPLE: Buscar soul/jazz/funk de los 60s-70s. Cargar en SliceX o Edison. Chop o loop. Detectar tonalidad.

PASO 3 - DRUMS: Kit de drums vinilicos/MPC/SP-1200. Patron basico: kick en 1,11,13 / snare en 5,13 / hat en corcheas. Swing: 58-62% en hats.

PASO 4 - BAJO: Serum 2 (sub sine) o FLEX (electric bass). Seguir la raiz de los acordes. Mono bajo 200Hz.

PASO 5 - VELOCITIES: Kick: 85-110, Snare: 95-127, Hats: 50-95. Nada a 127 constante.

PASO 6 - PROCESAMIENTO LO-FI: Fruity Squeeze (12-bit) en sample. Decapitator tape sat en drums y sample. Vinyl crackle a -15dB.

PASO 7 - ESTRUCTURA: Intro(4) > Verso(16) > Hook(8) > Verso(16) > Hook(8) > Outro(4)

PASO 8 - MEZCLA: Kick = referencia. Snare al mismo nivel. Sample -3/-6dB debajo. Hats -5/-8dB. Bus drums: Vintage Comp 2:1.

PASO 9 - EFECTOS: Reverb: LuxeVerb Room 1.0s en send. Delay: EchoBoy tape 1/4. Compresion paralela: Devil-Loc en send drums.

PASO 10 - MASTER: Ozone 12: Vintage Tape > Vintage Comp > Dynamic EQ > Imager (mono low) > Maximizer (ceiling -1.0dB). Target: -10 a -12 LUFS.
"""


def get_structure(genre: str = "boom_bap") -> str:
    """Get song structure template for a genre."""
    # Find matching structure
    for struct_id, struct in STRUCTURES.items():
        if struct["genre"] == genre and "standard" in struct_id:
            lines = [
                f"=== {struct['name']} ===",
                f"{struct['description']}",
                f"Total: {struct['total_bars']} compases\n",
            ]
            for section in struct["sections"]:
                lines.append(f"[{section['name']}] - {section['bars']} compases")
                lines.append(f"  {section['description']}")
                for tip in section.get("tips", []):
                    lines.append(f"    - {tip}")
                lines.append("")

            lines.append("\n=== TRANSICIONES ===")
            for trans_id, trans in TRANSITIONS.items():
                lines.append(f"\n{trans['description']}:")
                for tech in trans["techniques"]:
                    lines.append(f"  - {tech}")

            return "\n".join(lines)

    return f"No structure found for genre: {genre}"


def get_quick_start() -> str:
    """Get the 10-step quick start guide."""
    return QUICK_START_10_STEPS
