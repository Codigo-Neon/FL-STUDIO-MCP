#!/usr/bin/env python3
"""
Script de debug MIDI para FL Studio
Envía datos MIDI y muestra exactamente qué se está enviando
"""
import mido
from mido import Message
import time

print("=" * 60)
print("DEBUG MIDI - FL Studio Test")
print("=" * 60)

# Listar todos los puertos disponibles
print("\n📋 Puertos MIDI disponibles:")
for i, port_name in enumerate(mido.get_output_names()):
    print(f"  {i}: {port_name}")

# Conectar al puerto de Wine
print("\n🔌 Conectando al puerto de Wine...")
try:
    output_port = mido.open_output('WINE midi driver:WINE ALSA Input 128:0')
    print("✅ Conectado exitosamente")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    exit(1)

# Función para enviar nota con debug
def send_note_debug(note, velocity=100, duration=0.5):
    print(f"\n→ Enviando Note ON: note={note}, velocity={velocity}")
    msg_on = Message('note_on', note=note, velocity=velocity)
    print(f"  Mensaje: {msg_on}")
    output_port.send(msg_on)

    time.sleep(duration)

    print(f"→ Enviando Note OFF: note={note}")
    msg_off = Message('note_off', note=note, velocity=0)
    print(f"  Mensaje: {msg_off}")
    output_port.send(msg_off)

# Enviar 3 notas de prueba
print("\n" + "=" * 60)
print("ENVIANDO NOTAS DE PRUEBA")
print("=" * 60)

print("\n🎹 Nota 1: Do (C4) - MIDI 60")
send_note_debug(60, 100, 0.8)
time.sleep(0.3)

print("\n🎹 Nota 2: Mi (E4) - MIDI 64")
send_note_debug(64, 100, 0.8)
time.sleep(0.3)

print("\n🎹 Nota 3: Sol (G4) - MIDI 67")
send_note_debug(67, 100, 0.8)

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO")
print("=" * 60)
print("\nSi FL Studio está configurado correctamente:")
print("  1. Deberías haber ESCUCHADO 3 notas (Do-Mi-Sol)")
print("  2. La consola de scripts debería mostrar mensajes")
print("  3. Deberías ver actividad en los indicadores MIDI")
print("\nSi NO pasó nada:")
print("  - Verifica que VirMIDI 1-0 esté ENABLED en MIDI Settings")
print("  - Verifica que tengas un canal/instrumento seleccionado")
print("  - Abre View > Script output para ver mensajes del script")

output_port.close()
