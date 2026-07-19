# device_test.py
# name=Test Controller

import transport
import ui
import midi
import channels
import playlist
import patterns
import arrangement
import general
import device
import time
import sys

# Bridge bidireccional con el MCP vía SysEx MIDI.
# El script de FL Studio corre en un sub-interpreter sandboxeado que bloquea
# socket/threading/subprocess. La única forma de comunicación bidireccional
# es vía `device.midiOutSysex(bytes)` + el callback `OnSysEx(event)`.
try:
    from bridge import SysExServer, HandlerRegistry
    from bridge.fl_handlers import register_all
    from bridge.fl_adapter import LiveFLAdapter
    from bridge.peak_monitor import PeakMonitor
    from bridge.note_capture import NoteCapture
    from bridge.state_watcher import StateWatcher
    _BRIDGE_AVAILABLE = True
except ImportError as _bridge_err:
    print(f"[FL_MCP] Bridge no disponible: {_bridge_err}")
    _BRIDGE_AVAILABLE = False

_bridge_server = None
_bridge_registry = None
_peak_monitor = None
_note_capture = None
_state_watcher = None

# Global variables
running = True
command_history = []
current_pattern = 0
current_channel = 0
terminal_active = False

collecting_tempo_notes = False
tempo_note_array = []
NOTE_TEMPO_START = 72  # C4 starts tempo note collection
NOTE_TEMPO_END = 73    # C#4 ends collection and applies tempo change

# Mixer command protocol
NOTE_MIXER_START = 74  # Start mixer command
NOTE_MIXER_END = 75    # End mixer command and execute
collecting_mixer_data = False
mixer_data_array = []

# Mixer command types
MIXER_CMD_SET_VOLUME = 1
MIXER_CMD_SET_PAN = 2
MIXER_CMD_SET_ROUTE = 3
MIXER_CMD_SET_ROUTE_LEVEL = 4
MIXER_CMD_MUTE = 5
MIXER_CMD_SOLO = 6
MIXER_CMD_LINK_CHANNEL = 7
MIXER_CMD_SET_COLOR = 8
MIXER_CMD_ARM = 9
MIXER_CMD_SET_NAME = 10
MIXER_CMD_SET_EQ = 11

channel_to_edit = 0
step_to_edit = 0

def midi_notes_to_int(midi_notes):
    """
    Convert an array of MIDI note values (7 bits each) into a single integer
    
    This function takes a list of MIDI notes and combines them into a single
    integer value, with the first note being the most significant.
    
    Args:
        midi_notes (list): A list of MIDI note values (each 0-127)
        
    Returns:
        int: The combined integer value
    """
    result = 0
    for note in midi_notes:
        # Ensure each value is within MIDI range (0-127)
        note_value = min(127, max(0, note))
        # Shift left by 7 bits (MIDI values use 7 bits) and combine
        result = (result << 7) | note_value
    return result

def OnInit():
    """Called when the script is loaded by FL Studio"""
    global _bridge_server, _bridge_registry, _peak_monitor, _note_capture, _state_watcher
    print("FL Studio MCP Beat Builder initialized")
    print("Esperando comandos MIDI desde MCP...")

    if _BRIDGE_AVAILABLE:
        try:
            _adapter = LiveFLAdapter()
            _peak_monitor = PeakMonitor(_adapter)
            _note_capture = NoteCapture()
            _state_watcher = StateWatcher(_adapter)
            _bridge_registry = HandlerRegistry()
            register_all(_bridge_registry, _adapter, peak_monitor=_peak_monitor, note_capture=_note_capture)
            _bridge_server = SysExServer(device_module=device)
            print("[FL_MCP] SysEx bridge server registered (waiting for OnSysEx)")
        except Exception as exc:
            print(f"[FL_MCP] Falló el arranque del bridge: {exc}")
            _bridge_server = None
            _bridge_registry = None
            _peak_monitor = None
            _note_capture = None
            _state_watcher = None

    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    global _bridge_server, _bridge_registry, _peak_monitor, _note_capture, _state_watcher
    _bridge_server = None
    _bridge_registry = None
    _peak_monitor = None
    _note_capture = None
    _state_watcher = None
    global running
    running = False  # Signal the terminal thread to exit
    print("FL Studio Terminal Beat Builder deinitialized")
    return

def OnRefresh(flags):
    """Called when FL Studio's state changes or when a refresh is needed"""
    # Update terminal with current state if needed
    return

def OnMidiIn(event):
    """Called whenever the device sends a MIDI message to FL Studio.
    SysEx is handled by OnSysEx — we leave this as a no-op pass-through."""
    event.handled = False

