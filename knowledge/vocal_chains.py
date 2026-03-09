"""Vocal processing chains with exact settings from plugins_voz_fl_studio.txt.

Encodes the complete professional vocal chain (10-slot order), style-specific
recipes, advanced tricks, recording tips, mix levels, checklist, free plugin
alternatives, and investment tiers.
"""

from typing import Dict, List, Optional


# ============================================================================
# SLOT 1 - GATE / NOISE GATE
# ============================================================================

GATE_SETTINGS = {
    "fruity_limiter_gate": {
        "plugin": "Fruity Limiter",
        "mode": "GATE",
        "native": True,
        "settings": {
            "threshold": "Adjust until noise disappears between phrases",
            "attack_ms": (0.5, 2.0),
            "release_ms": (50, 100),
            "hold_ms": 50,
        },
        "notes": "Built into FL Studio, use gate mode tab.",
    },
    "waves_ns1": {
        "plugin": "Waves NS1 Noise Suppressor",
        "native": False,
        "settings": {
            "single_knob": "Turn until noise is gone",
        },
        "notes": "Do not overdo it or voice sounds 'underwater'.",
    },
    "izotope_rx_voice_denoise": {
        "plugin": "iZotope RX Voice De-noise",
        "native": False,
        "settings": {
            "learn": "Select a section with ONLY noise, hit Learn",
            "reduction_dB": (-10, -20),
        },
        "notes": "Most intelligent option. Learns noise profile. "
                 "Record 5 seconds of silence at the start of every session "
                 "to give RX a clean noise sample.",
    },
}


# ============================================================================
# SLOT 2 - PITCH CORRECTION (Autotune)
# ============================================================================

PITCH_CORRECTION_SETTINGS = {
    "antares_autotune_pro": {
        "plugin": "Antares Auto-Tune Pro",
        "native": False,
        "tier": "industry_standard",
        "settings": {
            "retune_speed": {
                "robotic": 0,
                "natural": (20, 50),
                "minimal_effect": 80,
            },
            "humanize": {
                "trap_urban": (0, 20),
                "ballad": 50,
            },
            "flex_tune": {
                "hard_tune": 0,
                "soft": 50,
            },
            "tracking": {
                "rap": "Relaxed",
                "clean_singing": "Choose",
            },
            "mode": {
                "live_recording": "Low Latency",
                "mixing": "Auto",
            },
        },
    },
    "waves_tune_realtime": {
        "plugin": "Waves Tune Real-Time",
        "native": False,
        "tier": "intermediate",
        "settings": {
            "speed": "0 = hard, higher = natural",
            "note_transition": ["Smooth", "Fast"],
        },
        "notes": "Cheaper and less CPU than Antares.",
    },
    "pitcher_native": {
        "plugin": "Pitcher",
        "native": True,
        "tier": "beginner",
        "settings": {
            "replace": True,
            "scale": "Select manually (e.g. C Minor)",
            "speed_knob": "Left = strong effect",
        },
        "notes": "Does not have Antares quality but works. "
                 "Can connect MIDI to control notes via keyboard.",
    },
}

PITCH_CORRECTION_RULE = (
    "ALWAYS place autotune BEFORE compression. "
    "If you compress first, autotune receives a squashed signal "
    "and cannot detect pitch correctly."
)


# ============================================================================
# SLOT 3 - SUBTRACTIVE EQ (remove the bad)
# ============================================================================

SUBTRACTIVE_EQ_SETTINGS = {
    "fabfilter_proq3": {
        "plugin": "FabFilter Pro-Q 3",
        "native": False,
        "bands": {
            "high_pass_filter": {
                "description": "Cut useless low frequencies. MANDATORY.",
                "freq_hz_low_voice": 80,
                "freq_hz_high_voice": (100, 120),
                "slope_dB_oct": 24,
                "notes": "Removes rumble, mic noise, footsteps, etc.",
            },
            "mud_cut": {
                "description": "Remove cardboard/nasal tone",
                "freq_range_hz": (200, 400),
                "technique": "Boost +10dB with narrow Q, sweep, cut where it sounds bad",
                "cut_dB": (-2, -4),
                "Q": (1.5, 3.0),
            },
            "boxiness_cut": {
                "description": "Remove boxy sound",
                "freq_range_hz": (400, 800),
                "technique": "Same sweep technique: boost, sweep, find ugly, cut",
                "cut_dB": (-1, -3),
            },
            "harshness_cut": {
                "description": "Remove ear-piercing harshness",
                "freq_range_hz": (2000, 4000),
                "cut_dB": (-2, -4),
                "Q": "narrow",
                "notes": "If the voice 'stings' the ears, look here.",
            },
        },
    },
    "parametric_eq2_native": {
        "plugin": "Parametric EQ 2",
        "native": True,
        "bands": {
            "band_1": "High-pass at 80-100Hz",
            "band_2_to_5": "Sweep and cut problem frequencies",
            "band_7": "Reserve for brightness later",
        },
        "notes": "Very capable. Same process as Pro-Q 3.",
    },
}

SWEEP_AND_DESTROY_TECHNIQUE = {
    "name": "Sweep and Destroy",
    "steps": [
        "1. Take an EQ band",
        "2. Set it to +10dB with very narrow Q (Q=10-15)",
        "3. Sweep slowly across all frequencies",
        "4. Where it sounds horrible = that is the problem",
        "5. Cut that frequency -2 to -5dB",
        "6. Repeat with another band",
    ],
    "common_errors": [
        "Do NOT cut too much. Multiple small cuts beat one brutal cut.",
        "Do NOT cut fundamental voice frequencies (150-500Hz has the body). "
        "Cutting everything there makes voice sound thin and lifeless.",
    ],
}


# ============================================================================
# SLOT 4 - COMPRESSION (control dynamics)
# ============================================================================

