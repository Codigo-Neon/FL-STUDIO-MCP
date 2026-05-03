"""iZotope RX 11 knowledge - módulos de reparación y limpieza de audio.

Guía completa de módulos RX 11 instalados, workflows de limpieza por tipo
de fuente, presets de intensidad, y funciones helper.
"""

from typing import Dict, List, Optional
from math import inf


# ============================================================================
# 1. MÓDULOS RX 11
# ============================================================================

RX_MODULES: Dict[str, Dict] = {
    "breath_control": {
        "name": "Breath Control",
        "description": "Controla respiraciones en vocales. Puede reducir volumen, acortar o eliminar. Más natural que cortar manualmente.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección de respiraciones"},
            "target_gain": {"range": (-inf, 0), "default": -12, "desc": "Reducción en dB aplicada a respiraciones detectadas"},
            "mode": {"options": ["gain", "remove"], "default": "gain", "desc": "Reducir volumen o eliminar completamente"},
        },
        "when_to_use": "Vocales con respiraciones audibles entre frases. Especialmente útil en grabaciones con micrófono cercano (proximity effect).",
        "tips": [
            "Modo 'gain' a -12dB suena más natural que 'remove'",
            "No eliminar TODAS las respiraciones - suena antinatural",
            "Sensitivity alta puede confundir consonantes suaves con respiraciones",
            "Revisar cada detección manualmente en grabaciones importantes",
        ],
    },
    "de_click": {
        "name": "De-click",
        "description": "Elimina clicks y pops de vinilos, grabaciones digitales con glitches, y artefactos de edición.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección de clicks"},
            "frequency_skew": {"range": (-100, 100), "default": 0, "desc": "Enfoque frecuencial. Negativo=graves, positivo=agudos"},
            "click_widening": {"range": (0, 100), "default": 30, "desc": "Amplitud de la zona reparada alrededor del click"},
            "algorithm": {"options": ["single_band", "multi_band", "periodic"], "default": "multi_band", "desc": "Algoritmo. Periodic para clicks rítmicos (vinilo)"},
        },
        "when_to_use": "Samples de vinilo con pops/clicks. Audio digital con glitches. Ediciones con clicks en los cortes.",
        "tips": [
            "Para vinilo: usar algoritmo 'periodic' con sensitivity 40-60",
            "Sensitivity >70 puede afectar transientes de drums",
            "Procesar ANTES de cualquier compresión/saturación",
            "Hacer preview antes de aplicar - verificar que no come transientes",
        ],
    },
    "de_clip": {
        "name": "De-clip",
        "description": "Repara audio clippeado/distorsionado por sobrecarga. Reconstruye los picos cortados.",
        "key_parameters": {
            "threshold": {"range": (-6, 0), "default": -0.1, "desc": "Umbral de detección de clipping en dB"},
            "quality": {"options": ["low", "medium", "high"], "default": "high", "desc": "Calidad de reconstrucción. High = más preciso pero más lento"},
            "makeup_gain": {"range": (-12, 0), "default": -3, "desc": "Reducción de ganancia post-reparación en dB"},
        },
        "when_to_use": "Audio grabado demasiado caliente. Samples de YouTube/SoundCloud con clipping. Grabaciones de campo con picos.",
        "tips": [
            "Funciona mejor con clipping leve (1-3dB over). Clipping severo no se repara bien",
            "Siempre reducir ganancia después con makeup_gain",
            "No usar en distorsión INTENCIONAL (808, guitarras distorsionadas)",
            "Calidad 'high' vale la pena para vocales, 'medium' para samples",
        ],
    },
    "de_crackle": {
        "name": "De-crackle",
        "description": "Elimina crackle continuo de vinilos, cintas viejas, y grabaciones degradadas. Diferente a De-click que busca eventos individuales.",
        "key_parameters": {
            "strength": {"range": (0, 100), "default": 50, "desc": "Intensidad de reducción del crackle"},
            "quality": {"options": ["low", "medium", "high"], "default": "medium", "desc": "Calidad de procesamiento"},
        },
        "when_to_use": "Samples de vinilo con ruido de superficie continuo. Grabaciones de cassette. Audio viejo digitalizado.",
        "tips": [
            "Complementa a De-click: primero De-click (pops grandes), luego De-crackle (ruido fino)",
            "Strength >60 puede afectar los agudos del audio original",
            "Para boom bap, a veces QUIERES algo de crackle - no eliminar todo",
            "Usar con precaución en hi-hats y cymbals",
        ],
    },
    "de_ess": {
        "name": "De-ess",
        "description": "Reduce sibilancia excesiva (sonidos 'S', 'SH', 'CH') en vocales sin afectar el resto de la señal.",
        "key_parameters": {
            "threshold": {"range": (-40, 0), "default": -20, "desc": "Umbral de detección de sibilancia en dB"},
            "frequency": {"range": (2000, 12000), "default": 6000, "desc": "Frecuencia central de la sibilancia en Hz"},
            "cutoff_slope": {"options": [6, 12, 24], "default": 12, "desc": "Pendiente del filtro en dB/octava"},
            "output_mode": {"options": ["classic", "spectral"], "default": "spectral", "desc": "Modo. Spectral es más transparente"},
        },
        "when_to_use": "Vocales con 'S' sibilantes y agresivas. Después de comprimir/saturar vocales (amplifica sibilancia). Micrófonos con pico de presencia.",
        "tips": [
            "Frecuencia típica: 5-8kHz para voces masculinas, 7-10kHz para femeninas",
            "Modo spectral suena más natural que classic",
            "No sobre-procesar: vocal sin sibilancia suena como con ceceo (lisping)",
            "Colocar DESPUÉS de compresión y EQ de presencia",
        ],
    },
    "de_hum": {
        "name": "De-hum",
        "description": "Elimina zumbido eléctrico (50Hz/60Hz y armónicos). Causado por líneas eléctricas, transformadores, ground loops.",
        "key_parameters": {
            "base_frequency": {"options": [50, 60], "default": 50, "desc": "Frecuencia base del hum. 50Hz Europa/Latam, 60Hz USA/Japón"},
            "num_harmonics": {"range": (1, 10), "default": 5, "desc": "Número de armónicos a eliminar"},
            "strength": {"range": (0, 100), "default": 70, "desc": "Intensidad de reducción"},
            "filter_q": {"range": (1, 100), "default": 10, "desc": "Estrechez del filtro. Alto=preciso, bajo=amplio"},
            "adaptive": {"options": [True, False], "default": True, "desc": "Adaptarse a variaciones de frecuencia del hum"},
        },
        "when_to_use": "Grabaciones con zumbido eléctrico constante. Audio cerca de transformadores/cables. Ground loop en la interfaz de audio.",
        "tips": [
            "En Latinoamérica generalmente es 50Hz (verificar con espectrograma)",
            "5 armónicos (50, 100, 150, 200, 250Hz) cubre la mayoría de casos",
            "Filter Q alto (>20) para afectar mínimamente el audio útil",
            "Si el hum varía, activar modo adaptive",
        ],
    },
    "de_plosive": {
        "name": "De-plosive",
        "description": "Reduce plosivas (sonidos 'P', 'B') que causan picos graves en el micrófono. Más preciso que un HPF.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección de plosivas"},
            "strength": {"range": (0, 100), "default": 60, "desc": "Cantidad de reducción aplicada"},
            "frequency_limit": {"range": (50, 500), "default": 200, "desc": "Frecuencia máxima afectada en Hz"},
        },
        "when_to_use": "Vocales grabadas sin pop filter. Plosivas que pasaron el pop filter. Siempre mejor que HPF porque solo actúa en las plosivas.",
        "tips": [
            "Usar ANTES de Auto-Tune (las plosivas confunden al pitch detector)",
            "Más transparente que un high-pass filter estático",
            "Sensitivity 50-60 es un buen punto de partida",
            "No confundir con De-click - plosivas son eventos de baja frecuencia",
        ],
    },
    "de_reverb": {
        "name": "De-reverb",
        "description": "Reduce reverberación de la sala en grabaciones. Acerca la vocal. NO elimina reverb añadido intencionalmente.",
        "key_parameters": {
            "reduction": {"range": (0, 100), "default": 40, "desc": "Cantidad de reducción de reverb"},
            "ambience_preservation": {"range": (0, 100), "default": 30, "desc": "Preservar algo de ambiente natural"},
            "tail_length": {"range": (0.1, 5.0), "default": 0.5, "desc": "Longitud estimada de la cola de reverb en segundos"},
            "artifact_smoothing": {"range": (0, 100), "default": 50, "desc": "Suavizar artefactos del procesamiento"},
        },
        "when_to_use": "Vocales grabadas en habitación no tratada. Samples con demasiado reverb de sala. Field recordings donde quieres aislar la fuente.",
        "tips": [
            "Reducción >60% genera artefactos audibles (sonido 'underwater')",
            "Mantener ambience_preservation 20-40% para que no suene antinatural",
            "Funciona mejor en vocales que en instrumentos complejos",
            "Procesar ANTES de añadir tu propio reverb con Pluto",
        ],
    },
    "dialogue_isolate": {
        "name": "Dialogue Isolate",
        "description": "Aísla voces/diálogo de fondos complejos. Usa machine learning para separar voz humana del resto.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección de voz"},
            "strength": {"range": (0, 100), "default": 70, "desc": "Intensidad del aislamiento"},
            "output_mode": {"options": ["dialogue", "noise"], "default": "dialogue", "desc": "Salida: voz aislada o ruido de fondo solo"},
        },
        "when_to_use": "Extraer vocales de samples/canciones. Aislar diálogo de películas para sampling. Separar acapellas de mezclas.",
        "tips": [
            "Para stem separation, mejor usar herramientas dedicadas (LALAL.ai, etc)",
            "Modo 'noise' útil para obtener el instrumental sin voz",
            "Calidad depende de cuánto se diferencia la voz del fondo",
            "Combinar con Spectral De-noise después para limpiar residuos",
        ],
    },
    "guitar_de_noise": {
        "name": "Guitar De-noise",
        "description": "Elimina ruido de amplificador, single coil hum, y buzz de guitarra eléctrica. Optimizado para guitarras.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección del ruido"},
            "strength": {"range": (0, 100), "default": 60, "desc": "Cantidad de reducción del ruido"},
        },
        "when_to_use": "Samples de guitarra con ruido de amplificador. Grabaciones de guitarra eléctrica single coil. Samples de funk/soul con buzz.",
        "tips": [
            "Diseñado específicamente para el perfil de ruido de guitarras",
            "Más efectivo que Spectral De-noise para ruido de ampli",
            "No usar en guitarras acústicas - usar Voice De-noise para eso",
            "Ideal para limpiar samples de funk antes de choppear",
        ],
    },
    "mouth_de_click": {
        "name": "Mouth De-click",
        "description": "Elimina clicks de boca, chasquidos de labios y saliva en vocales. Más preciso que De-click general para estos artefactos.",
        "key_parameters": {
            "sensitivity": {"range": (0, 100), "default": 50, "desc": "Sensibilidad de detección de clicks de boca"},
            "frequency_skew": {"range": (-100, 100), "default": 0, "desc": "Enfoque frecuencial de detección"},
            "click_widening": {"range": (0, 100), "default": 20, "desc": "Amplitud de zona reparada"},
        },
        "when_to_use": "Vocales con micrófonos de condensador (captan todo). Grabaciones cercanas al micrófono. Narraciones y voces habladas.",
        "tips": [
            "Procesar DESPUÉS de Breath Control y De-plosive",
            "Sensitivity 40-60 es el rango ideal para la mayoría de vocales",
            "Demasiada sensitivity puede afectar consonantes como 'T' y 'K'",
            "Más común en grabaciones con poca hidratación del cantante",
        ],
    },
    "repair_assistant": {
        "name": "Repair Assistant",
        "description": "Asistente automático que analiza el audio y sugiere una cadena de procesamiento. Buen punto de partida para principiantes.",
        "key_parameters": {
            "mode": {"options": ["music", "dialogue", "other"], "default": "music", "desc": "Tipo de audio a reparar"},
            "intensity": {"options": ["light", "moderate", "aggressive"], "default": "moderate", "desc": "Intensidad del procesamiento sugerido"},
        },
        "when_to_use": "Cuando no sabes por dónde empezar. Para análisis rápido del audio. Como segunda opinión sobre qué módulos usar.",
        "tips": [
            "Usar como punto de partida, luego ajustar manualmente",
            "El modo 'music' es mejor para samples que 'dialogue'",
            "No confiar ciegamente - siempre escuchar el resultado",
            "Útil para identificar problemas que no detectaste a oído",
        ],
    },
    "spectral_de_noise": {
        "name": "Spectral De-noise",
        "description": "Reducción de ruido avanzada basada en perfil espectral. Aprende el 'fingerprint' del ruido y lo elimina selectivamente.",
        "key_parameters": {
            "threshold": {"range": (-40, 0), "default": -20, "desc": "Umbral de reducción en dB"},
            "reduction": {"range": (0, 40), "default": 15, "desc": "Cantidad de reducción en dB"},
            "algorithm": {"options": ["adaptive", "manual"], "default": "adaptive", "desc": "Modo. Manual requiere noise print, adaptive es automático"},
            "smoothing_bands": {"range": (1, 6), "default": 3, "desc": "Suavizado frecuencial. Alto=menos artefactos pero menos preciso"},
            "smoothing_time": {"range": (1, 6), "default": 3, "desc": "Suavizado temporal. Alto=transiciones más suaves"},
        },
        "when_to_use": "Ruido de fondo constante (AC, ventiladores, calle). Samples de YouTube/SoundCloud con ruido. Cualquier audio con noise floor alto.",
        "tips": [
            "Modo manual: seleccionar zona de SOLO ruido para aprender el perfil",
            "Reducción >20dB genera artefactos 'musicales' (tinkling)",
            "Siempre usar smoothing 3+ para evitar artefactos",
            "Para samples, modo adaptive funciona bien sin noise print",
        ],
    },
    "voice_de_noise": {
        "name": "Voice De-noise",
        "description": "Reducción de ruido optimizada para voz humana. Usa ML para distinguir voz de ruido. Más fácil que Spectral De-noise.",
        "key_parameters": {
            "reduction": {"range": (0, 100), "default": 50, "desc": "Cantidad de reducción del ruido"},
            "quality": {"options": ["low", "medium", "high"], "default": "high", "desc": "Calidad del procesamiento ML"},
            "adaptive": {"options": [True, False], "default": True, "desc": "Adaptarse a cambios en el ruido"},
        },
        "when_to_use": "Vocales con ruido de fondo. Podcasts y narraciones. Cualquier grabación de voz en entorno no tratado.",
        "tips": [
            "Más fácil de usar que Spectral De-noise para vocales",
            "No necesita noise print - detecta voz automáticamente",
            "Quality 'high' usa más CPU pero suena significativamente mejor",
            "Para samples de vinilo con voz, usar Spectral De-noise en su lugar",
        ],
    },
}


