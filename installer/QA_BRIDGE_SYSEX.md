# QA Manual — Bridge SysEx (Plan A v2)

## Pre-requisitos

- [ ] `bridge/` y `device_test.py` instalados como `device_Test Controller.py` en `~/Documentos/Image-Line/FL Studio/Settings/Hardware/Test Controller/`
- [ ] `snd-virmidi` cargado con al menos 2 puertos (default 4 OK)
- [ ] python-rtmidi instalado en el venv del MCP: `.venv/bin/pip install python-rtmidi`
- [ ] FL Studio configurado:
  - Input row `VirMIDI 0-0` → Controller type `Test Controller`, Enable ✓
  - Output row `VirMIDI 0-1` → Send to port: mismo número que input

## Test 1: Setup ALSA loopback

```bash
./scripts/setup_alsa_loopback.sh
aconnect -l    # ver puertos
aconnect 14:0 130:0   # VirMIDI 0-0 → WINE input (ajustar números)
aconnect 130:1 14:1   # WINE output → VirMIDI 0-1
```

- [ ] `aconnect -l` muestra las conexiones bidireccionales

## Test 2: FL Studio carga el script SysEx

- [ ] Abrir FL Studio
- [ ] View → Script output, buscar:
  ```
  FL Studio MCP Beat Builder initialized
  [FL_MCP] SysEx bridge server registered (waiting for OnSysEx)
  ```
- [ ] **No** debe haber traceback de bridge

## Test 3: ping_fl()

- [ ] Desde Claude Desktop / MCP client, invocar `ping_fl()`
- [ ] Debe devolver `{"pong": true}`
- [ ] Latencia esperada: <100ms

## Test 4: get_fl_state()

- [ ] Cargar proyecto FL con BPM conocido + canales + patterns
- [ ] Invocar `get_fl_state()`
- [ ] Devuelve dict con `bpm`, `current_pattern`, `pattern_count`, `channels[]`, `mixer_tracks[]`

## Test 5: Tools MIDI legacy siguen funcionando

- [ ] `play()` → FL arranca playback
- [ ] `stop()` → FL para
- [ ] `set_bpm(120)` → BPM cambia

## Test 6: No corrupción entre canales

- [ ] Llamar `ping_fl()` y `set_bpm(140)` en rápida sucesión
- [ ] Ambas funcionan; ningún SysEx se mezcla con notas MIDI

## Reporte

Pegar resultados de cada test con outputs relevantes del Script output.
