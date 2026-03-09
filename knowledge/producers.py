"""Producer style profiles and replication guides from GUIA_BOOM_BAP_90s_COMPLETA.txt."""

from typing import List, Dict


PRODUCERS = {
    "dj_premier": {
        "name": "DJ Premier",
        "aka": "Primo, Preemo",
        "artists": "Gang Starr, Nas, Biggie, Jay-Z, Royce da 5'9\"",
        "style_summary": "Chops cortos (1/4 a 1 compas), scratches como instrumento, drums duros y secos, minimalista",
        "drum_machine": "MPC 60 / MPC 3000",
        "swing_range": "58-62%",
        "sampling_approach": "Soul 60s-70s, jazz. Corta pedazos MUY cortos y los reorganiza. Los samples son irreconocibles despues del chop.",
        "recommended_patterns": ["premier_style", "boom_bap_basic"],
        "recommended_scales": ["pentatonic_minor", "minor_natural", "blues"],
        "recommended_progressions": ["classic_dark", "melancholic"],
        "effects_notes": "Drums secos, poca reverb, mucho punch. Scratches como hooks.",
        "reference_tracks": ["Mass Appeal", "Unbelievable", "D'Evils", "Full Clip", "Above the Clouds"],
        "replication_tips": [
            "Chops de 1-2 beats en SliceX/Edison",
            "Scratch samples programados como percusion",
            "Drums secos, poca reverb, mucho punch",
            "Kick en offbeats para bounce (step 8 es su firma)",
            "LP filter en samples para sonido vintage",
            "Vocal scratches como hooks/transiciones",
        ],
    },

    "pete_rock": {
        "name": "Pete Rock",
        "aka": "Soul Brother #1",
        "artists": "CL Smooth, Nas, Raekwon, INI",
        "style_summary": "Jazzy, soul smooth, capas de texturas, SP-1200. El mas musical de todos.",
        "drum_machine": "SP-1200",
        "swing_range": "60-65%",
        "sampling_approach": "Jazz (saxo, trompeta, Rhodes), soul (strings, voces). Loops mas largos (2-4 compases). Multiples capas de samples.",
        "recommended_patterns": ["pete_rock_groove"],
        "recommended_scales": ["dorian", "pentatonic_minor", "minor_natural"],
        "recommended_progressions": ["jazz_hiphop", "soul_feel", "neo_soul"],
        "effects_notes": "Mas reverb que Premier. Snare con room. SP-1200 12-bit crunch. Ride cymbal como hi-hat alternativo.",
        "reference_tracks": ["T.R.O.Y.", "The Creator", "Lots of Lovin", "Straighten It Out"],
        "replication_tips": [
            "Sample loops de jazz de 2-4 compases",
            "Anadir ride cymbal con velocities suaves",
            "Swing 60-65% en hats",
            "Reverb Room en snare (LuxeVerb 0.8-1.2s)",
            "Fruity Squeeze 12-bit (SP-1200 emulation)",
            "Capas: sample principal + horn stab + pad sutil",
            "Rhodes y saxo como elementos melodicos clave",
        ],
    },

    "rza": {
        "name": "RZA",
        "aka": "Bobby Digital, The Abbott",
        "artists": "Wu-Tang Clan, GZA, Ol' Dirty Bastard, Raekwon, Ghostface",
        "style_summary": "Crudo, oscuro, cinematico, lo-fi extremo. El sonido mas sucio del hip-hop.",
        "drum_machine": "SP-1200 + ASR-10",
        "swing_range": "55-62%",
        "sampling_approach": "Soul oscuro, soundtracks de kung-fu, clasica, industrial. Pianos desolados, strings lamentosas.",
        "recommended_patterns": ["rza_wu_tang"],
        "recommended_scales": ["harmonic_minor", "phrygian", "minor_natural"],
        "recommended_progressions": ["phrygian_dark", "classic_dark"],
        "effects_notes": "Mucha distorsion, filtros LP extremos, reverb larga en snare. Lo-fi agresivo. Dialogos de peliculas.",
        "reference_tracks": ["C.R.E.A.M.", "Protect Ya Neck", "Triumph", "Da Mystery of Chessboxin'"],
        "replication_tips": [
            "Fruity Squeeze agresivo + Decapitator Drive 5+",
            "LP filter extremo (Volcano 3 o Fruity Filter, cutoff bajo)",
            "Piano: notas sueltas, melancolicas, menor armonica",
            "Reverb larga en snare (LuxeVerb 1.5-2.0s)",
            "Drums: patron irregular, kick en steps inesperados",
            "Dialogos de peliculas como intros/outros",
            "Saturacion agresiva en todo el bus de drums",
        ],
    },

    "j_dilla": {
        "name": "J Dilla",
        "aka": "Jay Dee, James Yancey",
        "artists": "Slum Village, Common, De La Soul, Erykah Badu, The Pharcyde",
        "style_summary": "Swing extremo, drums off-grid, lo-fi calido, sample protagonista. El genio del timing.",
        "drum_machine": "MPC 3000",
        "swing_range": "65-75% (pero no era swing de maquina, era su FEEL natural tocando en la MPC)",
        "sampling_approach": "Todo. Soul, jazz, bossa nova, electronica, pop 80s. El sample ES el beat. Loops soulful.",
        "recommended_patterns": ["dilla_drunk"],
        "recommended_scales": ["dorian", "pentatonic_minor", "minor_natural"],
        "recommended_progressions": ["minimal_jazz", "soul_feel", "neo_soul"],
        "effects_notes": "Lo-fi calido pero no extremo. Sample protagonista. Bajo sutil. Kick and snare detras del beat.",
        "reference_tracks": ["Donuts", "Fall in Love", "Won't Do", "Players", "Nothing Like This"],
        "replication_tips": [
            "Desactivar snap en Piano Roll",
            "Mover CADA nota fuera del grid manualmente",
            "Snares 15-30ms TARDE del beat",
            "Velocities irregulares, NADA a 127",
            "Sample loop como base, bajo sutil",
            "Alt+R > Humanize: Time 10-15%, Velocity 10-20%",
            "NO usar cuantizacion. Grabar en tiempo real con MIDI",
            "El feel viene de tocar, no de programar",
        ],
    },

    "9th_wonder": {
        "name": "9th Wonder",
        "aka": "Patrick Douthit",
        "artists": "Little Brother, Destiny's Child, Jay-Z, Mary J. Blige",
        "style_summary": "Sampling limpio, soul 70s, patrones simples pero samples complejos. USABA FL STUDIO.",
        "drum_machine": "FL Studio (no hardware!)",
        "swing_range": "0% (cuantizacion perfecta)",
        "sampling_approach": "Soul 70s limpio, Motown. Chops medio-largos. El sample suena bonito y reconocible.",
        "recommended_patterns": ["9th_wonder_clean"],
        "recommended_scales": ["pentatonic_minor", "minor_natural", "dorian"],
        "recommended_progressions": ["soul_feel", "jazz_hiphop"],
        "effects_notes": "Procesamiento limpio, poco lo-fi. Clap layeado con snare SIEMPRE. Bass limpio.",
        "reference_tracks": ["Threat", "The Listening", "Lovin' It"],
        "replication_tips": [
            "Patron basico (patron '9th_wonder_clean')",
            "Sample soul loop de 2-4 compases",
            "Layear clap + snare SIEMPRE",
            "Bajo limpio, synth sub",
            "Cuantizacion al 100% (a diferencia de Dilla)",
            "Procesamiento limpio, poco lo-fi",
            "El sample hace el trabajo pesado, drums simples",
        ],
    },

    "madlib": {
        "name": "Madlib",
        "aka": "Quasimoto, Lord Quas, Beat Konducta",
        "artists": "Madvillain (con MF DOOM), Freddie Gibbs",
        "style_summary": "Eclectico, lo-fi, experimental, crate digging extremo. El mas raro de todos.",
        "drum_machine": "MPC (varios modelos)",
        "swing_range": "variable (depende del sample)",
        "sampling_approach": "TODO. Jazz raro, world music, prog rock, OSTs, library music, artistas desconocidos. Busca lo raro.",
        "recommended_patterns": ["boom_bap_basic", "dilla_drunk"],
        "recommended_scales": ["minor_natural", "pentatonic_minor", "blues"],
        "recommended_progressions": ["minimal_jazz", "soul_feel"],
        "effects_notes": "Lo-fi extremo. Drums del propio sample (no one-shots separados). Pitch shifting agresivo.",
        "reference_tracks": ["Madvillainy", "Figaro", "Accordion", "All Caps", "Meat Grinder"],
        "replication_tips": [
            "Samplear cosas raras, no lo obvio",
            "Drums del propio sample (no reemplazar)",
            "Lo-fi extremo: Fruity Squeeze + Decapitator",
            "Pitch shifting agresivo (bajar 3-5 semitonos)",
            "Estructuras no convencionales",
            "Buscar vinilos raros, world music, library music",
        ],
    },

    "havoc": {
        "name": "Havoc",
        "aka": "Kejuan Muchita (Mobb Deep)",
        "artists": "Mobb Deep, Prodigy",
        "style_summary": "Minimalista, oscuro, piano melancolico. Menos es mas.",
        "drum_machine": "SP-1200 / ASR-10",
        "swing_range": "54-57% (sutil)",
        "sampling_approach": "Soul oscuro, piano clasico, strings. Pocos elementos pero cada uno perfecto.",
        "recommended_patterns": ["havoc_minimal"],
        "recommended_scales": ["harmonic_minor", "minor_natural", "phrygian"],
        "recommended_progressions": ["classic_dark", "phrygian_dark"],
        "effects_notes": "Hi-hats en semicorcheas constantes. Espacio vacio es clave. Snare protagonista.",
        "reference_tracks": ["Shook Ones Pt. II", "Survival of the Fittest"],
        "replication_tips": [
            "Patron 'havoc_minimal': kick solo en 1 y 9",
            "Hi-hats en CADA semicorchea con velocity variable",
            "Piano melancolico: notas sueltas, menor armonica",
            "POCOS elementos, cada uno perfecto",
            "El espacio vacio es tan importante como los golpes",
        ],
    },

    "large_professor": {
        "name": "Large Professor",
        "aka": "Extra P",
        "artists": "Nas, Main Source",
        "style_summary": "SP-1200, funk/soul, drums punchy. Chops cortos, scratches sutiles.",
        "drum_machine": "SP-1200",
        "swing_range": "58-62%",
        "sampling_approach": "Funk, soul, jazz. Chops cortos bien colocados.",
        "recommended_patterns": ["boom_bap_basic", "premier_style"],
        "recommended_scales": ["minor_natural", "blues", "pentatonic_minor"],
        "recommended_progressions": ["classic_dark", "soul_feel"],
        "effects_notes": "Drums punchy, SP-1200 character. Scratches sutiles.",
        "reference_tracks": ["Live at the Barbeque", "Looking at the Front Door"],
        "replication_tips": [
            "SP-1200 emulation: Fruity Squeeze 12-bit, 26kHz",
            "Drums punchy con ataque definido",
            "Chops cortos de funk y soul",
            "Scratches sutiles como acento",
        ],
    },

    "alchemist": {
        "name": "The Alchemist",
        "aka": "Alan Daniel Maman",
        "artists": "Dilated Peoples, Mobb Deep, Nas, Eminem, Freddie Gibbs",
        "style_summary": "Soul oscuro, loops largos, drums minimalistas. Productor moderno con sonido clasico.",
        "drum_machine": "MPC / software",
        "swing_range": "54-57% (sutil)",
        "sampling_approach": "Soul oscuro, loops largos. Sampling sofisticado y cinematico.",
        "recommended_patterns": ["havoc_minimal", "boom_bap_basic"],
        "recommended_scales": ["minor_natural", "phrygian", "harmonic_minor"],
        "recommended_progressions": ["classic_dark", "melancholic"],
        "effects_notes": "Loops largos, drums minimalistas. Soul oscuro con texturas cinematicas.",
        "reference_tracks": ["We Gonna Make It", "Keep It Thoro (beat)"],
        "replication_tips": [
            "Loops largos de soul oscuro (4-8 compases)",
            "Drums minimalistas, espaciados",
            "Swing sutil 54-57%",
            "Texturas cinematicas como capas",
        ],
    },

    "hi_tek": {
        "name": "Hi-Tek",
        "aka": "Tony Cottrell",
        "artists": "Talib Kweli (Reflection Eternal), Mos Def",
        "style_summary": "Soul 70s, gospel, bajo gordo, drums organicos.",
        "drum_machine": "MPC / ASR-10",
        "swing_range": "58-62%",
        "sampling_approach": "Soul 70s, gospel, funk. Bajo gordo como protagonista.",
        "recommended_patterns": ["boom_bap_basic", "pete_rock_groove"],
        "recommended_scales": ["dorian", "pentatonic_minor", "minor_natural"],
        "recommended_progressions": ["soul_feel", "jazz_hiphop"],
        "effects_notes": "Bajo gordo, drums organicos. Soul calido con gospel.",
        "reference_tracks": ["The Blast", "Move Somethin'"],
        "replication_tips": [
            "Soul/gospel samples con feeling calido",
            "Bajo GORDO como protagonista",
            "Drums organicos con swing standard",
        ],
    },

    "buckwild": {
        "name": "Buckwild",
        "aka": "D.I.T.C. member",
        "artists": "Big L, Fat Joe, O.C., D.I.T.C.",
        "style_summary": "Soul 60s-70s, samples melodicos, drums pesados.",
        "drum_machine": "SP-1200 / MPC",
        "swing_range": "58-62%",
        "sampling_approach": "Soul 60s-70s. Samples melodicos y accesibles. Drums pesados.",
        "recommended_patterns": ["boom_bap_basic", "advanced_2bar"],
        "recommended_scales": ["minor_natural", "pentatonic_minor"],
        "recommended_progressions": ["classic_dark", "melancholic"],
        "effects_notes": "Drums pesados, samples melodicos claros.",
        "reference_tracks": ["Twinz (Deep Cover 98)", "Where I'm From"],
        "replication_tips": [
            "Samples melodicos de soul 60s-70s",
            "Drums pesados con punch",
            "Swing standard 58-62%",
        ],
    },

    "lord_finesse": {
        "name": "Lord Finesse",
        "aka": "D.I.T.C. member",
        "artists": "D.I.T.C., Big L",
        "style_summary": "Funk/soul 70s, drums bouncy, swing fuerte.",
        "drum_machine": "SP-1200 / MPC",
        "swing_range": "60-65%",
        "sampling_approach": "Funk/soul 70s. Chops bouncy y funkys.",
        "recommended_patterns": ["pete_rock_groove", "boom_bap_basic"],
        "recommended_scales": ["blues", "pentatonic_minor", "dorian"],
        "recommended_progressions": ["soul_feel", "jazz_hiphop"],
        "effects_notes": "Drums bouncy, swing fuerte. Funk flavor.",
        "reference_tracks": ["Hip 2 Da Game", "Actual Facts"],
        "replication_tips": [
            "Funk samples, bouncy and groovy",
            "Swing fuerte 60-65%",
            "Drums bouncy con mucho pocket",
        ],
    },

    "marley_marl": {
        "name": "Marley Marl",
        "aka": "El pionero",
        "artists": "MC Shan, Biz Markie, Big Daddy Kane, Kool G Rap",
        "style_summary": "INVENTO el sampling de drums individual. El padre del boom bap moderno.",
        "drum_machine": "SP-1200 / E-MU",
        "swing_range": "55-60%",
        "sampling_approach": "Fue el primero en samplear kicks, snares y hats individualmente de vinilos.",
        "recommended_patterns": ["boom_bap_basic"],
        "recommended_scales": ["minor_natural", "pentatonic_minor"],
        "recommended_progressions": ["classic_dark"],
        "effects_notes": "Pionero del sonido. Drums sampleados de vinilo.",
        "reference_tracks": ["The Bridge", "Road to the Riches"],
        "replication_tips": [
            "Samplear drums de vinilos de funk y soul",
            "Drums como protagonistas absolutos",
            "El primer sonido boom bap: simple pero revolucionario",
        ],
    },
}