# ============================================================================
# 2. WORKFLOWS DE LIMPIEZA POR FUENTE
# ============================================================================

CLEANUP_WORKFLOWS: Dict[str, Dict] = {
    "vinyl_sample": {
        "nombre": "Sample de Vinilo",
        "descripcion": "Limpieza de samples extraídos de discos de vinilo. Preservar carácter vintage eliminando artefactos no deseados.",
        "orden": ["de_click", "de_crackle", "spectral_de_noise"],
        "pasos": [
            {
                "modulo": "de_click",
                "config": {
                    "sensitivity": 45,
                    "frequency_skew": 0,
                    "click_widening": 25,
                    "algorithm": "periodic",
                },
                "notas": "Periodic mode para clicks rítmicos del vinilo. Sensitivity moderada para no comer transientes de drums.",
            },
            {
                "modulo": "de_crackle",
                "config": {
                    "strength": 40,
                    "quality": "high",
                },
                "notas": "Strength conservador (40). Para boom bap, algo de crackle es deseable. Subir a 60 solo si el crackle es excesivo.",
            },
            {
                "modulo": "spectral_de_noise",
                "config": {
                    "threshold": -25,
                    "reduction": 10,
                    "algorithm": "adaptive",
                    "smoothing_bands": 4,
                    "smoothing_time": 3,
                },
                "notas": "Reducción sutil (10dB). Solo para el hiss/ruido de superficie que queda después de De-click y De-crackle.",
            },
        ],
        "notas_generales": "Para boom bap, no limpiar demasiado. El carácter del vinilo es parte del sonido. Objetivo: eliminar pops/clicks molestos manteniendo la textura.",
    },
    "youtube_sample": {
        "nombre": "Sample de YouTube / Internet",
        "descripcion": "Limpieza de audio extraído de YouTube, SoundCloud u otras fuentes online. Generalmente comprimido y con artefactos de codec.",
        "orden": ["spectral_de_noise", "de_clip"],
        "pasos": [
            {
                "modulo": "spectral_de_noise",
                "config": {
                    "threshold": -18,
                    "reduction": 12,
                    "algorithm": "adaptive",
                    "smoothing_bands": 3,
                    "smoothing_time": 3,
                },
                "notas": "Reducción moderada para eliminar artefactos de compresión y ruido de fondo. Adaptive funciona bien sin noise print.",
            },
            {
                "modulo": "de_clip",
                "config": {
                    "threshold": -0.3,
                    "quality": "high",
                    "makeup_gain": -2,
                },
                "notas": "Muchos videos de YouTube tienen clipping por normalización agresiva. Threshold -0.3dB para captar clipping sutil.",
            },
        ],
        "notas_generales": "Audio de YouTube ya está degradado por compresión. No esperar milagros. Mejor buscar fuentes de mayor calidad si es posible.",
    },
    "vocal_recording": {
        "nombre": "Grabación Vocal",
        "descripcion": "Limpieza completa de vocal grabada. Desde raw recording hasta vocal lista para mezclar.",
        "orden": ["breath_control", "de_plosive", "mouth_de_click", "de_ess", "voice_de_noise"],
        "pasos": [
            {
                "modulo": "breath_control",
                "config": {
                    "sensitivity": 50,
                    "target_gain": -15,
                    "mode": "gain",
                },
                "notas": "Reducir respiraciones a -15dB, no eliminar. Modo gain suena más natural. En rap, las respiraciones son parte de la energía.",
            },
            {
                "modulo": "de_plosive",
                "config": {
                    "sensitivity": 55,
                    "strength": 60,
                    "frequency_limit": 200,
                },
                "notas": "Antes de Auto-Tune. Las plosivas confunden al pitch detector. Frequency limit 200Hz cubre las plosivas sin afectar el cuerpo de la voz.",
            },
            {
                "modulo": "mouth_de_click",
                "config": {
                    "sensitivity": 45,
                    "frequency_skew": 10,
                    "click_widening": 20,
                },
                "notas": "Sensitivity conservadora. Los clicks de boca están en frecuencias medias-altas, frequency_skew ligeramente positivo.",
            },
            {
                "modulo": "de_ess",
                "config": {
                    "threshold": -22,
                    "frequency": 6500,
                    "cutoff_slope": 12,
                    "output_mode": "spectral",
                },
                "notas": "6500Hz buen punto de partida para voces masculinas. Subir a 8000Hz para voces femeninas. Modo spectral más transparente.",
            },
            {
                "modulo": "voice_de_noise",
                "config": {
                    "reduction": 40,
                    "quality": "high",
                    "adaptive": True,
                },
                "notas": "Último paso. Reducción moderada (40) para no degradar la vocal. Quality high siempre para vocales principales.",
            },
        ],
        "notas_generales": "Este workflow va ANTES de Auto-Tune y antes de cualquier otro procesamiento (EQ, compresión). La vocal limpia entra mejor a toda la cadena.",
    },
    "field_recording": {
        "nombre": "Grabación de Campo",
        "descripcion": "Limpieza de grabaciones hechas en exterior o lugares ruidosos. Entrevistas, ambientes, foley.",
        "orden": ["de_hum", "spectral_de_noise", "de_reverb"],
        "pasos": [
            {
                "modulo": "de_hum",
                "config": {
                    "base_frequency": 50,
                    "num_harmonics": 5,
                    "strength": 80,
                    "filter_q": 15,
                    "adaptive": True,
                },
                "notas": "50Hz para Latinoamérica. 5 armónicos cubre hasta 250Hz. Q 15 para ser preciso. Adaptive por si hay variaciones.",
            },
            {
                "modulo": "spectral_de_noise",
                "config": {
                    "threshold": -15,
                    "reduction": 18,
                    "algorithm": "adaptive",
                    "smoothing_bands": 4,
                    "smoothing_time": 4,
                },
                "notas": "Reducción más agresiva que para samples musicales. Smoothing alto para evitar artefactos. Adaptive se adapta al ruido cambiante del exterior.",
            },
            {
                "modulo": "de_reverb",
                "config": {
                    "reduction": 50,
                    "ambience_preservation": 20,
                    "tail_length": 0.8,
                    "artifact_smoothing": 60,
                },
                "notas": "Reducir reverb de espacios grandes. Ambience preservation bajo porque en campo quieres aislar la fuente. Smoothing alto por artefactos.",
            },
        ],
        "notas_generales": "Field recordings suelen tener múltiples problemas. Procesar en orden: primero frecuencias específicas (hum), luego ruido broadband, luego reverb.",
    },
    "stem_isolation": {
        "nombre": "Aislamiento de Stems / Vocales",
        "descripcion": "Extraer vocales o instrumentos de mezclas completas usando Dialogue Isolate.",
        "orden": ["dialogue_isolate"],
        "pasos": [
            {
                "modulo": "dialogue_isolate",
                "config": {
                    "sensitivity": 55,
                    "strength": 75,
                    "output_mode": "dialogue",
                },
                "notas": "Strength 75 para buen aislamiento. Para obtener instrumental, cambiar output_mode a 'noise'. Combinar con Spectral De-noise después si quedan residuos.",
            },
        ],
        "notas_generales": "Para mejor calidad de stem separation, considerar LALAL.ai o Demucs. RX es bueno para aislamiento rápido y casos simples.",
    },
}