def change_tempo(bpm):
    """
    Change the tempo in FL Studio to the specified BPM value
    
    Args:
        bpm (float): The desired tempo in beats per minute
    """
    # FL Studio stores tempo as BPM * 1000
    tempo_value = int(bpm * 1000)
    
    # Use processRECEvent to set the tempo
    # REC_Tempo is the event ID for tempo
    # REC_Control | REC_UpdateControl flags ensure the value is set and the UI updates
    general.processRECEvent(
        midi.REC_Tempo,
        tempo_value,
        midi.REC_Control | midi.REC_UpdateControl
    )

def process_received_midi(note, velocity):

    global current_note, current_velocity, current_length, current_position
    global decimal_state, decimal_value, decimal_target
    
    # Special MIDI commands
    DECIMAL_MARKER = 100   # Indicates next value is a decimal part
    LENGTH_MARKER = 101    # Next value affects length
    POSITION_MARKER = 102  # Next value affects position
    
    # Process based on message type
    if note == DECIMAL_MARKER:
        # Next value will be a decimal
        decimal_state = 1
        return False
        
    elif note == LENGTH_MARKER:
        # Next value affects length
        decimal_target = "length"
        decimal_state = 0
        decimal_value = 0
        return False
        
    elif note == POSITION_MARKER:
        # Next value affects position
        decimal_target = "position"
        decimal_state = 0
        decimal_value = 0
        return False
        
    elif decimal_state == 1:
        # This is a decimal part value
        decimal_value = note / 10.0  # Convert to decimal (0-9 becomes 0.0-0.9)
        
        # Apply to the correct parameter
        if decimal_target == "length":
            current_length = (current_length or 0) + decimal_value
            print(f"Set length decimal: {current_length:.2f}")
        elif decimal_target == "position":
            current_position = (current_position or 0) + decimal_value
            print(f"Set position decimal: {current_position:.2f}")
            
        decimal_state = 0
        return False
        
    elif decimal_target is not None:
        # This is a whole number part for a specific parameter
        if decimal_target == "length":
            current_length = float(note)
            print(f"Set length whole: {current_length:.2f}")
        elif decimal_target == "position":
            current_position = float(note)
            print(f"Set position whole: {current_position:.2f}")
        return False
        
    else:
        # This is a note value and velocity
        # Check if we have a complete previous note to add
        add_note = (current_note is not None and 
                   current_velocity is not None and 
                   current_length is not None and 
                   current_position is not None)
        
        # Start a new note
        current_note = note
        current_velocity = velocity
        # Use default values if not specified
        if current_length is None:
            current_length = 1.0
        if current_position is None:
            current_position = 0.0
        print(f"Started new note: {current_note}, velocity: {current_velocity}")
        
        return add_note


