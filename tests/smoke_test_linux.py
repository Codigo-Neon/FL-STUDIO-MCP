"""Manual smoke test for the Linux MIDI transport.

Run this AFTER FL Studio is open and the WINE ALSA connection is up:

    aconnect -l                   # confirm WINE ALSA Input is visible
    aconnect 'VirMIDI 0-0' 'WINE ALSA Input'

    python tests/smoke_test_linux.py

You should hear/see one C5 note (MIDI note 60) play in FL Studio. If you
hear nothing, the transport refactor regressed Linux behavior.
"""
import time
from knowledge.midi_transport import create_transport


def main() -> None:
    transport = create_transport()
    print(f"Using transport: {type(transport).__name__}")

    print("Sending C5 note ON (vel 100)...")
    transport.send(bytes.fromhex("90 3C 64"))
    time.sleep(0.5)

    print("Sending C5 note OFF...")
    transport.send(bytes.fromhex("80 3C 00"))

    transport.close()
    print("Done. Did you hear/see the note in FL Studio?")


if __name__ == "__main__":
    main()