# ============================================================================
# 3. PRESETS DE INTENSIDAD
# ============================================================================

INTENSITY_PRESETS: Dict[str, Dict] = {
    "gentle": {
        "nombre": "Suave / Conservador",
        "descripcion": "Procesamiento mínimo. Preserva el audio original al máximo. Para cuando el audio está casi limpio o quieres mantener carácter.",
        "configs": {
            "breath_control": {"sensitivity": 35, "target_gain": -8, "mode": "gain"},
            "de_click": {"sensitivity": 30, "click_widening": 15, "algorithm": "single_band"},
            "de_clip": {"threshold": -0.1, "quality": "high", "makeup_gain": -1},
            "de_crackle": {"strength": 25, "quality": "high"},
            "de_ess": {"threshold": -25, "frequency": 6000, "cutoff_slope": 6, "output_mode": "spectral"},
            "de_hum": {"strength": 50, "num_harmonics": 3, "filter_q": 20},
            "de_plosive": {"sensitivity": 40, "strength": 40, "frequency_limit": 150},
            "de_reverb": {"reduction": 20, "ambience_preservation": 50, "artifact_smoothing": 60},
            "dialogue_isolate": {"sensitivity": 40, "strength": 50},
            "mouth_de_click": {"sensitivity": 35, "click_widening": 15},
            "spectral_de_noise": {"threshold": -25, "reduction": 8, "smoothing_bands": 4, "smoothing_time": 4},
            "voice_de_noise": {"reduction": 30, "quality": "high"},
        },
    },
    "medium": {
        "nombre": "Medio / Estándar",
        "descripcion": "Balance entre limpieza y preservación. Punto de partida recomendado para la mayoría de situaciones.",
        "configs": {
            "breath_control": {"sensitivity": 50, "target_gain": -15, "mode": "gain"},
            "de_click": {"sensitivity": 50, "click_widening": 30, "algorithm": "multi_band"},
            "de_clip": {"threshold": -0.3, "quality": "high", "makeup_gain": -3},
            "de_crackle": {"strength": 50, "quality": "medium"},
            "de_ess": {"threshold": -20, "frequency": 6500, "cutoff_slope": 12, "output_mode": "spectral"},
            "de_hum": {"strength": 70, "num_harmonics": 5, "filter_q": 12},
            "de_plosive": {"sensitivity": 55, "strength": 60, "frequency_limit": 200},
            "de_reverb": {"reduction": 40, "ambience_preservation": 30, "artifact_smoothing": 50},
            "dialogue_isolate": {"sensitivity": 50, "strength": 70},
            "mouth_de_click": {"sensitivity": 50, "click_widening": 20},
            "spectral_de_noise": {"threshold": -20, "reduction": 15, "smoothing_bands": 3, "smoothing_time": 3},
            "voice_de_noise": {"reduction": 50, "quality": "high"},
        },
    },
    "aggressive": {
        "nombre": "Agresivo / Máxima Limpieza",
        "descripcion": "Limpieza profunda. Puede generar artefactos pero elimina casi todo el ruido. Para audio muy problemático.",
        "configs": {
            "breath_control": {"sensitivity": 70, "target_gain": -30, "mode": "remove"},
            "de_click": {"sensitivity": 70, "click_widening": 50, "algorithm": "multi_band"},
            "de_clip": {"threshold": -0.5, "quality": "high", "makeup_gain": -5},
            "de_crackle": {"strength": 75, "quality": "high"},
            "de_ess": {"threshold": -15, "frequency": 7000, "cutoff_slope": 24, "output_mode": "spectral"},
            "de_hum": {"strength": 90, "num_harmonics": 8, "filter_q": 8},
            "de_plosive": {"sensitivity": 70, "strength": 80, "frequency_limit": 250},
            "de_reverb": {"reduction": 65, "ambience_preservation": 10, "artifact_smoothing": 40},
            "dialogue_isolate": {"sensitivity": 65, "strength": 90},
            "mouth_de_click": {"sensitivity": 65, "click_widening": 35},
            "spectral_de_noise": {"threshold": -15, "reduction": 25, "smoothing_bands": 2, "smoothing_time": 2},
            "voice_de_noise": {"reduction": 75, "quality": "high"},
        },
    },
}