def execute_mixer_command(data):
    """Execute a mixer command from the collected MIDI data array.

    Protocol: [command_type, param1, param2, ...]
    """
    if not data:
        print("Empty mixer command data")
        return

    cmd = data[0]
    params = data[1:]

    try:
        import mixer as mx

        if cmd == MIXER_CMD_SET_VOLUME and len(params) >= 2:
            # params: [track_index, volume_0_127]
            track = params[0]
            volume = params[1] / 127.0  # Convert 0-127 to 0.0-1.0
            mx.setTrackVolume(track, volume)
            print(f"Mixer: Track {track} volume set to {volume:.2f} ({params[1]}/127)")

        elif cmd == MIXER_CMD_SET_PAN and len(params) >= 2:
            # params: [track_index, pan_0_127] where 64=center
            track = params[0]
            pan = (params[1] - 64) / 64.0  # Convert 0-127 to -1.0 to 1.0
            mx.setTrackPan(track, pan)
            print(f"Mixer: Track {track} pan set to {pan:.2f}")

        elif cmd == MIXER_CMD_SET_ROUTE and len(params) >= 3:
            # params: [src_track, dest_track, enable(0/1)]
            src = params[0]
            dest = params[1]
            enable = params[2] > 0
            mx.setRouteTo(src, dest, enable)
            mx.afterRoutingChanged()
            state = "enabled" if enable else "disabled"
            print(f"Mixer: Route from track {src} to track {dest} {state}")

        elif cmd == MIXER_CMD_SET_ROUTE_LEVEL and len(params) >= 3:
            # params: [src_track, dest_track, level_0_127]
            src = params[0]
            dest = params[1]
            level = params[2] / 127.0
            mx.setRouteToLevel(src, dest, level)
            print(f"Mixer: Route level {src} -> {dest} set to {level:.2f}")

        elif cmd == MIXER_CMD_MUTE and len(params) >= 1:
            # params: [track_index] (toggle) or [track_index, state]
            track = params[0]
            if len(params) >= 2:
                # Specific state: 0=unmute, 1=mute
                current = mx.isTrackMuted(track)
                if (params[1] == 1 and not current) or (params[1] == 0 and current):
                    mx.muteTrack(track)
            else:
                mx.muteTrack(track)  # Toggle
            state = "muted" if mx.isTrackMuted(track) else "unmuted"
            print(f"Mixer: Track {track} {state}")

        elif cmd == MIXER_CMD_SOLO and len(params) >= 1:
            # params: [track_index]
            track = params[0]
            mx.soloTrack(track)
            print(f"Mixer: Track {track} solo toggled")

        elif cmd == MIXER_CMD_LINK_CHANNEL and len(params) >= 2:
            # params: [channel_index, track_index]
            channel = params[0]
            track = params[1]
            mx.linkChannelToTrack(channel, track)
            print(f"Mixer: Channel {channel} linked to track {track}")

        elif cmd == MIXER_CMD_SET_COLOR and len(params) >= 4:
            # params: [track_index, r, g, b] (each 0-127, scaled to 0-255)
            track = params[0]
            r = min(255, params[1] * 2)
            g = min(255, params[2] * 2)
            b = min(255, params[3] * 2)
            # FL Studio uses 0x--BBGGRR format
            color = (b << 16) | (g << 8) | r
            mx.setTrackColor(track, color)
            print(f"Mixer: Track {track} color set to RGB({r},{g},{b})")

        elif cmd == MIXER_CMD_ARM and len(params) >= 1:
            # params: [track_index]
            track = params[0]
            mx.armTrack(track)
            print(f"Mixer: Track {track} arm toggled")

        elif cmd == MIXER_CMD_SET_NAME and len(params) >= 2:
            # params: [track_index, char1, char2, char3, ...]
            track = params[0]
            chars = params[1:]
            name = "".join(chr(c) for c in chars if 32 <= c <= 126)
            mx.setTrackName(track, name)
            print(f"Mixer: Track {track} renamed to '{name}'")

        elif cmd == MIXER_CMD_SET_EQ and len(params) >= 4:
            # params: [track_index, band(0-2), freq_0_127, gain_0_127]
            track = params[0]
            band = params[1]
            freq = params[2] / 127.0
            gain = params[3] / 127.0
            mx.setEqFrequency(track, band, freq)
            mx.setEqGain(track, band, gain)
            print(f"Mixer: Track {track} EQ band {band}: freq={freq:.2f}, gain={gain:.2f}")

        else:
            print(f"Mixer: Unknown command {cmd} with params {params}")

    except Exception as e:
        print(f"Mixer command error: {e}")