COMPRESSION_SETTINGS = {
    "waves_cla2a": {
        "plugin": "Waves CLA-2A",
        "native": False,
        "type": "Optical compressor emulation",
        "character": "Smooth, warm, musical. Ideal for ballads and R&B.",
        "settings": {
            "peak_reduction": "Turn until it reduces 3-6dB on peaks",
            "gain": "Raise to compensate lost volume",
        },
    },
    "fabfilter_proc2": {
        "plugin": "FabFilter Pro-C 2",
        "native": False,
        "type": "Versatile and precise",
        "settings": {
            "style": "Vocal",
            "threshold": "Lower until meter shows -3 to -6dB reduction",
            "ratio_normal": "3:1 to 4:1",
            "ratio_aggressive_trap": "6:1 to 8:1",
            "attack_ms": (5, 15),
            "release_ms": (50, 100),
            "release_auto": True,
            "knee_natural": "Soft",
            "knee_aggressive": "Hard",
            "makeup_gain": "Auto gain ON",
        },
        "notes": "Has a specific Vocal mode.",
    },
    "waves_rvox": {
        "plugin": "Waves RVox",
        "native": False,
        "type": "Fast and aggressive",
        "settings": {
            "compression": "Turn until -4 to -8dB reduction",
            "output": "Compensate volume",
            "gate": "Raise until it removes noise between phrases",
        },
        "notes": "Ideal for rap and trap due to simplicity.",
    },
    "fruity_limiter_comp": {
        "plugin": "Fruity Limiter",
        "native": True,
        "mode": "COMP",
        "settings": {
            "threshold_dB": (-15, -20),
            "ratio": "4:1",
            "attack_ms": 10,
            "release_ms": 80,
        },
        "notes": "Decent. Not as 'analog' as paid plugins but works.",
    },
}

SERIAL_COMPRESSION_TECHNIQUE = {
    "name": "Serial Compression (2-pass, pro level)",
    "principle": "Two gentle compressors beat one aggressive compressor.",
    "first_compressor": {
        "ratio": "2:1",
        "reduction_dB": (2, 3),
        "purpose": "Tame the peaks",
    },
    "second_compressor": {
        "ratio": "4:1",
        "reduction_dB": (3, 4),
        "purpose": "Control dynamics",
    },
    "result": "Super consistent but natural voice without 'crushed' effect.",
}


# ============================================================================
# SLOT 5 - ADDITIVE EQ (add brightness and presence)
# ============================================================================

ADDITIVE_EQ_SETTINGS = {
    "presence": {
        "description": "Makes the voice CUT through the mix. Understand every word.",
        "freq_hz": (2500, 5000),
        "boost_dB": (2, 4),
        "Q": (0.7, 1.5),
    },
    "air_brightness": {
        "description": "Professional 'sparkle'. Sensation of air and openness.",
        "freq_hz": (10000, 16000),
        "boost_dB": (2, 5),
        "Q": (0.5, 1.0),
        "band_type": "HIGH SHELF works better than bell here",
        "warning": "If voice is already bright, do not overdo it.",
    },
    "warmth": {
        "description": "Optional. Only if voice sounds thin and lacks body.",
        "freq_hz": (200, 300),
        "boost_dB": (1, 2),
        "notes": "VERY subtle.",
    },
}

ADDITIVE_EQ_VALIDATION = {
    "bypass_test": (
        "Enable/disable the EQ (bypass). If turning it off makes the voice "
        "'go dark' and turning it on 'opens it up', you are on the right track."
    ),
    "overdone_signs": "If it sounds 'metallic' or 'hissy', you went too far.",
    "reference": (
        "Put on a professional song of the style you want and compare. "
        "Your voice should have SIMILAR brightness, not more."
    ),
}


# ============================================================================
# SLOT 6 - SATURATION / COLOR
# ============================================================================

SATURATION_SETTINGS = {
    "soundtoys_decapitator": {
        "plugin": "Soundtoys Decapitator",
        "native": False,
        "title": "The king of vocal saturation",
        "settings": {
            "style_subtle": "A",
            "style_aggressive": "E",
            "drive_subtle_pct": (20, 40),
            "drive_noticeable_pct": (50, 70),
            "tone": "Adjust to taste (right = more brightness)",
            "mix_pct": (30, 60),
            "low_cut_hz": 100,
            "low_cut_note": "Activate. Do not saturate the lows.",
        },
        "notes": "'Punish' button is for brutal distortion. "
                 "Only for creative effects, NOT for clean mixing.",
    },
    "waves_j37_tape": {
        "plugin": "Waves J37 Tape",
        "native": False,
        "settings": {
            "formula_subtle": "IEC1",
            "formula_warm": "NAB",
            "speed_clean": "15ips",
            "speed_color": "7.5ips",
            "input": "Raise until the meter moves slightly",
            "wow_flutter": "0 or very low for vocals",
        },
    },
    "softube_saturation_knob": {
        "plugin": "Softube Saturation Knob",
        "native": False,
        "free": True,
        "settings": {
            "mode": "Keep High (preserves highs for vocals)",
            "amount_pct": (20, 40),
        },
    },
    "fruity_waveshaper": {
        "plugin": "Fruity Waveshaper",
        "native": True,
        "settings": {
            "presets": ["Light saturation", "Warm"],
            "mix_pct": (20, 40),
        },
        "notes": "Works surprisingly well for being free.",
    },
}


# ============================================================================
# SLOT 7 - DE-ESSER (control S and T sibilance)
# ============================================================================

DEESSER_SETTINGS = {
    "fabfilter_prods": {
        "plugin": "FabFilter Pro-DS",
        "native": False,
        "settings": {
            "freq_hz": (5000, 9000),
            "threshold": "Lower until it catches sibilants",
            "range_dB": (-3, -8),
            "mode_precise": "Single Band",
            "mode_natural": "Wide Band",
        },
        "notes": "'Audition' mode lets you hear ONLY what is being removed. "
                 "Use it to verify it is catching the S correctly.",
    },
    "waves_sibilance": {
        "plugin": "Waves Sibilance",
        "native": False,
        "settings": {
            "threshold": "Lower until it controls sibilance",
            "mode": ["Broad", "Split"],
        },
    },
    "spitfish": {
        "plugin": "Spitfish",
        "native": False,
        "free": True,
        "comparable_to": "FabFilter Pro-DS",
        "notes": "Free de-esser alternative.",
    },
    "fruity_limiter_deesser_hack": {
        "plugin": "Fruity Limiter + Parametric EQ 2",
        "native": True,
        "technique": "Hack - not ideal but works without paid plugins",
        "steps": [
            "1. Place Parametric EQ 2 BEFORE the Limiter",
            "2. In EQ: boost +6dB in the 5-8kHz zone (detection only)",
            "3. In Limiter: COMP mode, low threshold",
        ],
    },
}

