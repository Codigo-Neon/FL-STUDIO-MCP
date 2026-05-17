# FL MCP — Guía de Desarrollo

## Arquitectura

Sistema de control remoto de FL Studio desde Linux o Windows vía MIDI en tiempo real.

```
Linux:    Claude (MCP) → trigger.py → /dev/snd/midiC0D0 → VirMIDI → Wine ALSA → FL Studio → device_test.py
Windows:  Claude (MCP) → trigger.py → python-rtmidi → puerto loopMIDI "FL_MCP" → FL Studio → device_test.py
```

| Componente | Descripción |
|---|---|
| `trigger.py` | Servidor FastMCP, ~900 líneas, 43 tools. Genera y envía MIDI |
| `device_test.py` | Script MIDI dentro de FL Studio. Recibe y ejecuta comandos |
| `knowledge/` | 10 módulos de producción (escalas, acordes, drums, bass, plugins, mixer) |

Comunicación unidireccional: Linux → FL Studio. No se puede leer estado de vuelta.

---

## Protocolo MIDI

| Función | Nota inicio | Nota fin | Payload |
|---|---|---|---|
| Grabación melodía/bajo | 76 (start rec+play) | 77 (stop rec) | Notas MIDI crudas en tiempo real |
| Tempo | 72 | 73 | Bytes de BPM |
| Mixer | 74 | 75 | command_type + params |

### Transporte MIDI
- Abstracción cross-platform en `knowledge/midi_transport.py`:
  - **Linux**: `LinuxRawTransport` → escritura directa a `/dev/snd/midiC0D0`
  - **Windows**: `WindowsRtmidiTransport` → `python-rtmidi` al puerto virtual `FL_MCP` (creado por loopMIDI)
- `trigger.py` usa `create_transport()` que detecta plataforma vía `sys.platform`
- **NO usar** mido (falla con Wine ALSA) ni amidi subprocess (demasiado lento)
- Conexión Linux: `aconnect` VirMIDI 0-0 → WINE ALSA Input
- Tests: `pytest tests/test_midi_transport.py` (mocks rtmidi y open() — corre en cualquier plataforma)

---

## Bridge Bidireccional (Linux ↔ FL Studio)

Canal de retorno desde FL Studio hacia el MCP, complementario al canal MIDI (que sigue siendo unidireccional para envío de notas).

**Transporte:** TCP plano sobre `localhost:8765` con framing newline-delimited JSON (JSONL). Stdlib only en ambos lados.

**Tipos de mensaje:**

| Tipo | Sentido | Propósito |
|---|---|---|
| `req` | Linux → FL | Query con `id`, `method`, `params` |
| `res` | FL → Linux | Respuesta correlacionada por `id`, con `ok` + `result` o `error` |
| `evt` | FL → Linux | Evento empujado sin request previo (cambio de BPM, pattern switch, etc.) |

**Threading en FL Studio:**
- `bridge/server.py` corre un thread worker que acepta UNA conexión y lee mensajes
- Las requests entran a `pending_requests` (queue thread-safe)
- `OnIdle()` de `device_test.py` llama `server.drain_once(registry)` que dispatchea contra `HandlerRegistry`
- Los handlers se ejecutan en el thread principal de FL — única zona segura para tocar el API de FL Studio

**Ubicación de archivos:**
- Linux (este repo): `bridge/{__init__,protocol,client,server,handlers,fl_handlers,fl_adapter}.py`
- FL Studio (instalado por el installer): copiado a `Documents/Image-Line/FL Studio/Settings/Hardware/FL_MCP/bridge/`

**Métodos registrados (v1):**
- `ping` — sanity check, devuelve `{"pong": True}`
- `get_fl_state` — devuelve `{bpm, current_pattern, pattern_count, channels[], mixer_tracks[]}`

**Tools MCP expuestas:**
- `ping_fl()` — wraps `ping`
- `get_fl_state()` — wraps `get_fl_state`