def OnMidiMsg(event, timestamp=0):
    """Called when a processed MIDI message is received.

    Handles three protocols:
    - Melody: Note 0 (start) → count → 6 values per note → Note 127 (end)
    - Tempo:  Note 72 (start) → BPM bytes → Note 73 (end)
    - Mixer:  Note 74 (start) → command + params → Note 75 (end)
    - SysEx:  F0 ... F7 (bridge bidireccional)
    """

    # SysEx is handled by OnSysEx — skip it here.
    if getattr(event, 'sysex', None):
        return

    global receiving_mode, collecting_tempo_notes, tempo_note_array
    global collecting_mixer_data, mixer_data_array
    global midi_notes_array

    if 'receiving_mode' not in globals():
        global receiving_mode
        receiving_mode = False

    if 'note_count' not in globals():
        global note_count
        note_count = 0

    if 'values_received' not in globals():
        global values_received
        values_received = 0

    if 'midi_data' not in globals():
        global midi_data
        midi_data = []

    if 'midi_notes_array' not in globals():
        global midi_notes_array
        midi_notes_array = []

    # Only process Note On messages with velocity > 0
    if not (event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16 and event.data2 > 0):
        event.handled = False
        return

    note_value = event.data1

    # ================================================================
    # STATE: Collecting melody notes
    # ================================================================
    if receiving_mode:
        # Second message is the note count
        if note_count == 0:
            note_count = note_value
            print(f"Expecting {note_count} notes")
            event.handled = True
            return

        # All subsequent messages are MIDI values (6 per note)
        midi_data.append(note_value)
        values_received += 1

        # Process completed notes (every 6 values)
        if len(midi_data) >= 6 and len(midi_data) % 6 == 0:
            i = len(midi_data) - 6
            note = midi_data[i]
            velocity = midi_data[i+1]
            length_whole = midi_data[i+2]
            length_decimal = midi_data[i+3]
            position_whole = midi_data[i+4]
            position_decimal = midi_data[i+5]

            length = length_whole + (length_decimal / 10.0)
            position = position_whole + (position_decimal / 10.0)

            midi_notes_array.append((note, velocity, length, position))
            print(f"Added note: note={note}, vel={velocity}, len={length:.1f}, pos={position:.1f} ({len(midi_notes_array)}/{note_count})")

            if len(midi_notes_array) >= note_count or note_value == 127:
                print(f"Received all {len(midi_notes_array)} notes")
                receiving_mode = False

                if midi_notes_array:
                    record_notes_batch(midi_notes_array)

                event.handled = True
                return

        event.handled = True
        return

    # ================================================================
    # STATE: Collecting tempo data
    # ================================================================
    if collecting_tempo_notes:
        if note_value == NOTE_TEMPO_END:
            if tempo_note_array:
                bpm = change_tempo_from_notes(tempo_note_array)
                print(f"Tempo changed to {bpm} BPM from notes: {tempo_note_array}")
            collecting_tempo_notes = False
            tempo_note_array = []
            event.handled = True
            return
        else:
            tempo_note_array.append(note_value)
            print(f"Tempo data: added {note_value}, array: {tempo_note_array}")
            event.handled = True
            return

    # ================================================================
    # STATE: Collecting mixer command data
    # ================================================================
    if collecting_mixer_data:
        if note_value == NOTE_MIXER_END:
            print(f"Executing mixer command: {mixer_data_array}")
            execute_mixer_command(mixer_data_array)
            collecting_mixer_data = False
            mixer_data_array = []
            event.handled = True
            return
        else:
            mixer_data_array.append(note_value)
            print(f"Mixer data: added {note_value}, array: {mixer_data_array}")
            event.handled = True
            return

    # ================================================================
    # IDLE STATE: Check for command start markers
    # ================================================================

    # PROTOCOL COMMANDS: only trigger when velocity == 1 (to avoid conflict with musical notes)
    is_command = (event.data2 == 1)

    if is_command:
        # Note 0 → Start melody receiving
        if note_value == 0:
            receiving_mode = True
            midi_data = []
            note_count = 0
            values_received = 0
            midi_notes_array = []
            print("Started receiving melody notes")
            event.handled = True
            return

        # Note 72 → Start tempo change
        if note_value == NOTE_TEMPO_START:
            collecting_tempo_notes = True
            tempo_note_array = []
            print("Started collecting tempo data")
            event.handled = True
            return

        # Note 74 → Start mixer command
        if note_value == NOTE_MIXER_START:
            collecting_mixer_data = True
            mixer_data_array = []
            print("Started collecting mixer command")
            event.handled = True
            return

        # Note 76 → Start recording + playback
        if note_value == 76:
            # Reset any stuck states
            collecting_tempo_notes = False
            collecting_mixer_data = False
            receiving_mode = False
            # Make sure we're stopped first
            if transport.isPlaying():
                transport.stop()
            # Go to beginning
            transport.setSongPos(0, 2)
            # Enable recording if not already
            if not transport.isRecording():
                transport.record()
            # Start playback (recording will capture incoming MIDI)
            transport.start()
            print("Recording started - waiting for MIDI notes...")
            event.handled = True
            return

        # Note 77 → Stop recording + playback + auto-quantize
        if note_value == 77:
            transport.stop()
            if transport.isRecording():
                transport.record()  # Toggle off recording
            # Auto-quantize to snap notes to grid
            channel = channels.selectedChannel()
            channels.quickQuantize(channel)
            print(f"Recording stopped - channel {channel} quantized")
            transport.setSongPos(0, 2)
            event.handled = True
            return

    # Any other note (or velocity > 1): let FL Studio handle it (play/record normally)
    event.handled = False

# Make sure your commit_pattern_changes function is defined:
def commit_pattern_changes(pattern_num=None):
    """Force FL Studio to update the pattern data visually"""
    if pattern_num is None:
        pattern_num = patterns.patternNumber()
    
    # Force FL Studio to redraw and commit changes
    ui.crDisplayRect()
    
    # Force channel rack to update
    ui.setFocused(midi.widChannelRack)
    
    # Update playlist if needed
    playlist.refresh()
def OnTransport(isPlaying):
    """Called when the transport state changes (play/stop)"""
    print(f"Transport state changed: {'Playing' if isPlaying else 'Stopped'}")
    return

def OnTempoChange(tempo):
    """Called when the tempo changes"""
    print(f"Tempo changed to: {tempo} BPM")
    return


# # Terminal interface functions
# def start_terminal_thread():
#     """Start a thread to handle terminal input"""
#     global terminal_active
#     if not terminal_active:
#         terminal_active = True
#         thread = threading.Thread(target=terminal_loop)
#         thread.daemon = True
#         thread.start()

# def terminal_loop():
#     """Main terminal input loop"""
#     global running, terminal_active
    
#     print("\n===== FL STUDIO TERMINAL BEAT BUILDER =====")
#     print("Enter commands to build your beat (type 'help' for commands)")
    
#     while running:
#         try:
#             command = input("\nFLBEAT> ")
#             command_history.append(command)
#             process_command(command)
#         except Exception as e:
#             print(f"Error processing command: {e}")
    
#     terminal_active = False