# Dynamic EQ approach (Pro-Q 3)
DEESSER_DYNAMIC_EQ = {
    "plugin": "FabFilter Pro-Q 3",
    "technique": "Dynamic EQ band",
    "settings": {
        "band_type": "Dynamic Bell",
        "freq_hz": (5000, 9000),
        "threshold": "Set so it only activates on sibilants",
        "range_dB": (-3, -8),
    },
    "notes": "Pro-Q 3 dynamic bands act as a transparent de-esser.",
}


# ============================================================================
# SLOT 8 - SOUNDGOODIZER (the truth)
# ============================================================================

SOUNDGOODIZER_TRUTH = {
    "what_it_really_is": (
        "Soundgoodizer is a Maximus (multiband compressor) with presets "
        "simplified to a single knob. It is NOT magic. It is multiband "
        "compression + saturation + limiting."
    ),
    "presets": {
        "A": {
            "character": "Most subtle and warm. BEST FOR VOCALS.",
            "max_pct_for_vocals": (30, 50),
        },
        "B": {
            "character": "More aggressive, more brightness. Can work for urban vocals.",
            "max_pct_for_vocals": (20, 40),
        },
        "C": {
            "character": "Very aggressive, heavy compression. Too much for solo vocals.",
            "recommended_for_vocals": False,
        },
        "D": {
            "character": "BRUTAL. Crushes everything. Only for extreme creative effects.",
            "recommended_for_vocals": False,
        },
    },
    "never_100_pct": (
        "Never at 100%. Sounds crushed, no dynamics, artificial. "
        "Voice loses nuances and becomes a wall of sound."
    ),
    "placement": (
        "AT THE END, after the entire chain (or second to last, before the limiter). "
        "NEVER at the beginning. Placing it before EQ/compression processes noise too."
    ),
    "honest_recommendation": {
        "quick_demos": "Soundgoodizer preset A at 40%",
        "professional_mix": (
            "NO. Use Maximus directly for full control over each frequency band. "
            "Soundgoodizer applies the same compression to lows, mids, and highs "
            "without letting you control it."
        ),
    },
}

MAXIMUS_VOCAL_SETTINGS = {
    "plugin": "Maximus",
    "native": True,
    "description": "What Soundgoodizer does behind the scenes, but YOU decide how much.",
    "bands": {
        "LOW": {
            "range_hz": (20, 200),
            "compression": "Gentle, remove rumble",
        },
        "MID": {
            "range_hz": (200, 5000),
            "compression": "Moderate - where the voice lives",
        },
        "HIGH": {
            "range_hz": (5000, 20000),
            "compression": "Gentle + subtle brightness boost",
        },
    },
    "master": "Soft limiter",
}


# ============================================================================
# SLOT 9 - REVERB / DELAY (sends, NOT inserts)
# ============================================================================

REVERB_DELAY_SETTINGS = {
    "golden_rule": (
        "Use sends (buses), NOT direct inserts. "
        "This way you control how much effect goes to the voice "
        "without affecting the dry signal."
    ),
    "fl_send_setup": {
        "steps": [
            "1. Place the voice on Insert 1 of the Mixer",
            "2. Create Insert 5 for Reverb (rename to 'VOX REVERB')",
            "3. Create Insert 6 for Delay (rename to 'VOX DELAY')",
            "4. On Insert 1, turn the send knob toward Insert 5 and 6",
            "5. On Insert 5 and 6, set plugins to 100% WET",
            "6. Control the amount with the send knobs",
        ],
    },
    "reverb": {
        "valhalla_vintageverb": {
            "plugin": "Valhalla VintageVerb",
            "native": False,
            "trap_urban": {
                "mode": "Plate or Room",
                "decay_s": (1.0, 1.8),
                "predelay_ms": (20, 40),
                "mix_pct": 100,
                "damping_high_hz": (4000, 8000),
                "notes": "Short, do not muddy. Reverb should NOT be brighter than the voice.",
            },
            "ballad_pop": {
                "mode": "Concert Hall or Chamber",
                "decay_s": (2.0, 3.5),
                "predelay_ms": (30, 60),
                "damping": "More subtle",
            },
        },
        "fruity_reeverb2": {
            "plugin": "Fruity Reeverb 2",
            "native": True,
            "settings": {
                "decay_s": (1.5, 2.5),
                "damping_hz": (5000, 8000),
                "mix_pct": 100,
            },
            "notes": "Good. Not as 'lush' as Valhalla but functional.",
        },
        "valhalla_supermassive": {
            "plugin": "Valhalla Supermassive",
            "native": False,
            "free": True,
            "comparable_to": "Any professional reverb",
        },
    },
    "delay": {
        "soundtoys_echoboy": {
            "plugin": "Soundtoys EchoBoy",
            "native": False,
            "settings": {
                "style": ["Studio Tape", "Digital"],
                "tempo_sync": True,
                "division_obvious": "1/4",
                "division_subtle": "1/8",
                "mix_pct": 100,
                "feedback_pct": (20, 35),
                "saturation": "Subtle, adds warmth to the delay",
            },
        },
        "fruity_delay3": {
            "plugin": "Fruity Delay 3",
            "native": True,
            "settings": {
                "sync": True,
                "time": ["1/4", "3/8"],
                "feedback_pct": (25, 35),
                "filter_lowpass_hz": (5000, 8000),
                "filter_notes": "Dark delay = more professional sounding",
                "mix_pct": 100,
            },
        },
    },
    "delay_eq_trick": (
        "After the delay, place an EQ and cut lows (below 200Hz) "
        "and highs (above 8kHz). The delay will not compete with the "
        "main voice; it only accompanies it as a 'distant' echo."
    ),
}


# ============================================================================
# SLOT 10 - FINAL LIMITER (protection only)
# ============================================================================