**Cómo agregar un método nuevo:**
1. Definir el método en `FLApi` Protocol (`bridge/fl_handlers.py`)
2. Implementarlo en `LiveFLAdapter` (`bridge/fl_adapter.py`)
3. Registrarlo en `register_all()` de `bridge/fl_handlers.py`
4. Exponerlo como tool MCP en `trigger.py`
5. Tests: agregar caso en `tests/bridge/test_fl_handlers.py` con `FakeFLApi`

---

## Calibración de Timing para Grabación en Tiempo Real

Cuando se envían notas via grabación real-time (Note 76 → notas → Note 77), el timing requiere calibración precisa.

### Delay de Arranque (después de Note 76)

```python
send_raw_midi('90 4C 01')   # Note 76 ON — start recording
time.sleep(0.01)
send_raw_midi('80 4C 00')   # Note 76 OFF
time.sleep(0.05)             # Delay mínimo — NO usar 0.5s o más
```

Un delay largo (0.5s+) causa que las notas arranquen ~1 beat tarde en el piano roll.

### Compensación de Drift por BPM

Python `sleep()` acumula errores de timing que varían según el tempo del proyecto.

| BPM | Factor DRIFT | Resultado | Notas |
|---|---|---|---|
| 80 | `1.0` (ninguno) | 24.36s real vs 24.00s esperado | Timing preciso, sin compensación |
| 90 | `1.21` | Corrige compresión de 0.826× | Sin compensar: 31.9 beats → 26.36 grabados |

### Aplicación del Drift

```python
bpm = 80
seconds_per_beat = 60.0 / bpm
DRIFT = 1.0  # Ajustar según tabla

# Construir eventos
for note, velocity, length, position in notes:
    t_on = position * seconds_per_beat * DRIFT
    t_off = (position + length) * seconds_per_beat * DRIFT
    events.append((t_on, 'on', note, velocity))
    events.append((t_off, 'off', note, 0))
events.sort(key=lambda e: e[0])
```

### Reglas Generales

1. **BPMs lentos (≤80)**: No necesitan compensación de drift
2. **BPMs rápidos (90+)**: Necesitan drift creciente
3. **BPM nuevo sin calibrar**: Empezar con `DRIFT=1.0`, enviar patrón de prueba, exportar MIDI y verificar posiciones bar/beat
4. **Calibrar**: `DRIFT = beats_esperados / beats_grabados`

### Formato de Notas

```python
# (midi_note, velocity, length_in_beats, position_in_beats)
(39, 115, 0.5, 0.0)   # D#2, vel 115, duración medio beat, posición beat 1

# Notas relevantes en D# minor:
# D#2 = 39 (root), E2 = 40 (cromático), F#2 = 42, G#2 = 44, A#2 = 46, B2 = 47
```

### Envío Completo

```python
# 1. Start recording
send_raw_midi('90 4C 01'); time.sleep(0.01); send_raw_midi('80 4C 00')
time.sleep(0.05)

# 2. Enviar notas en tiempo real
start_time = time.time()
for event_time, event_type, note, vel in events:
    wait = event_time - (time.time() - start_time)
    if wait > 0:
        time.sleep(wait)
    if event_type == 'on':
        send_raw_midi(f'90 {note:02X} {vel:02X}')
    else:
        send_raw_midi(f'80 {note:02X} 00')

# 3. Stop recording
time.sleep(0.5)
send_raw_midi('90 4D 01'); time.sleep(0.01); send_raw_midi('80 4D 00')
```

---

## Sistema de BPM

- Variable global `current_bpm` en trigger.py (default 90)
- `set_bpm()` almacena y sincroniza con FL Studio
- Todos los tools de generación usan `current_bpm` automáticamente
- BPM afecta: sugerencia de patrones, humanize, duración de notas, sustain de 808

---

## Sistema de Mixer

- 11 comandos via protocolo MIDI (volume, pan, route, mute, solo, name, color, etc.)
- `setup_sidechain(kick_track, bass_track)` crea routing + guía
- `apply_mixer_template(genre)` configura mixer completo por género
- Sidechain requiere setup manual de Fruity Limiter después del routing