def record_note(note=60, velocity=100, length_beats=1.0, position_beats=0.0, quantize=True):
    """
    Records a single note to the piano roll synced with project tempo
    
    Args:
        note (int): MIDI note number (60 = middle C)
        velocity (int): Note velocity (0-127)
        length_beats (float): Length of note in beats (1.0 = quarter note)
        position_beats (float): Position to place note in beats from start
        quantize (bool): Whether to quantize the recording afterward
    """
    # Make sure transport is stopped first
    if transport.isPlaying():
        transport.stop()
    
    # Get the current channel
    channel = channels.selectedChannel()
    
    # Get the project's PPQ (pulses per quarter note)
    ppq = general.getRecPPQ()
    
    # Calculate ticks based on beats
    length_ticks = int(length_beats * ppq)
    position_ticks = int(position_beats * ppq)
    
    # Set playback position
    transport.setSongPos(position_ticks, 2)  # 2 = SONGLENGTH_ABSTICKS
    
    # Toggle recording mode if needed
    if not transport.isRecording():
        transport.record()
    
    print(f"Recording note {note} to channel {channel}")
    print(f"Position: {position_beats} beats, Length: {length_beats} beats")
    
    # Calculate the exact tick positions where we need to place note and note-off
    start_tick = position_ticks
    end_tick = start_tick + length_ticks
    
    # Start playback to begin recording
    transport.start()
    
    # Record the note at the exact start position
    channels.midiNoteOn(channel, note, velocity)
    
    # Get the current tempo (BPM)
    tempo = 120  # Default fallback
    
    # Try to get actual tempo from the project
    try:
        import mixer
        tempo = mixer.getCurrentTempo()
        tempo = tempo/1000
        print(f"Using project tempo: {tempo} BPM")
    except (ImportError, AttributeError):
        print("Using default tempo: 120 BPM")
    
    # Calculate the time to wait in seconds
    seconds_to_wait = (length_beats * 60) / tempo
    
    print(f"Waiting for {seconds_to_wait:.2f} seconds...")
    
    # Wait the calculated time
    time.sleep(seconds_to_wait)
    
    # Send note-off event
    channels.midiNoteOn(channel, note, 0)
    
    # Stop playback
    transport.stop()
    
    # Exit recording mode if it was active
    if transport.isRecording():
        transport.record()
    
    # Quantize if requested
    if quantize:
        channels.quickQuantize(channel)
        print("Recording quantized")
    
    print(f"Note {note} recorded to piano roll")
    
    # Return to beginning
    transport.setSongPos(0, 2)