LIMITER_SETTINGS = {
    "purpose": "Last plugin in the chain. Ensures no peak exceeds 0dB.",
    "ceiling_dB": -0.3,
    "ceiling_note": "NEVER 0dB exact. Always leave headroom.",
    "fabfilter_prol2": {
        "plugin": "FabFilter Pro-L 2",
        "native": False,
        "settings": {
            "style_trap": "Modern",
            "style_pop": "Transparent",
            "gain": "Raise until -1 to -3dB reduction MAX",
            "ceiling_dB": -0.3,
        },
        "notes": "If reducing more than -3dB, your mix needs adjustment upstream.",
    },
    "waves_l1_l2": {
        "plugin": "Waves L1/L2",
        "native": False,
        "settings": {
            "threshold": "Lower gently",
            "ceiling_dB": -0.3,
            "release": "ARC (automatic)",
        },
    },
    "fruity_limiter_limit": {
        "plugin": "Fruity Limiter",
        "native": True,
        "mode": "LIMIT",
        "settings": {
            "ceiling_dB": -0.3,
            "attack_ms": 5,
            "release_ms": 100,
            "gain": "Raise until the limiter barely touches the peaks",
        },
    },
}


# ============================================================================
# COMPLETE 10-SLOT STANDARD VOCAL CHAIN
# ============================================================================

VOCAL_CHAIN_STANDARD = {
    "name": "Professional Vocal Chain - Standard (10 slots)",
    "important": (
        "Order matters A LOT. Each plugin processes the signal coming from "
        "the previous one. If you change the order, the result changes drastically."
    ),
    "slots": {
        1: {
            "name": "Gate / Noise Gate",
            "purpose": "Eliminate background noise when not singing/rapping",
            "optional": True,
            "recommended": True,
            "plugins": GATE_SETTINGS,
        },
        2: {
            "name": "Pitch Correction (Autotune)",
            "purpose": "Correct or stylize pitch",
            "rule": PITCH_CORRECTION_RULE,
            "plugins": PITCH_CORRECTION_SETTINGS,
        },
        3: {
            "name": "Subtractive EQ (remove the bad)",
            "purpose": "Clean the voice BEFORE adding anything nice",
            "most_important": True,
            "plugins": SUBTRACTIVE_EQ_SETTINGS,
            "technique": SWEEP_AND_DESTROY_TECHNIQUE,
        },
        4: {
            "name": "Compression (control dynamics)",
            "purpose": "Make voice sound professional and consistent",
            "plugins": COMPRESSION_SETTINGS,
            "advanced_technique": SERIAL_COMPRESSION_TECHNIQUE,
        },
        5: {
            "name": "Additive EQ (add brightness and presence)",
            "purpose": "After cleaning and compressing, add the beauty",
            "settings": ADDITIVE_EQ_SETTINGS,
            "validation": ADDITIVE_EQ_VALIDATION,
        },
        6: {
            "name": "Saturation / Color",
            "purpose": "Add harmonics for richer, more present voice. "
                       "Difference between digital/cold and warm/analog.",
            "plugins": SATURATION_SETTINGS,
        },
        7: {
            "name": "De-esser (control S and T sibilance)",
            "purpose": "Control sibilants that become worse after compression and brightness",
            "plugins": DEESSER_SETTINGS,
            "dynamic_eq": DEESSER_DYNAMIC_EQ,
        },
        8: {
            "name": "Soundgoodizer / Maximus",
            "purpose": "Multiband processing (optional polish)",
            "truth": SOUNDGOODIZER_TRUTH,
            "superior_alternative": MAXIMUS_VOCAL_SETTINGS,
        },
        9: {
            "name": "Reverb / Delay (sends, NOT inserts)",
            "purpose": "Spatial effects for depth and dimension",
            "settings": REVERB_DELAY_SETTINGS,
        },
        10: {
            "name": "Final Limiter (protection only)",
            "purpose": "Ensure no peak exceeds 0dB. Safety net.",
            "settings": LIMITER_SETTINGS,
        },
    },
}


# ============================================================================
# VOCAL CHAIN - BRIGHT TRAP
# ============================================================================

VOCAL_CHAIN_BRIGHT_TRAP = {
    "name": "Bright Trap / Urban Vocal Recipe",
    "description": (
        "Voice that CUTS the mix, sounds crisp, crystalline, "
        "heard perfectly even on phone speakers."
    ),
    "eq": {
        "plugin": "Parametric EQ 2 or Pro-Q 3",
        "bands": {
            1: {"type": "High Pass", "freq_hz": 90, "slope": "24dB/oct", "purpose": "eliminate lows"},
            2: {"type": "Cut", "freq_hz": 250, "gain_dB": -2, "Q": 2, "purpose": "remove mud"},
            3: {"type": "Cut", "freq_hz": 500, "gain_dB": -1.5, "Q": 2, "purpose": "remove boxiness"},
            4: {"type": "Boost", "freq_hz": 3000, "gain_dB": 2.5, "Q": 1, "purpose": "presence"},
            5: {"type": "Boost", "freq_hz": 5000, "gain_dB": 2, "Q": 1.5, "purpose": "clarity"},
            6: {"type": "High Shelf", "freq_hz": 12000, "gain_dB": 3, "purpose": "AIR / BRIGHTNESS"},
        },
    },
    "compression": {
        "plugin": "Pro-C 2 or Fruity Limiter",
        "ratio": "4:1",
        "attack_ms": 10,
        "release": "Auto or 80ms",
        "reduction_dB": (-4, -6),
    },
    "saturation": {
        "plugin": "Decapitator or Saturation Knob",
        "drive_pct": (20, 30),
        "mix_pct": (40, 50),
    },
    "extra_brightness": {
        "option_a": "Waves Vitamin or Aphex Aural Exciter",
        "option_b_trick": (
            "Duplicate the voice, high-pass at 8kHz, raise slightly. "
            "Mix subtly with the original = natural brightness without EQ."
        ),
    },
    "reverb": {
        "type": "Plate",
        "decay_s": 1.2,
        "predelay_ms": 25,
        "damping_high_hz": 6000,
        "damping_note": "Reverb must NOT have more brightness than the voice",
        "routing": "Send, NOT insert",
    },
    "result": "Voice heard perfectly on any system, from studio monitors to phone earbuds.",
}


# ============================================================================
# VOCAL CHAIN - YUNG BEEF STYLE
# ============================================================================

