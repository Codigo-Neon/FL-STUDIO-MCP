"""Antares Auto-Tune Pro + Auto-Key knowledge para produccion vocal.

Guia completa de estilos de tuning, deteccion de tonalidad con Auto-Key,
workflow de grabacion a vocal tuneada, y errores comunes.
"""

from typing import Dict, List, Optional


# ============================================================================
# 1. ESTILOS DE AUTO-TUNE
# ============================================================================

AUTOTUNE_STYLES: Dict[str, Dict] = {
    "natural": {
        "nombre": "Natural / Transparente",
        "descripcion": "Correccion invisible. El oyente no nota que hay Auto-Tune. Mantiene la expresion natural del cantante con micro-variaciones de pitch intactas.",
        "retune_speed": 50,
        "retune_speed_unit": "ms",
        "humanize": 80,
        "flex_tune": 60,
        "throat_length": 0,
        "vibrato": {
            "rate": 0,
            "depth": 0,
            "nota": "Dejar el vibrato natural del cantante intacto",
        },
        "formant_correction": True,
        "genres": ["boom bap", "jazz rap", "R&B clasico", "neo-soul", "acoustic"],
        "reference_artists": ["J. Cole", "Anderson .Paak", "Chance the Rapper", "Mac Miller"],
        "notas": "Ideal cuando el cantante tiene buena afinacion base. Solo corrige las notas mas desviadas sin afectar el feeling.",
    },
    "moderate": {
        "nombre": "Moderado / Pulido",
        "descripcion": "Correccion audible pero no obvia. Vocal suena profesional y afinada sin efecto robotico. Estandar de la industria para R&B/pop moderno.",
        "retune_speed": 20,
        "retune_speed_unit": "ms",
        "humanize": 40,
        "flex_tune": 30,
        "throat_length": 0,
        "vibrato": {
            "rate": 5.0,
            "depth": 15,
            "nota": "Vibrato sutil artificial. Ajustar rate segun tempo del beat.",
        },
        "formant_correction": True,
        "genres": ["R&B moderno", "pop", "afrobeat", "reggaeton", "latin trap"],
        "reference_artists": ["Drake", "The Weeknd", "SZA", "Bryson Tiller", "Bad Bunny"],
        "notas": "Balance entre perfeccion y naturalidad. Retune 20ms permite algo de expresion pero corrige rapido. Humanize 40 mantiene ligeras imperfecciones intencionales.",
    },
    "hard_tune": {
        "nombre": "Hard Tune / Efecto T-Pain",
        "descripcion": "Efecto Auto-Tune obvio y audible. La voz salta entre notas sin transicion. El efecto ES el sonido buscado.",
        "retune_speed": 0,
        "retune_speed_unit": "ms",
        "humanize": 0,
        "flex_tune": 0,
        "throat_length": 0,
        "vibrato": {
            "rate": 0,
            "depth": 0,
            "nota": "SIN vibrato. El vibrato arruina el efecto hard tune porque suaviza las transiciones.",
        },
        "formant_correction": True,
        "genres": ["trap", "drill", "melodic trap", "mumble rap", "cloud rap"],
        "reference_artists": ["T-Pain", "Future", "Travis Scott", "Young Thug", "Lil Uzi Vert", "Gunna"],
        "notas": "Retune speed 0 = correccion instantanea. Cero humanize y flex-tune. La key DEBE estar perfecta o sonara horrible. SIEMPRE usar Auto-Key primero.",
    },
    "extreme": {
        "nombre": "Extremo / Experimental",
        "descripcion": "Auto-Tune llevado al limite con formant shifting. Voz alienigena, no humana. Efecto artistico extremo.",
        "retune_speed": 0,
        "retune_speed_unit": "ms",
        "humanize": 0,
        "flex_tune": 0,
        "throat_length": 2,
        "vibrato": {
            "rate": 0,
            "depth": 0,
            "nota": "Sin vibrato. El formant shift ya altera suficiente la voz.",
        },
        "formant_correction": False,
        "formant_shift_semitones": 2,
        "genres": ["hyperpop", "experimental", "PC music", "digicore", "glitchcore"],
        "reference_artists": ["100 gecs", "Bladee", "Charli XCX", "SOPHIE", "Yung Lean"],
        "notas": "Formant shift +2 semitonos sube la resonancia sin cambiar el pitch. Desactivar formant correction para efecto mas extremo. Combinar con chorus y distorsion.",
    },
}


# ============================================================================
# 2. DETECCION DE TONALIDAD CON AUTO-KEY
# ============================================================================