def rec_hihat_pattern():
    """
    Records a predefined hi-hat pattern to the piano roll using record_notes_batch
    
    This creates a 4-bar hi-hat pattern with variations in velocity, rhythm, and types of hats
    """
    # Stop playback and rewind to beginning first
    if transport.isPlaying():
        transport.stop()
    
    transport.setSongPos(0, 2)  # Go to the beginning
    
    print("Recording hi-hat pattern...")
    
    # Common hi-hat MIDI notes:
    # 42 = Closed hi-hat
    # 44 = Pedal hi-hat
    # 46 = Open hi-hat
    
    # Define the pattern as a list of notes
    # Each tuple contains (note, velocity, length_beats, position_beats)
    hihat_pattern = [
        # BAR 1 - Basic pattern
        (42, 90, 0.1, 0.0),     # Closed hat on beat 1
        (42, 65, 0.1, 0.5),     # Closed hat on off-beat
        (42, 90, 0.1, 1.0),     # Closed hat on beat 2
        (42, 65, 0.1, 1.5),     # Closed hat on off-beat
        (42, 90, 0.1, 2.0),     # Closed hat on beat 3
        (42, 65, 0.1, 2.5),     # Closed hat on off-beat
        (42, 90, 0.1, 3.0),     # Closed hat on beat 4
        (42, 65, 0.1, 3.5),     # Closed hat on off-beat
        
        # BAR 2 - Adding 16th notes
        (42, 90, 0.1, 4.0),     # Closed hat on beat 1
        (42, 60, 0.1, 4.25),    # Closed hat on 16th
        (42, 70, 0.1, 4.5),     # Closed hat on off-beat
        (42, 60, 0.1, 4.75),    # Closed hat on 16th
        (42, 90, 0.1, 5.0),     # Closed hat on beat 2
        (42, 60, 0.1, 5.25),    # Closed hat on 16th
        (42, 70, 0.1, 5.5),     # Closed hat on off-beat
        (42, 60, 0.1, 5.75),    # Closed hat on 16th
        (42, 90, 0.1, 6.0),     # Closed hat on beat 3
        (42, 60, 0.1, 6.25),    # Closed hat on 16th
        (42, 70, 0.1, 6.5),     # Closed hat on off-beat
        (42, 60, 0.1, 6.75),    # Closed hat on 16th
        (42, 90, 0.1, 7.0),     # Closed hat on beat 4
        (46, 80, 0.2, 7.5),     # Open hat on off-beat
        
        # BAR 3 - Mixing closed and open hats
        (42, 100, 0.1, 8.0),    # Closed hat on beat 1
        (42, 70, 0.1, 8.5),     # Closed hat on off-beat
        (46, 85, 0.2, 9.0),     # Open hat on beat 2
        (42, 70, 0.1, 9.5),     # Closed hat on off-beat
        (42, 95, 0.1, 10.0),    # Closed hat on beat 3
        (42, 70, 0.1, 10.5),    # Closed hat on off-beat
        (46, 85, 0.2, 11.0),    # Open hat on beat 4
        
        # Triplet fill at the end of bar 3
        (42, 80, 0.08, 11.33),  # Closed hat - triplet 1
        (42, 85, 0.08, 11.66),  # Closed hat - triplet 2
        (42, 90, 0.08, 11.99),  # Closed hat - triplet 3
        
        # BAR 4 - Complex pattern with pedal hats
        (42, 100, 0.1, 12.0),   # Closed hat on beat 1
        (44, 75, 0.1, 12.25),   # Pedal hat on 16th
        (42, 80, 0.1, 12.5),    # Closed hat on off-beat
        (44, 70, 0.1, 12.75),   # Pedal hat on 16th
        (42, 90, 0.1, 13.0),    # Closed hat on beat 2
        (46, 85, 0.3, 13.5),    # Open hat on off-beat
        
        # Beat 3-4: Building intensity
        (42, 95, 0.1, 14.0),    # Closed hat on beat 3
        (42, 75, 0.1, 14.25),   # Closed hat on 16th
        (42, 85, 0.1, 14.5),    # Closed hat on off-beat
        (42, 80, 0.1, 14.75),   # Closed hat on 16th
        
        # Final fill
        (42, 85, 0.05, 15.0),   # Closed hat - 32nd note 1
        (42, 90, 0.05, 15.125), # Closed hat - 32nd note 2
        (42, 95, 0.05, 15.25),  # Closed hat - 32nd note 3
        (42, 100, 0.05, 15.375),# Closed hat - 32nd note 4
        (42, 105, 0.05, 15.5),  # Closed hat - 32nd note 5
        (42, 110, 0.05, 15.625),# Closed hat - 32nd note 6
        (42, 115, 0.05, 15.75), # Closed hat - 32nd note 7
        (46, 120, 0.25, 15.875),# Open hat - final accent
    ]
    
    # Record the hi-hat pattern using the batch recording function
    record_notes_batch(hihat_pattern)
    
    print("Hi-hat pattern recording complete!")
    
    # Quantize the hi-hat pattern
    channel = channels.selectedChannel()
    channels.quickQuantize(channel)
    
    # Return to beginning
    transport.setSongPos(0, 2)

def record_notes_batch(notes_array):
    """
    Records a batch of notes to FL Studio using a single play+record pass.
    Sends note on/off events in real-time from within FL Studio (no MIDI latency).
    Works in both Pattern and Song mode.

    Args:
        notes_array: List of tuples, each containing (note, velocity, length_beats, position_beats)
    """
    if not notes_array:
        print("No notes to record")
        return

    channel = channels.selectedChannel()

    # Get tempo
    try:
        import mixer
        tempo = mixer.getCurrentTempo() / 1000
    except (ImportError, AttributeError):
        tempo = 120

    seconds_per_beat = 60.0 / tempo
    print(f"Recording {len(notes_array)} notes at {tempo} BPM (1 beat = {seconds_per_beat:.3f}s)")

    # Build event timeline (note_on and note_off sorted by time)
    events = []
    for note, velocity, length, position in notes_array:
        t_on = position * seconds_per_beat
        t_off = (position + length) * seconds_per_beat
        events.append((t_on, 'on', note, velocity))
        events.append((t_off, 'off', note, 0))
    events.sort(key=lambda e: (e[0], 0 if e[1] == 'off' else 1))

    # Calculate total duration
    total_time = max(e[0] for e in events) + 0.3

    # Stop transport and go to beginning
    if transport.isPlaying():
        transport.stop()
    transport.setSongPos(0, 2)
    time.sleep(0.1)

    # Enable recording
    if not transport.isRecording():
        transport.record()

    # Start playback (recording captures from within FL - no Wine latency)
    transport.start()
    print("Recording started - sending notes in real-time...")

    # Send all note events timed from within FL Studio
    start_time = time.time()
    for event_time, event_type, note, vel in events:
        wait = event_time - (time.time() - start_time)
        if wait > 0:
            time.sleep(wait)
        if event_type == 'on':
            channels.midiNoteOn(channel, note, vel)
        else:
            channels.midiNoteOn(channel, note, 0)

    # Wait for last note to finish
    time.sleep(0.3)

    # Stop recording
    transport.stop()
    if transport.isRecording():
        transport.record()

    # Quantize to fix any tiny timing drift
    channels.quickQuantize(channel)

    transport.setSongPos(0, 2)
    print(f"All {len(notes_array)} notes recorded and quantized!")