VOCAL_CHAIN_YUNG_BEEF = {
    "name": "Yung Beef Style Processing",
    "description": (
        "Characteristic Spanish trap sound with Atlanta scene influences."
    ),
    "autotune": {
        "retune_speed_ms": (0, 15),
        "character": "Very fast = robotic effect",
        "humanize": "Low",
        "key": "Detect or set manually",
        "flex_tune": "Low",
    },
    "compression": {
        "ratio": "4:1 to 8:1",
        "attack_ms": (5, 15),
        "release_ms": (50, 100),
        "character": "Strong compression",
    },
    "eq": {
        "high_pass_hz": (80, 100),
        "presence_boost": {"freq_hz": (3000, 5000), "gain_dB": 3},
        "air_boost": {"freq_hz": (10000, 12000), "gain_dB": 2},
        "mud_cut": {"freq_hz": (200, 400), "gain_dB": -2},
    },
    "saturation": {
        "type": "Subtle tape saturation",
        "purpose": "Adds characteristic 'dirt'",
    },
    "reverb": {
        "type": ["Room", "Plate"],
        "decay_s": (0.8, 1.5),
        "mix_pct": (15, 25),
        "predelay_ms": (20, 40),
    },
    "delay": {
        "division": ["1/8", "1/4"],
        "mix_pct": (10, 20),
        "feedback_pct": (20, 30),
        "character": "Subtle",
    },
}


# ============================================================================
# VOCAL TRICKS - Advanced techniques
# ============================================================================

VOCAL_TRICKS: Dict[str, dict] = {
    "doubles": {
        "name": "Double Vocal (thick effect)",
        "steps": [
            "Duplicate the vocal",
            "Pan one L, the other R",
            "Offset one by 10-20ms with Fruity Delay",
            "Raise pitch of one slightly (+5 cents)",
            "Lower pitch of the other (-5 cents)",
        ],
    },
    "autotune_midi": {
        "name": "Native Autotune with Pitcher via MIDI",
        "steps": [
            "Insert Pitcher on the mixer channel",
            "Activate 'MIDI'",
            "Connect a MIDI channel to Pitcher",
            "Now you can play autotune notes with a keyboard",
        ],
    },
    "vocal_chops": {
        "name": "Quick Vocal Chops",
        "steps": [
            "Use Edison to record",
            "Ctrl+U = region detection",
            "Drag to playlist as 'chopped'",
            "Use Slice X to manipulate",
        ],
    },
    "sidechain_vocal": {
        "name": "Sidechain Vocal to Beat",
        "steps": [
            "Fruity Limiter on the vocal",
            "Sidechain from the kick",
            "Threshold: -10 to -20dB",
        ],
        "result": "Voice 'breathes' with the beat.",
    },
    "pitch_automation": {
        "name": "Real-time Pitch Shifting",
        "steps": [
            "Automation clip on the sampler pitch",
            "Creates 'chipmunk' or 'demon' effects",
        ],
        "use_case": "Useful for ad-libs.",
    },
    "reverb_throws": {
        "name": "Reverb Throw (pro effect)",
        "steps": [
            "Create a reverb bus (100% wet)",
            "Automate the send only on certain words",
            "Right-click the send knob > Create automation clip",
            "Draw peaks ONLY on the words you want with reverb",
        ],
        "result": "Adds drama without muddying the entire vocal.",
    },
    "parallel_compression": {
        "name": "Parallel Compression",
        "method_a": {
            "steps": [
                "Duplicate voice channel",
                "Compress the copy BRUTALLY (10:1, crushed)",
                "Mix subtly with the original",
            ],
            "result": "Voice with body without losing dynamics.",
        },
        "method_b": {
            "steps": [
                "In Pro-C 2, use the 'Mix' knob at 50-70%",
            ],
            "result": "Same technique without duplicating the channel.",
        },
    },
    "volume_riding": {
        "name": "Volume Automation (Riding)",
        "steps": [
            "Right-click the voice fader > Create automation clip",
            "Draw volume MANUALLY for each phrase",
            "Raise parts that get lost, lower parts that scream",
            "Do this BEFORE compression = more natural mix",
        ],
        "notes": "Professional engineers ALWAYS do this.",
    },
    "false_chorus": {
        "name": "Fake Chorus from a Single Voice",
        "steps": [
            "Record the main voice",
            "Duplicate 3-4 times",
            "Each copy: change pitch (+3, +5, +7 semitones or per harmony)",
            "Pan: one at L30%, another R30%, another L60%, another R60%",
            "Lower volume of copies -8 to -12dB",
        ],
        "result": "Harmonized chorus from a single take.",
    },
    "mid_side_eq": {
        "name": "Mid-Side EQ on Voice",
        "plugin": "FabFilter Pro-Q 3",
        "steps": [
            "Activate 'Mid/Side' mode in Pro-Q 3",
            "Boost presence ONLY in Mid (center): +3dB at 3kHz",
        ],
        "result": (
            "Voice stands out in the center without affecting "
            "reverb/delay that is on the sides (Side)."
        ),
    },
    "beat_ducking": {
        "name": "Ducking the Beat Under the Voice",
        "steps": [
            "Place a compressor on the instrumental bus",
            "Sidechain from the voice",
            "Ratio: 2:1, subtle reduction -2 to -3dB",
        ],
        "result": (
            "When you sing, the beat lowers slightly automatically. "
            "Voice ALWAYS sounds clear without raising its volume."
        ),
    },
    "vocal_layering": {
        "name": "Vocal Texture Layering",
        "layers": {
            "main": "Clean, centered",
            "copy_1": "Heavy distortion, volume VERY low (-15dB), center",
            "copy_2": "Pitch -12 semitones (octave down), vol -12dB, center",
            "copy_3": "Whisper track (record whispering the same part), vol -10dB",
        },
        "result": "Voice sounds 'huge' and 'textured'.",
    },
    "mixer_template": {
        "name": "Save Voice Template",
        "steps": [
            "Right-click on the Mixer > Save mixer track state",
            "Instant load in future projects",
        ],
        "notes": "DO THIS. Saves hours of work on every song.",
    },
}


# ============================================================================
# VOCAL RECORDING TIPS
# ============================================================================