KEY_DETECTION: Dict[str, any] = {
    "descripcion": "Auto-Key analiza audio y detecta la tonalidad automaticamente. Envia la key directamente a Auto-Tune Pro.",
    "workflow": [
        "1. Abrir Auto-Key como plugin en un canal auxiliar o en el master",
        "2. Reproducir el beat completo (minimo 8 compases, idealmente el beat entero)",
        "3. Auto-Key muestra la tonalidad detectada (ej: C# Minor)",
        "4. Verificar que el confidence sea alto (>80%)",
        "5. Si el confidence es bajo, probar con la seccion mas melodica del beat",
        "6. Click en 'Send to Auto-Tune' para enviar la key automaticamente",
        "7. En Auto-Tune Pro, verificar que la escala recibida sea correcta",
    ],
    "tips": [
        "Analizar el BEAT solo (sin vocal) para mejor deteccion",
        "Si el beat tiene cambios de key, analizar cada seccion por separado",
        "Para beats con pocos elementos melodicos, usar la nota del 808/bass como referencia",
        "Auto-Key detecta Major/Minor. Para escalas modales (dorica, frigia), ajustar manualmente",
        "Si la deteccion falla, probar transponiendo el beat +/-1 semitono y re-analizar",
    ],
    "escalas_comunes": {
        "trap": ["C Minor", "D Minor", "F# Minor", "G Minor", "A Minor"],
        "boom_bap": ["Eb Major", "Bb Minor", "Ab Major", "C Minor", "F Minor"],
        "phonk": ["D Minor", "G Minor", "A Minor", "E Minor", "C Minor"],
        "rnb": ["Ab Major", "Db Major", "F Minor", "Bb Major", "Eb Minor"],
    },
}


# ============================================================================
# 3. WORKFLOW VOCAL COMPLETO
# ============================================================================

VOCAL_WORKFLOW: Dict[str, any] = {
    "titulo": "Workflow Completo: De Grabacion a Vocal Tuneada",
    "pasos": [
        {
            "paso": 1,
            "nombre": "Preparacion del beat",
            "acciones": [
                "Detectar tonalidad con Auto-Key (reproducir beat completo)",
                "Anotar BPM y key detectada",
                "Configurar metronomo al BPM del beat",
            ],
        },
        {
            "paso": 2,
            "nombre": "Grabacion",
            "acciones": [
                "Grabar en mono, 24-bit, sample rate del proyecto",
                "Gain staging: picos a -6dB, promedio -18dB",
                "Grabar 3-4 tomas completas minimo",
                "Hacer comping: elegir las mejores partes de cada toma",
            ],
        },
        {
            "paso": 3,
            "nombre": "Limpieza pre-tune (iZotope RX si disponible)",
            "acciones": [
                "Eliminar ruido de fondo (Voice De-noise)",
                "Quitar plosivas (De-plosive)",
                "Controlar respiraciones (Breath Control)",
                "De-ess si hay sibilancia excesiva",
            ],
        },
        {
            "paso": 4,
            "nombre": "Auto-Tune",
            "acciones": [
                "Insertar Auto-Tune Pro en el canal de vocal",
                "Configurar la key detectada por Auto-Key",
                "Seleccionar estilo segun genero (ver AUTOTUNE_STYLES)",
                "Ajustar retune speed - empezar conservador e ir bajando",
                "Activar formant correction (excepto estilo extreme)",
                "Reproducir y ajustar en tiempo real",
            ],
        },
        {
            "paso": 5,
            "nombre": "Post-procesamiento",
            "acciones": [
                "EQ: HPF a 80Hz, cortar 200-300Hz si hay boominess, boost sutil 3-5kHz",
                "Compresion: ratio 3:1, attack 10ms, release 50ms, 3-6dB GR",
                "De-esser post-compresion si es necesario",
                "Reverb/delay al gusto segun genero",
                "Saturacion sutil (Diablo tube, drive 10-15) para presencia",
            ],
        },
    ],
    "orden_de_plugins": [
        "1. Gain/Trim (staging)",
        "2. Auto-Tune Pro",
        "3. EQ substractivo",
        "4. Compresor",
        "5. De-esser",
        "6. EQ aditivo",
        "7. Saturacion (Diablo)",
        "8. Delay/Reverb (sends)",
    ],
}


# ============================================================================
# 4. ERRORES COMUNES
# ============================================================================