# ============================================================================
# 4. FUNCIONES HELPER
# ============================================================================

def get_cleanup_chain(source_type: str) -> str:
    """Devuelve el workflow de limpieza recomendado para un tipo de fuente.

    Args:
        source_type: Tipo de fuente (vinyl_sample, youtube_sample, vocal_recording,
                     field_recording, stem_isolation)

    Returns:
        Workflow formateado en español con módulos, configuraciones y notas.
    """
    key = source_type.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in CLEANUP_WORKFLOWS:
        disponibles = ", ".join(CLEANUP_WORKFLOWS.keys())
        return f"Tipo de fuente '{source_type}' no encontrado. Disponibles: {disponibles}"

    wf = CLEANUP_WORKFLOWS[key]
    lines = [
        f"=== LIMPIEZA RX 11: {wf['nombre'].upper()} ===",
        f"Descripción: {wf['descripcion']}",
        f"Cadena: {' → '.join(wf['orden'])}",
        "",
    ]

    for i, paso in enumerate(wf["pasos"], 1):
        modulo_info = RX_MODULES.get(paso["modulo"], {})
        modulo_name = modulo_info.get("name", paso["modulo"])
        lines.append(f"--- Paso {i}: {modulo_name} ---")
        lines.append(f"  Configuración:")
        for param, value in paso["config"].items():
            param_info = modulo_info.get("key_parameters", {}).get(param, {})
            desc = param_info.get("desc", "")
            if desc:
                lines.append(f"    {param}: {value}  ({desc})")
            else:
                lines.append(f"    {param}: {value}")
        lines.append(f"  Notas: {paso['notas']}")
        lines.append("")

    lines.append(f"NOTAS GENERALES: {wf['notas_generales']}")
    return "\n".join(lines)