---

## Sistema de Instalación (Windows)

`installer/` empaqueta el setup automático del MCP en Windows en 3 sub-paquetes:

### `installer/setup_engine/` — Lógica pura

| Módulo | Responsabilidad |
|---|---|
| `detect.py` | Devuelve `EnvironmentReport` con qué hay instalado (Claude Desktop, FL Studio, loopMIDI, WebView2) |
| `claude_config.py` | Edita `claude_desktop_config.json` con backup `.bak`. Tira `ConfigCorruptedError` si el JSON está roto |
| `fl_studio.py` | Copia `device_test.py` a `Documents/Image-Line/FL Studio/Settings/Hardware/FL_MCP/` + crea `.nfo` companion |
| `loopmidi.py` | Descarga loopMIDI del sitio oficial, descomprime ZIP, instalación silenciosa, crea/detecta puerto virtual `FL_MCP` |
| `cli.py` | Wrapper argparse: `python -m installer.setup_engine.cli <subcommand>` para QA manual |

### `installer/wizard/` — GUI primera vez

| Archivo | Responsabilidad |
|---|---|
| `api.py` | `JsApi` — métodos callable desde JS via `pywebview.api.*`. Wraps cada función del setup_engine y la traduce a `{ok, error}` |
| `window.py` | `launch_wizard()` — abre la ventana pywebview, inyecta JsApi, bloquea hasta cierre |
| `ui/index.html` | 9 pasos como `<section>` apilados, ocultos via clase `.hidden` |
| `ui/styles.css` | Dark mode estilo VS Code, sidebar 220px + main 32px padding |
| `ui/wizard.js` | Vanilla JS — state machine de pasos, llama a `pywebview.api.*`. Usa `replaceChildren()`/`textContent` solamente (no `innerHTML`) |

### `installer/tray/` — App persistente

| Archivo | Responsabilidad |
|---|---|
| `state.py` | `AppState` — persiste `setup_completed` en `%APPDATA%\FL MCP Studio\state.json` |
| `supervisor.py` | `Supervisor.check_status()` — detecta proceso del MCP server + verifica puerto MIDI |
| `app.py` | `TrayApp` — pystray + menú + thread polling cada 5s |

### `installer/main.py` — Entry point

Lee `state.json` → si setup no completo lanza wizard; después (siempre) lanza tray.

### `installer/build/` — Build pipeline

| Archivo | Responsabilidad |
|---|---|
| `fetch_python.py` | Descarga Python 3.11 embedded de python.org, parchea `_pth` para habilitar site-packages |
| `install_deps.py` | `pip install --platform win_amd64 --only-binary=:all:` — wheels Windows desde Linux dev |
| `stage.py` | Copia trigger.py, device_test.py, knowledge/, installer/ a `build/staging/`. Filtra `__pycache__`, `tests/`, `.pyc`. Escribe `flmcp.bat` |
| `setup.iss` | Inno Setup script: metadata, [Files], [Icons], [Run], [UninstallDelete] |
| `build.sh` | Orquestador: fetch → install_deps → stage → iscc (via Wine en Linux). Output: `installer/build/dist/FL-MCP-Studio-Setup-vX.Y.Z.exe` |

Build local desde Linux: `cd installer/build && ./build.sh` (requiere Wine + Inno Setup 6 instalado bajo Wine — ver `installer/BUILD.md`).

**No usamos PyInstaller** (deviation del spec original). Embedded Python directo es más liviano, más AV-friendly, y mantiene las paths que `wizard.js` hardcodea.

Tests: `pytest tests/wizard tests/tray tests/setup_engine tests/build_pipeline` (Linux con pyfakefs/tmp_path + mocks de subprocess/urllib/rtmidi/psutil). QA end-to-end manual via `installer/QA_CHECKLIST.md` en VM Windows.

---

## Preferencias del Proyecto

- **Idioma**: Español (todo output y guías en español)
- **Géneros principales**: Boom bap, trap, phonk
- **Plataforma**: Kali Linux + FL Studio via Wine