VOCAL_RECORDING_TIPS = {
    "importance": "Mixing does NOT fix a bad recording. 70% of the sound is defined here.",
    "microphone": {
        "ideal": "Large diaphragm condenser (AT2020, Rode NT1, AKG C214)",
        "alternative": "Dynamic (SM58, SM7B) - less detail but less background noise",
        "budget": "USB - fine to start but has its limits",
    },
    "distance": {
        "distance_cm": (15, 20),
        "reference": "A closed fist = reference distance",
        "pop_filter": "MANDATORY (eliminates plosives: P, B, T)",
        "angle": (
            "Slightly off-axis, do not sing DIRECTLY into the mic. "
            "Reduces plosives and sibilants."
        ),
    },
    "room": {
        "enemy_number_1": "Room reflections",
        "cheap_solution": "Record in a closet full of clothes (seriously, it works)",
        "diy": "Thick blankets on the walls behind you",
        "pro": "Acoustic panels - if you can buy them, buy them",
        "rule": "The more 'dead' the room, the cleaner the voice",
        "never": "NEVER record in an empty room or one with tiles",
    },
    "recording_level": {
        "input_gain_peak_dBFS": (-12, -6),
        "never_clip": "NEVER clip (exceed 0dB) when recording. That cannot be fixed.",
        "rule": "Better to record low and raise later than record hot and distort.",
    },
    "editing_before_effects": {
        "cut_silences": (
            "Edison > select > Delete (or lower volume). "
            "Do NOT remove ALL breaths, only the bothersome ones. "
            "Leaving some sounds more natural."
        ),
        "comping": (
            "If you recorded multiple takes, choose the best parts. "
            "Playlist > cut and paste the best phrases from each take. "
            "Crossfade at the cuts (5-20ms fade) to avoid clicks."
        ),
        "de_click": "Edison > Tools > De-click or iZotope RX De-click (the best).",
    },
    "gain_staging": {
        "target_dBFS": (-18, -12),
        "why": (
            "Plugins are designed to work at these levels. "
            "Too hot = distortion. Too quiet = internal noise rises."
        ),
        "how": [
            "1. Without plugins, play the voice",
            "2. Watch the mixer meter",
            "3. Adjust the fader until peaks reach -12dBFS",
            "4. NOW start adding plugins",
        ],
    },
}


# ============================================================================
# VOCAL LEVELS - Correct mix levels
# ============================================================================

VOCAL_LEVELS = {
    "principle": (
        "The voice should be the LOUDEST element in the mix, "
        "but not by much. It needs to 'sit' on top of the instrumental."
    ),
    "instrumental": {
        "fader_dB": (-6, -3),
        "notes": "This leaves room for the voice.",
    },
    "lead_vocal": {
        "fader_dB": "0dB or whatever it needs to be ON TOP",
        "relative_to_instrumental_dB": (2, 4),
        "vu_meter_peak_dBFS": (-6, -3),
    },
    "doubles_chorus": {
        "relative_to_lead_dB": (-6, -10),
        "role": "Accompany, not compete",
        "pan_pct": (30, 70),
        "pan_note": "L and R",
    },
    "adlibs": {
        "relative_to_lead_dB": (-8, -12),
        "role": "Seasoning, not the main dish",
        "more_reverb_delay": True,
    },
    "master": {
        "ceiling_dB": -0.3,
        "rule": "Never exceed -0.3dB (leave headroom for mastering)",
        "if_clipping": "Lower EVERYTHING proportionally, not just the voice",
    },
    "validation": {
        "test_1": "Listen at LOW volume. If you understand the lyrics, it is fine.",
        "test_2": "Listen on phone/cheap earbuds. If it gets lost, raise it.",
        "test_3": "Reference with professional songs of the same genre.",
        "test_4": (
            "Car test: if in the car with the window open you hear the voice "
            "above the beat, it is perfect."
        ),
    },
    "common_errors": {
        "too_high": "Sounds 'karaoke', disconnected from the beat",
        "too_low": "Gets lost, not understood, amateur",
        "equal_to_beat": "Frequency fight, nothing stands out",
    },
    "gain_staging_before_plugins": {
        "target_peak_dBFS": (-18, -12),
        "importance": (
            "Before inserting ANY plugin, adjust the voice volume "
            "to peak between -18 and -12dBFS in the mixer."
        ),
    },
}


# ============================================================================
# VOCAL CHECKLIST - 17-point final verification (including extras)
# ============================================================================

VOCAL_CHECKLIST: List[str] = [
    "1. Gain staging correct (-18 to -12dBFS before plugins)",
    "2. High pass at 80-100Hz (remove useless lows)",
    "3. Problem frequencies cleaned (sweep & destroy)",
    "4. Compression controlled (no more than -6dB reduction)",
    "5. Presence at 3-5kHz",
    "6. Air/brightness at 10-16kHz",
    "7. De-esser controlling sibilants",
    "8. Reverb and delay on SEND (not on insert)",
    "9. Reverb with damping (must not be brighter than the voice)",
    "10. Voice volume 2-4dB above the instrumental",
    "11. Limiter at the end, ceiling at -0.3dB",
    "12. Sounds good on headphones AND speakers",
    "13. Sounds good at low volume",
    "14. A/B comparison with professional reference of same genre",
    "15. Each plugin IMPROVES the sound (if not, remove it)",
    "16. Less is more: 3 well-placed plugins beat 15 random ones",
    "17. Processed voice sounds BETTER than unprocessed (A/B bypass all)",
]


# ============================================================================
# FREE PLUGINS - alternatives that rival paid ones
# ============================================================================

FREE_PLUGINS: List[Dict[str, str]] = [
    {
        "plugin": "TDR Nova",
        "function": "Dynamic EQ",
        "comparable_to": "FabFilter Pro-Q 3",
        "price": "Free",
    },
    {
        "plugin": "MAutoPitch",
        "function": "Autotune",
        "comparable_to": "Waves Tune",
        "price": "Free",
    },
    {
        "plugin": "OTT (Xfer)",
        "function": "Multiband compression",
        "comparable_to": "Everything (industry standard)",
        "price": "Free",
    },
    {
        "plugin": "Valhalla Supermassive",
        "function": "Reverb / Delay",
        "comparable_to": "Any professional reverb",
        "price": "Free",
    },
    {
        "plugin": "Analog Obsession plugins",
        "function": "Full suite",
        "comparable_to": "Waves, UAD",
        "price": "Free",
    },
    {
        "plugin": "Kilohearts Essentials",
        "function": "Various effects",
        "comparable_to": "Soundtoys",
        "price": "Free",
    },
    {
        "plugin": "Softube Saturation Knob",
        "function": "Saturation",
        "comparable_to": "Decapitator (light)",
        "price": "Free",
    },
    {
        "plugin": "Spitfish",
        "function": "De-esser",
        "comparable_to": "FabFilter Pro-DS",
        "price": "Free",
    },
    {
        "plugin": "TDR Kotelnikov",
        "function": "Compressor",
        "comparable_to": "Pro-C 2",
        "price": "Free",
    },
    {
        "plugin": "Youlean Loudness Meter",
        "function": "LUFS meter",
        "comparable_to": "Waves WLM",
        "price": "Free",
    },
]