def get_module_guide(module_name: str) -> str:
    """Devuelve guía detallada de un módulo RX 11.

    Args:
        module_name: Nombre del módulo (breath_control, de_click, etc.)

    Returns:
        Guía formateada en español.
    """
    key = module_name.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in RX_MODULES:
        disponibles = ", ".join(RX_MODULES.keys())
        return f"Módulo '{module_name}' no encontrado. Disponibles: {disponibles}"

    mod = RX_MODULES[key]
    lines = [
        f"=== {mod['name'].upper()} ===",
        f"Descripción: {mod['description']}",
        "",
        "PARÁMETROS:",
    ]

    for param_name, param_info in mod["key_parameters"].items():
        if "range" in param_info:
            rango = f"Rango: {param_info['range'][0]} a {param_info['range'][1]}"
        elif "options" in param_info:
            rango = f"Opciones: {', '.join(str(o) for o in param_info['options'])}"
        else:
            rango = ""
        lines.append(f"  {param_name}:")
        lines.append(f"    {param_info['desc']}")
        lines.append(f"    {rango}  |  Default: {param_info['default']}")

    lines.append("")
    lines.append(f"CUÁNDO USAR: {mod['when_to_use']}")
    lines.append("")
    lines.append("TIPS:")
    for tip in mod["tips"]:
        lines.append(f"  • {tip}")

    # Presets de intensidad para este módulo
    lines.append("")
    lines.append("PRESETS POR INTENSIDAD:")
    for intensity_name, intensity in INTENSITY_PRESETS.items():
        config = intensity["configs"].get(key, {})
        if config:
            params_str = ", ".join(f"{k}={v}" for k, v in config.items())
            lines.append(f"  [{intensity['nombre']}] {params_str}")

    return "\n".join(lines)


