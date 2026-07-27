#!/usr/bin/env bash
# Set up two ALSA virmidi ports for the FL_MCP SysEx bridge and connect them
# to Wine's ALSA in/out. Idempotent — safe to re-run.
#
# Requires: snd-virmidi module loaded with at least 2 devices (default has 4).
#
# Ports created (conceptually — virmidi just provides bidirectional pairs):
#   FL_MCP_IN  ← Linux→FL: trigger.py sends here, FL listens to it
#   FL_MCP_OUT ← FL→Linux: FL writes here via midiOutSysex, trigger.py listens

set -euo pipefail

echo "==> Checking snd-virmidi module..."
if ! lsmod | grep -q '^snd_virmidi'; then
    echo "    Loading snd-virmidi (needs sudo)..."
    sudo modprobe snd-virmidi midi_devs=4
fi

echo "==> Available ALSA MIDI ports:"
aconnect -l

echo ""
echo "==> Look for VirMIDI 0-0 and VirMIDI 0-1 above."
echo "    To connect Linux trigger.py to FL Studio bidirectionally:"
echo "      VirMIDI 0-0 → WINE Input    # trigger.py sends, FL receives"
echo "      WINE Output → VirMIDI 0-1   # FL sends, trigger.py receives"
echo ""
echo "    Use aconnect with the numeric client:port from 'aconnect -l' output."
echo "    Example (numbers vary on your system):"
echo "      aconnect 14:0 130:0   # VirMIDI 0-0 → WINE midi input"
echo "      aconnect 130:1 14:1   # WINE midi output → VirMIDI 0-1"
echo ""
echo "==> In FL Studio MIDI Settings:"
echo "    Input  row VirMIDI 0-0 → Controller type: Test Controller, Enable ✓"
echo "    Output row VirMIDI 0-1 → Send to port: same number as input"
echo ""
echo "==> Done. Re-run aconnect -l after the connections to verify."