# FL Studio native plugins always available
FL_NATIVE_PLUGINS = [
    "Parametric EQ 2",
    "Fruity Limiter",
    "Fruity Reeverb 2",
    "Fruity Delay 3",
    "Maximus",
    "Edison",
    "Pitcher",
    "Soundgoodizer",
    "Fruity Waveshaper",
]


# ============================================================================
# PLUGIN TIERS - Investment guide
# ============================================================================

PLUGIN_TIERS = {
    "beginner": {
        "budget": "$0",
        "label": "Beginner (zero budget)",
        "plugins": [
            "MAutoPitch (free) - autotune",
            "TDR Nova (free) - dynamic EQ",
            "OTT (free) - multiband compression",
            "Valhalla Supermassive (free) - reverb/delay",
            "Softube Saturation Knob (free) - saturation",
            "Spitfish (free) - de-esser",
            "FL Studio native plugins (Parametric EQ 2, Fruity Limiter, "
            "Fruity Reeverb 2, Fruity Delay 3, Maximus, Edison)",
        ],
    },
    "intermediate": {
        "budget": "$200-$300",
        "label": "Intermediate (invest here first)",
        "plugins": [
            "Waves Tune Real-Time (~$30 on sale)",
            "FabFilter Pro-Q 3 (~$180)",
            "Waves CLA-2A + RVox (~$30 each on sale)",
            "Valhalla VintageVerb (~$50)",
        ],
        "tip": "Waves runs up to 90% off sales constantly. Never pay full price for Waves.",
    },
    "professional": {
        "budget": "$2000+",
        "label": "Professional (complete setup)",
        "plugins": [
            "Antares Auto-Tune Pro",
            "FabFilter Pro-Q 3 + Pro-C 2 + Pro-DS + Pro-L 2",
            "Soundtoys Bundle (Decapitator + EchoBoy + everything)",
            "iZotope RX (for deep cleaning)",
            "SSL Native Channel Strip (console sound)",
        ],
    },
}

# Brand comparison overview
BRAND_COMPARISON = {
    "Waves": {
        "strength": "Professional quality, variety",
        "weakness": "Subscription model",
        "price_tier": "$$-$$$",
    },
    "iZotope": {
        "strength": "Artificial intelligence",
        "weakness": "Learning curve",
        "price_tier": "$$$",
    },
    "Cymatics": {
        "strength": "Ready presets, easy to use",
        "weakness": "Less fine control",
        "price_tier": "$-$$",
    },
    "FabFilter": {
        "strength": "Absolute cleanliness, visual",
        "weakness": "High price",
        "price_tier": "$$$",
    },
    "Soundtoys": {
        "strength": "Character and saturation",
        "weakness": "Specific to effects",
        "price_tier": "$$",
    },
    "Antares": {
        "strength": "Autotune industry standard",
        "weakness": "Only pitch correction",
        "price_tier": "$$$",
    },
    "SSL_Native": {
        "strength": "Real console sound",
        "weakness": "Less visual",
        "price_tier": "$$",
    },
    "Slate_Digital": {
        "strength": "All-in-one, subscription",
        "weakness": "Monthly dependency",
        "price_tier": "$$",
    },
}


# ============================================================================
# FL STUDIO KEYBOARD SHORTCUTS (vocal workflow)
# ============================================================================