def rec_melody():
    """
    Records a predefined melody to the piano roll by calling record_notes_batch
    
    The melody is a robust 4-bar composition with melody notes and chord accompaniment
    """
    # Stop playback and rewind to beginning first
    if transport.isPlaying():
        transport.stop()
    
    transport.setSongPos(0, 2)  # Go to the beginning
    
    print("Recording melody...")
    
    # Define the melody as a list of notes
    # Each tuple contains (note, velocity, length_beats, position_beats)
    melody = [
        # BAR 1
        # Beat 1: C major chord
        (60, 100, 1.0, 0.0),    # C4 - root note
        (64, 85, 1.0, 0.0),     # E4 - chord tone
        (67, 80, 1.0, 0.0),     # G4 - chord tone
        
        # Beat 1.5: Melody note
        (72, 110, 0.5, 0.5),    # C5 - melody
        
        # Beat 2: G7 chord
        (55, 90, 1.0, 1.0),     # G3 - bass note
        (59, 75, 1.0, 1.0),     # B3 - chord tone
        (62, 75, 1.0, 1.0),     # D4 - chord tone
        (65, 75, 1.0, 1.0),     # F4 - chord tone
        
        # Beat 2.5-3: Melody phrase
        (71, 105, 0.25, 1.5),   # B4 - melody
        (69, 95, 0.25, 1.75),   # A4 - melody
        (67, 90, 0.5, 2.0),     # G4 - melody
        
        # Beat 3: C major chord
        (48, 95, 1.0, 2.0),     # C3 - bass note
        (64, 75, 1.0, 2.0),     # E4 - chord tone
        (67, 75, 1.0, 2.0),     # G4 - chord tone
        
        # Beat 4: Melody fill
        (64, 100, 0.5, 3.0),    # E4 - melody
        (65, 90, 0.25, 3.5),    # F4 - melody
        (67, 95, 0.25, 3.75),   # G4 - melody
        
        # BAR 2
        # Beat 1: Am chord
        (57, 95, 1.0, 4.0),     # A3 - bass note
        (60, 80, 1.0, 4.0),     # C4 - chord tone
        (64, 80, 1.0, 4.0),     # E4 - chord tone
        
        # Beat 1-2: Melody note
        (69, 110, 0.75, 4.0),   # A4 - melody
        (67, 90, 0.25, 4.75),   # G4 - melody
        
        # Beat 2: F major chord
        (53, 90, 1.0, 5.0),     # F3 - bass note
        (57, 75, 1.0, 5.0),     # A3 - chord tone
        (60, 75, 1.0, 5.0),     # C4 - chord tone
        
        # Beat 2.5-3: Melody
        (65, 100, 0.5, 5.5),    # F4 - melody
        (64, 90, 0.5, 6.0),     # E4 - melody
        
        # Beat 3: G7 chord
        (55, 95, 1.0, 6.0),     # G3 - bass note
        (59, 80, 1.0, 6.0),     # B3 - chord tone
        (62, 80, 1.0, 6.0),     # D4 - chord tone
        
        # Beat 3.5-4: Melody fill
        (62, 100, 0.25, 6.5),   # D4 - melody
        (64, 95, 0.25, 6.75),   # E4 - melody
        (65, 90, 0.25, 7.0),    # F4 - melody
        (67, 105, 0.75, 7.25),  # G4 - melody
        
        # BAR 3
        # Beat 1: C major chord
        (48, 100, 1.0, 8.0),    # C3 - bass note
        (60, 85, 1.0, 8.0),     # C4 - chord tone
        (64, 85, 1.0, 8.0),     # E4 - chord tone
        (67, 85, 1.0, 8.0),     # G4 - chord tone
        
        # Beat 1-2: Melody
        (72, 110, 1.0, 8.0),    # C5 - melody
        
        # Beat 2: Em chord
        (52, 90, 1.0, 9.0),     # E3 - bass note
        (59, 75, 1.0, 9.0),     # B3 - chord tone
        (64, 75, 1.0, 9.0),     # E4 - chord tone
        
        # Beat 2.5-3.5: Melody run
        (71, 105, 0.25, 9.5),   # B4 - melody
        (72, 100, 0.25, 9.75),  # C5 - melody
        (74, 110, 0.5, 10.0),   # D5 - melody
        (76, 115, 0.5, 10.5),   # E5 - melody
        
        # Beat 3: Am chord
        (57, 95, 1.0, 10.0),    # A3 - bass note
        (60, 80, 1.0, 10.0),    # C4 - chord tone
        (64, 80, 1.0, 10.0),    # E4 - chord tone
        
        # Beat 4: Descending run
        (74, 100, 0.25, 11.0),  # D5 - melody
        (72, 95, 0.25, 11.25),  # C5 - melody
        (71, 90, 0.25, 11.5),   # B4 - melody
        (69, 85, 0.25, 11.75),  # A4 - melody
        
        # BAR 4
        # Beat 1: F major chord
        (53, 95, 1.0, 12.0),    # F3 - bass note
        (60, 80, 1.0, 12.0),    # C4 - chord tone
        (65, 80, 1.0, 12.0),    # F4 - chord tone
        
        # Beat 1-2: Melody
        (67, 100, 1.0, 12.0),   # G4 - melody
        
        # Beat 2: G7 chord
        (55, 90, 1.0, 13.0),    # G3 - bass note
        (59, 75, 1.0, 13.0),    # B3 - chord tone
        (62, 75, 1.0, 13.0),    # D4 - chord tone
        
        # Beat 2-3: Melody
        (65, 95, 0.5, 13.0),    # F4 - melody
        (64, 90, 0.5, 13.5),    # E4 - melody
        
        # Beat 3-4: Final C major chord
        (48, 110, 2.0, 14.0),   # C3 - bass note
        (60, 95, 2.0, 14.0),    # C4 - chord tone
        (64, 95, 2.0, 14.0),    # E4 - chord tone
        (67, 95, 2.0, 14.0),    # G4 - chord tone
        
        # Final melody note
        (72, 120, 2.0, 14.0),   # C5 - melody final note
    ]
    
    # Record the melody using the batch recording function
    record_notes_batch(melody)
    
    print("Melody recording complete!")
    