COMMON_MISTAKES: List[Dict[str, str]] = [
    {
        "error": "Key incorrecta",
        "sintoma": "Auto-Tune lleva las notas a tonos incorrectos, suena desafinado PEOR que sin Auto-Tune",
        "solucion": "Re-analizar con Auto-Key. Verificar manualmente con un piano. Probar relativa mayor/menor (C Minor = Eb Major).",
    },
    {
        "error": "Retune speed demasiado rapido para el estilo",
        "sintoma": "Vocal suena robotica cuando se busca un efecto natural. Pierde expresion y feeling.",
        "solucion": "Subir retune speed a 30-50ms. Aumentar humanize a 60-80. El objetivo natural es que NO se note el Auto-Tune.",
    },
    {
        "error": "Retune speed demasiado lento para hard tune",
        "sintoma": "El efecto Auto-Tune no se escucha. La vocal suena 'casi afinada' pero sin el salto caracteristico.",
        "solucion": "Retune speed a 0ms. Humanize a 0. Flex-tune a 0. Todo al minimo para maximo efecto.",
    },
    {
        "error": "Formant correction desactivada sin querer",
        "sintoma": "La vocal suena como ardilla (pitcheo agudo) o como monstruo (pitcheo grave) al corregir notas lejanas.",
        "solucion": "Activar formant correction. Solo desactivar intencionalmente para efecto extreme/experimental.",
    },
    {
        "error": "Grabar con Auto-Tune en tiempo real sin monitoreo",
        "sintoma": "El cantante no se escucha tuneado mientras graba, no puede ajustar su performance.",
        "solucion": "Configurar input monitoring con Auto-Tune en la cadena. Latencia <10ms es aceptable para monitoreo.",
    },
    {
        "error": "Notas de paso detectadas como errores",
        "sintoma": "Auto-Tune corrige notas de paso/melismas que deberian ser rapidas y libres.",
        "solucion": "Subir flex-tune (40-60) para ignorar notas que pasan rapido. O usar modo grafico para excluir zonas especificas.",
    },
    {
        "error": "Auto-Tune antes de limpiar la vocal",
        "sintoma": "Auto-Tune intenta afinar ruido, respiraciones, plosivas. Genera artefactos extranos.",
        "solucion": "SIEMPRE limpiar la vocal primero (RX 11 o manualmente). Auto-Tune va DESPUES de la limpieza.",
    },
    {
        "error": "Usar la misma configuracion para toda la cancion",
        "sintoma": "Versos suenan sobre-tuneados, coros suenan sub-tuneados. No hay dinamica.",
        "solucion": "Automatizar retune speed: mas lento en versos (20-40ms), mas rapido en coros (5-15ms). O usar dos instancias separadas.",
    },
]


# ============================================================================
# 5. FUNCIONES HELPER
# ============================================================================

def get_autotune_settings(style: str) -> str:
    """Devuelve la configuracion de Auto-Tune para un estilo dado.

    Args:
        style: Estilo de tuning (natural, moderate, hard_tune, extreme)

    Returns:
        Configuracion formateada en espanol.
    """
    key = style.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in AUTOTUNE_STYLES:
        disponibles = ", ".join(AUTOTUNE_STYLES.keys())
        return f"Estilo '{style}' no encontrado. Disponibles: {disponibles}"

    s = AUTOTUNE_STYLES[key]
    lines = [
        f"=== AUTO-TUNE: {s['nombre'].upper()} ===",
        f"Descripcion: {s['descripcion']}",
        "",
        "CONFIGURACION:",
        f"  Retune Speed: {s['retune_speed']} {s['retune_speed_unit']}",
        f"  Humanize: {s['humanize']}",
        f"  Flex-Tune: {s['flex_tune']}",
        f"  Throat Length: {s['throat_length']}",
        f"  Formant Correction: {'Si' if s['formant_correction'] else 'No'}",
        "",
        "VIBRATO:",
        f"  Rate: {s['vibrato']['rate']}",
        f"  Depth: {s['vibrato']['depth']}",
        f"  Nota: {s['vibrato']['nota']}",
        "",
        f"Generos: {', '.join(s['genres'])}",
        f"Artistas referencia: {', '.join(s['reference_artists'])}",
        "",
        f"Notas: {s['notas']}",
    ]

    if "formant_shift_semitones" in s:
        lines.insert(9, f"  Formant Shift: +{s['formant_shift_semitones']} semitonos")

    return "\n".join(lines)


def get_vocal_tuning_workflow() -> str:
    """Devuelve el workflow completo de grabacion a vocal tuneada.

    Returns:
        Workflow paso a paso formateado en espanol.
    """
    wf = VOCAL_WORKFLOW
    lines = [
        f"=== {wf['titulo'].upper()} ===",
        "",
    ]

    for paso in wf["pasos"]:
        lines.append(f"--- PASO {paso['paso']}: {paso['nombre'].upper()} ---")
        for accion in paso["acciones"]:
            lines.append(f"  - {accion}")
        lines.append("")

    lines.append("ORDEN DE PLUGINS EN EL CANAL:")
    for item in wf["orden_de_plugins"]:
        lines.append(f"  {item}")

    return "\n".join(lines)


def get_key_detection_guide() -> str:
    """Devuelve guia de deteccion de tonalidad con Auto-Key.

    Returns:
        Guia formateada en espanol.
    """
    kd = KEY_DETECTION
    lines = [
        "=== GUIA AUTO-KEY: DETECCION DE TONALIDAD ===",
        f"Descripcion: {kd['descripcion']}",
        "",
        "WORKFLOW:",
    ]

    for step in kd["workflow"]:
        lines.append(f"  {step}")

    lines.append("")
    lines.append("TIPS:")
    for tip in kd["tips"]:
        lines.append(f"  - {tip}")

    lines.append("")
    lines.append("ESCALAS COMUNES POR GENERO:")
    for genre, scales in kd["escalas_comunes"].items():
        lines.append(f"  {genre}: {', '.join(scales)}")

    return "\n".join(lines)