FL_SHORTCUTS = {
    "Ctrl+L": "Link parameter to controller",
    "Ctrl+Shift+C": "Clone channel",
    "Alt+R": "Invert selection",
    "Ctrl+U": "Quick chop (in Edison)",
    "Ctrl+B": "Duplicate pattern",
    "Ctrl+Shift+M": "Mute/Unmute all channels",
    "F9": "Open Mixer",
    "F6": "Open Channel Rack",
    "F7": "Open Piano Roll",
    "Ctrl+T": "Create automation clip",
    "Ctrl+Shift+H": "Open Edison tools",
    "Alt+M": "Mute selected channel in mixer",
    "Ctrl+Shift+L": "Toggle Left/Right in mixer",
    "F10": "MIDI Settings",
    "Ctrl+Z": "Undo (works in mixer since FL 20.7+)",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_vocal_chain(style: str = "standard") -> str:
    """Return a formatted string describing the vocal chain for a given style.

    Args:
        style: One of "standard", "bright_trap", "yung_beef".

    Returns:
        Formatted multi-line string with the complete chain description.
    """
    if style == "standard":
        chain = VOCAL_CHAIN_STANDARD
        lines = [
            f"=== {chain['name']} ===",
            f"NOTE: {chain['important']}",
            "",
        ]
        for slot_num in sorted(chain["slots"]):
            slot = chain["slots"][slot_num]
            lines.append(f"SLOT {slot_num}: {slot['name']}")
            lines.append(f"  Purpose: {slot['purpose']}")
            if slot.get("optional"):
                lines.append("  (Optional but recommended)")
            if slot.get("most_important"):
                lines.append("  *** MOST IMPORTANT STEP for a clean voice ***")
            if slot.get("rule"):
                lines.append(f"  RULE: {slot['rule']}")
            # List plugin names
            if "plugins" in slot:
                plugins = slot["plugins"]
                if isinstance(plugins, dict):
                    for key, val in plugins.items():
                        if isinstance(val, dict) and "plugin" in val:
                            native_tag = " [NATIVE]" if val.get("native") else ""
                            free_tag = " [FREE]" if val.get("free") else ""
                            lines.append(f"    - {val['plugin']}{native_tag}{free_tag}")
            if "settings" in slot and isinstance(slot["settings"], dict):
                if "plugins" not in slot:
                    for key, val in slot["settings"].items():
                        if isinstance(val, dict):
                            plugin_name = val.get("plugin", key)
                            lines.append(f"    - {plugin_name}")
            lines.append("")
        return "\n".join(lines)

    elif style == "bright_trap":
        chain = VOCAL_CHAIN_BRIGHT_TRAP
        lines = [
            f"=== {chain['name']} ===",
            f"{chain['description']}",
            "",
            "EQ ({plugin}):".format(plugin=chain["eq"]["plugin"]),
        ]
        for band_num in sorted(chain["eq"]["bands"]):
            band = chain["eq"]["bands"][band_num]
            parts = [f"  Band {band_num}: {band['type']}"]
            if "freq_hz" in band:
                parts.append(f"{band['freq_hz']}Hz")
            if "gain_dB" in band:
                parts.append(f"{band['gain_dB']:+g}dB")
            if "Q" in band:
                parts.append(f"Q={band['Q']}")
            if "slope" in band:
                parts.append(band["slope"])
            parts.append(f"({band['purpose']})")
            lines.append(" | ".join(parts))

        comp = chain["compression"]
        lines.append("")
        lines.append(f"Compression ({comp['plugin']}):")
        lines.append(f"  Ratio: {comp['ratio']}, Attack: {comp['attack_ms']}ms, "
                     f"Release: {comp['release']}")
        lines.append(f"  Reduction: {comp['reduction_dB'][0]} to {comp['reduction_dB'][1]}dB")

        sat = chain["saturation"]
        lines.append("")
        lines.append(f"Saturation ({sat['plugin']}):")
        lines.append(f"  Drive: {sat['drive_pct'][0]}-{sat['drive_pct'][1]}%, "
                     f"Mix: {sat['mix_pct'][0]}-{sat['mix_pct'][1]}%")

        rev = chain["reverb"]
        lines.append("")
        lines.append("Reverb (SEND, not insert):")
        lines.append(f"  Type: {rev['type']}, Decay: {rev['decay_s']}s, "
                     f"Pre-delay: {rev['predelay_ms']}ms")
        lines.append(f"  Damping High: {rev['damping_high_hz']}Hz")
        lines.append(f"  {rev['damping_note']}")

        lines.append("")
        lines.append(f"Result: {chain['result']}")
        return "\n".join(lines)

    elif style == "yung_beef":
        chain = VOCAL_CHAIN_YUNG_BEEF
        lines = [
            f"=== {chain['name']} ===",
            f"{chain['description']}",
            "",
            "Autotune:",
            f"  Retune Speed: {chain['autotune']['retune_speed_ms'][0]}-"
            f"{chain['autotune']['retune_speed_ms'][1]}ms ({chain['autotune']['character']})",
            f"  Humanize: {chain['autotune']['humanize']}",
            f"  Flex Tune: {chain['autotune']['flex_tune']}",
            "",
            "Compression:",
            f"  Ratio: {chain['compression']['ratio']}",
            f"  Attack: {chain['compression']['attack_ms'][0]}-"
            f"{chain['compression']['attack_ms'][1]}ms",
            f"  Release: {chain['compression']['release_ms'][0]}-"
            f"{chain['compression']['release_ms'][1]}ms",
            "",
            "EQ:",
            f"  High Pass: {chain['eq']['high_pass_hz'][0]}-{chain['eq']['high_pass_hz'][1]}Hz",
            f"  Presence: {chain['eq']['presence_boost']['freq_hz'][0]}-"
            f"{chain['eq']['presence_boost']['freq_hz'][1]}Hz, "
            f"+{chain['eq']['presence_boost']['gain_dB']}dB",
            f"  Air: {chain['eq']['air_boost']['freq_hz'][0]}-"
            f"{chain['eq']['air_boost']['freq_hz'][1]}Hz, "
            f"+{chain['eq']['air_boost']['gain_dB']}dB",
            f"  Mud Cut: {chain['eq']['mud_cut']['freq_hz'][0]}-"
            f"{chain['eq']['mud_cut']['freq_hz'][1]}Hz, "
            f"{chain['eq']['mud_cut']['gain_dB']}dB",
            "",
            "Saturation:",
            f"  {chain['saturation']['type']}",
            "",
            "Reverb:",
            f"  Type: {', '.join(chain['reverb']['type'])}",
            f"  Decay: {chain['reverb']['decay_s'][0]}-{chain['reverb']['decay_s'][1]}s",
            f"  Mix: {chain['reverb']['mix_pct'][0]}-{chain['reverb']['mix_pct'][1]}%",
            f"  Pre-delay: {chain['reverb']['predelay_ms'][0]}-"
            f"{chain['reverb']['predelay_ms'][1]}ms",
            "",
            "Delay:",
            f"  Division: {', '.join(chain['delay']['division'])}",
            f"  Mix: {chain['delay']['mix_pct'][0]}-{chain['delay']['mix_pct'][1]}%",
            f"  Feedback: {chain['delay']['feedback_pct'][0]}-"
            f"{chain['delay']['feedback_pct'][1]}%",
        ]
        return "\n".join(lines)

    else:
        available = ["standard", "bright_trap", "yung_beef"]
        return f"Unknown style '{style}'. Available styles: {', '.join(available)}"


def get_vocal_tricks() -> str:
    """Return a formatted string listing all advanced vocal tricks.

    Returns:
        Formatted multi-line string with all tricks, steps, and results.
    """
    lines = ["=== Advanced Vocal Tricks ===", ""]
    for key, trick in VOCAL_TRICKS.items():
        lines.append(f"--- {trick['name']} ---")
        if "steps" in trick:
            for step in trick["steps"]:
                lines.append(f"  {step}")
        if "method_a" in trick:
            lines.append("  Method A:")
            for step in trick["method_a"]["steps"]:
                lines.append(f"    {step}")
            lines.append(f"    Result: {trick['method_a']['result']}")
            lines.append("  Method B:")
            for step in trick["method_b"]["steps"]:
                lines.append(f"    {step}")
            lines.append(f"    Result: {trick['method_b']['result']}")
        if "layers" in trick:
            for layer_name, desc in trick["layers"].items():
                lines.append(f"  {layer_name}: {desc}")
        if "result" in trick:
            lines.append(f"  Result: {trick['result']}")
        if "notes" in trick:
            lines.append(f"  Note: {trick['notes']}")
        lines.append("")
    return "\n".join(lines)


def get_vocal_checklist() -> str:
    """Return the formatted 17-point final verification checklist.

    Returns:
        Formatted multi-line string with all checklist items.
    """
    lines = ["=== Vocal Mix Final Checklist ===", ""]
    for item in VOCAL_CHECKLIST:
        lines.append(f"[ ] {item}")
    return "\n".join(lines)