def get_repair_workflow() -> str:
    """Devuelve una visión general de todos los workflows de reparación disponibles.

    Returns:
        Resumen formateado en español.
    """
    lines = [
        "=== iZOTOPE RX 11: WORKFLOWS DE REPARACIÓN ===",
        "",
        "WORKFLOWS DISPONIBLES:",
        "",
    ]

    for wf_key, wf in CLEANUP_WORKFLOWS.items():
        cadena = " → ".join(wf["orden"])
        lines.append(f"  [{wf_key}] {wf['nombre']}")
        lines.append(f"    Cadena: {cadena}")
        lines.append(f"    {wf['descripcion']}")
        lines.append("")

    lines.append("NIVELES DE INTENSIDAD:")
    for int_key, intensity in INTENSITY_PRESETS.items():
        lines.append(f"  [{int_key}] {intensity['nombre']}: {intensity['descripcion']}")

    lines.append("")
    lines.append("REGLAS GENERALES:")
    lines.append("  1. Siempre procesar de lo más específico a lo más general")
    lines.append("  2. Menos es más: empezar suave e ir subiendo si es necesario")
    lines.append("  3. Siempre comparar A/B con bypass")
    lines.append("  4. Procesar RX ANTES de Auto-Tune, EQ, compresión")
    lines.append("  5. Para samples de boom bap, preservar algo de carácter (no limpiar todo)")

    return "\n".join(lines)


def list_rx_modules() -> str:
    """Lista todos los módulos RX 11 disponibles con descripción breve.

    Returns:
        Lista formateada en español.
    """
    lines = [
        "=== MÓDULOS iZOTOPE RX 11 INSTALADOS ===",
        "",
    ]

    for key, mod in RX_MODULES.items():
        lines.append(f"  [{key}] {mod['name']}")
        lines.append(f"    {mod['description'][:100]}...")
        lines.append(f"    Usar cuando: {mod['when_to_use'][:80]}...")
        lines.append("")

    lines.append(f"Total: {len(RX_MODULES)} módulos disponibles")
    lines.append("Usar get_module_guide('nombre') para detalles completos de cada módulo")

    return "\n".join(lines)