def get_producer_profile(producer_id: str) -> str:
    """Format a producer profile as a readable string."""
    if producer_id not in PRODUCERS:
        available = ", ".join(PRODUCERS.keys())
        return f"Producer not found: {producer_id}. Available: {available}"

    p = PRODUCERS[producer_id]
    lines = [
        f"=== {p['name']} ({p.get('aka', '')}) ===",
        f"Artistas: {p['artists']}",
        f"Estilo: {p['style_summary']}",
        f"Drum Machine: {p['drum_machine']}",
        f"Swing: {p['swing_range']}",
        f"Sampling: {p['sampling_approach']}",
        f"Efectos: {p['effects_notes']}",
        f"",
        f"Patrones recomendados: {', '.join(p['recommended_patterns'])}",
        f"Escalas recomendadas: {', '.join(p['recommended_scales'])}",
        f"Progresiones recomendadas: {', '.join(p['recommended_progressions'])}",
        f"",
        f"Tracks de referencia: {', '.join(p['reference_tracks'])}",
        f"",
        f"COMO REPLICAR EN FL STUDIO:",
    ]
    for i, tip in enumerate(p["replication_tips"], 1):
        lines.append(f"  {i}. {tip}")

    return "\n".join(lines)


def list_producers() -> str:
    """List all available producer profiles."""
    lines = ["=== PRODUCTORES DISPONIBLES ===\n"]
    for pid, p in PRODUCERS.items():
        lines.append(f"  {pid}: {p['name']} - {p['style_summary'][:60]}...")
    return "\n".join(lines)
