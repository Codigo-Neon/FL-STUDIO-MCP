"""Foundation constants for FL Studio MCP knowledge base."""

from enum import Enum


class Genre(str, Enum):
    BOOM_BAP = "boom_bap"
    TRAP = "trap"
    PHONK = "phonk"
    LOFI = "lofi"
    JAZZ_HIPHOP = "jazz_hiphop"
    REGGAETON = "reggaeton"
    UK_DRILL = "uk_drill"


class DrumPiece(str, Enum):
    KICK = "kick"
    SNARE = "snare"
    CLAP = "clap"
    CLOSED_HAT = "closed_hat"
    OPEN_HAT = "open_hat"
    PEDAL_HAT = "pedal_hat"
    RIDE = "ride"
    PERC = "perc"
    CRASH = "crash"
    SHAKER = "shaker"


# General MIDI drum note numbers
DRUM_MIDI_MAP = {
    DrumPiece.KICK: 36,
    DrumPiece.SNARE: 38,
    DrumPiece.CLAP: 39,
    DrumPiece.CLOSED_HAT: 42,
    DrumPiece.PEDAL_HAT: 44,
    DrumPiece.OPEN_HAT: 46,
    DrumPiece.RIDE: 51,
    DrumPiece.PERC: 47,
    DrumPiece.CRASH: 49,
    DrumPiece.SHAKER: 69,
}

# Note name to semitone offset (within octave)
NOTE_NAMES = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}

# Reverse mapping: semitone offset -> sharp name
SEMITONE_TO_NAME = {
    0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
    6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B",
}


def note_to_midi(note_name: str, octave: int = 4) -> int:
    """Convert note name + octave to MIDI number. C4 = 60."""
    return NOTE_NAMES[note_name] + (octave + 1) * 12


def midi_to_note(midi_num: int) -> str:
    """Convert MIDI number to note name with octave. 60 -> 'C4'."""
    octave = (midi_num // 12) - 1
    semitone = midi_num % 12
    return f"{SEMITONE_TO_NAME[semitone]}{octave}"


def transpose(midi_note: int, semitones: int) -> int:
    """Transpose a MIDI note by a number of semitones."""
    return max(0, min(127, midi_note + semitones))


# FL Studio MIDI command note mappings
NOTE_PLAY = 60
NOTE_STOP = 61
NOTE_RECORD = 62
NOTE_NEW_PROJECT = 63
NOTE_SET_BPM = 64
NOTE_NEW_PATTERN = 65
NOTE_SELECT_PATTERN = 66
NOTE_ADD_CHANNEL = 67
NOTE_NAME_CHANNEL = 68
NOTE_ADD_NOTE = 69
NOTE_ADD_TO_PLAYLIST = 70
NOTE_SET_PATTERN_LEN = 71
NOTE_CHANGE_TEMPO = 72

# CC mappings
CC_SELECT_CHANNEL = 100
CC_SELECT_STEP = 110
CC_TOGGLE_STEP = 111
CC_STEP_VELOCITY = 112