def change_tempo_from_notes(note_array):
    """
    Change the tempo in FL Studio based on an array of MIDI notes
    
    This function converts an array of MIDI notes to a single integer value
    and uses that value as the new tempo.
    
    Args:
        note_array (list): A list of MIDI note values (each 0-127)
    """
    # Convert note array to integer
    bpm_value = midi_notes_to_int(note_array)
    
    # Limit to a reasonable BPM range
    if bpm_value < 20:
        bpm_value = 20  # Minimum reasonable tempo
    elif bpm_value > 999:
        bpm_value = 999  # Maximum reasonable tempo
    
    # Change the tempo
    print(f"Changing tempo to {bpm_value} BPM from note array {note_array}")
    change_tempo(bpm_value)
    
    return bpm_value

def OnIdle():
    """Called periodically by FL Studio. Drains the bridge queue and samples
    peaks (both must run on the main thread — FL's API is not thread-safe)."""
    if _peak_monitor is not None:
        try:
            _peak_monitor.sample()
        except Exception as exc:
            print(f"[FL_MCP] OnIdle peak sample error: {exc}")
    if _bridge_server is not None and _bridge_registry is not None:
        try:
            _bridge_server.drain_once(_bridge_registry, max_per_call=8)
        except Exception as exc:
            print(f"[FL_MCP] OnIdle drain error: {exc}")
    if _state_watcher is not None and _bridge_server is not None:
        try:
            for ev in _state_watcher.poll():
                _bridge_server.send_event(ev["name"], ev["data"])
        except Exception as exc:
            print(f"[FL_MCP] OnIdle state watch error: {exc}")
    return


def OnSysEx(event):
    """Called by FL Studio when a SysEx message arrives on this input."""
    if _bridge_server is not None:
        try:
            _bridge_server.feed_packet(bytes(event.sysex))
        except Exception as exc:
            print(f"[FL_MCP] OnSysEx feed error: {exc}")
    return


def OnMidiOutMsg(event):
    """FL sends MIDI to the controller during playback. While note capture is
    armed, record note-on/off with their transport position (in beats) so Linux
    can reconstruct the selected channel's notes. Read-only — never sets handled."""
    if _note_capture is None or not _note_capture.armed:
        return
    try:
        status = event.status & 0xF0
        is_noteon = (status == 0x90 and event.data2 > 0)
        is_noteoff = (status == 0x80) or (status == 0x90 and event.data2 == 0)
        if not (is_noteon or is_noteoff):
            return
        ppq = general.getRecPPQ()
        pos_ticks = transport.getSongPos(2)  # 2 = SONGLENGTH_ABSTICKS
        pos_beats = (pos_ticks / ppq) if ppq else 0.0
        _note_capture.feed(event.data1, event.data2, is_noteon, pos_beats)
    except Exception as exc:
        print(f"[FL_MCP] OnMidiOutMsg capture error: {exc}")


# Start the terminal interface when loaded in FL Studio
# No need to call this explicitly as OnInit will be called by FL Studio
