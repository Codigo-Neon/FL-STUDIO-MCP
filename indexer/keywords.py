"""Keyword dictionaries for filename-based sample classification.

All keyword lists are lowercase. The parser normalizes input filenames
before matching. Keywords are matched against tokens (split on `_-. /\\`),
not substrings — this avoids "kick" matching inside "kickback" or "sticking".
"""

__all__ = [
    "SAMPLE_TYPE_KEYWORDS",
    "SUBTYPE_KEYWORDS",
    "GENRE_KEYWORDS",
    "MOOD_KEYWORDS",
    "LOOP_KEYWORDS",
    "ONESHOT_KEYWORDS",
    "AUDIO_EXTENSIONS",
    "SKIP_EXTENSIONS",
]


SAMPLE_TYPE_KEYWORDS: dict[str, list[str]] = {
    # Drums
    "kick": ["kick", "kik", "bd", "bassdrum", "bass_drum", "bombo", "tk"],
    "snare": ["snare", "sd", "sn", "snr", "caja"],
    "clap": ["clap", "claps", "clp", "palmas"],
    "hat_closed": ["closedhat", "closed_hat", "ch", "hihat_closed", "hh_closed"],
    "hat_open": ["openhat", "open_hat", "oh", "hihat_open", "hh_open"],
    "hat": ["hat", "hats", "hh", "hihat", "hi_hat", "hi-hat"],
    "cymbal": ["cymbal", "crash", "ride", "splash"],
    "tom": ["tom", "toms", "floor_tom", "rack_tom"],
    "perc": ["perc", "percussion", "shaker", "tambourine", "tamb",
             "rim", "rimshot", "cowbell", "conga", "bongo", "wood",
             "block", "click", "tick"],
    # Bass & melody
    "bass": ["bass", "808", "sub", "subbass", "bajo"],
    "lead": ["lead", "melody", "topline"],
    "pad": ["pad", "atmos", "ambient_pad"],
    "pluck": ["pluck", "plk"],
    "key": ["piano", "keys", "rhodes", "epiano", "ep"],
    # FX & vocals
    "fx": ["fx", "riser", "downer", "impact", "sweep", "swell",
           "transition", "uplift", "drop", "reverse", "rev",
           "whoosh"],
    "vocal": ["vocal", "vox", "vocals", "voice", "voz", "adlib", "ad_lib"],
}


SUBTYPE_KEYWORDS: dict[str, list[str]] = {
    "808": ["808"],
    "sub": ["sub", "subbass", "subby"],
    "growl": ["growl", "growly"],
    "reese": ["reese"],
    "wobble": ["wobble", "wob"],
    "layered": ["layered", "stacked", "stack"],
    "distorted": ["distorted", "distort", "dist", "saturated", "crunch"],
}


GENRE_KEYWORDS: dict[str, list[str]] = {
    "trap": ["trap"],
    "boom_bap": ["boombap", "boom_bap", "boom-bap", "boom bap",
                 "90s", "oldschool", "old_school", "old-school"],
    "phonk": ["phonk", "drift"],
    "hiphop": ["hiphop", "hip_hop", "hip-hop", "hip hop"],
    "drill": ["drill"],
    "house": ["house", "deephouse", "deep_house"],
    "techno": ["techno"],
    "dubstep": ["dubstep", "dub_step"],
    "dnb": ["dnb", "drum_and_bass", "drum_n_bass", "drumandbass"],
    "lofi": ["lofi", "lo-fi", "lo_fi"],
    "edm": ["edm"],
    "future_bass": ["future_bass", "futurebass"],
    "ambient": ["ambient"],
    "rnb": ["rnb", "r&b", "r_and_b"],
    "afrobeat": ["afro", "afrobeat", "afrobeats"],
    "reggaeton": ["reggaeton", "dembow"],
}


MOOD_KEYWORDS: dict[str, list[str]] = {
    "punchy": ["punchy", "punch", "snappy", "tight", "sharp"],
    "vintage": ["vintage", "retro", "old", "classic", "analog"],
    "dark": ["dark", "evil", "scary", "horror", "doom"],
    "warm": ["warm", "soft", "smooth", "vinyl"],
    "bright": ["bright", "shiny", "crisp", "clean"],
    "subby": ["deep", "low", "heavy", "booming"],
    "gritty": ["gritty", "raw", "dirty"],
    "wet": ["wet", "reverb", "verb", "spacey", "spaced", "ambient_fx"],
    "dry": ["dry"],
    "epic": ["epic", "huge", "massive", "cinematic"],
    "minimal": ["minimal", "thin", "sparse"],
}


LOOP_KEYWORDS: list[str] = ["loop", "loops", "groove", "rhythm", "rhy"]


ONESHOT_KEYWORDS: list[str] = ["one_shot", "oneshot", "one-shot", "shot",
                    "single", "one"]


AUDIO_EXTENSIONS: list[str] = [".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif"]

SKIP_EXTENSIONS: list[str] = [
    # FL Studio internals
    ".fst", ".fnv", ".flp", ".dat",
    # VST/Plugin presets
    ".fxp", ".fxb", ".nki", ".nkc", ".nkm", ".nks",
    # MIDI (handled by a different system)
    ".mid", ".midi",
    # Documentation
    ".txt", ".pdf", ".nfo", ".rtf", ".md", ".html",
    # Project files
    ".als", ".cwp", ".rpp", ".project",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp",
]
