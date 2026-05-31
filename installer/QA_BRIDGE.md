# QA Manual del Bridge Bidireccional

Validación end-to-end que requiere FL Studio corriendo. Ejecutar después de cualquier cambio al bridge.

## Pre-requisitos

- [ ] FL Studio 2024 instalado (Linux: via Wine; Windows: nativo)
- [ ] `device_test.py` y `bridge/` copiados a `Documents/Image-Line/FL Studio/Settings/Hardware/FL_MCP/`
- [ ] FL Studio configurado con el script "Test Controller" activo en MIDI Settings
- [ ] `trigger.py` corriendo como MCP

## Test 1: Bridge se levanta al abrir FL

- [ ] Abrir FL Studio
- [ ] Verificar en la consola del script (View → Script output) que aparece:
  ```
  FL Studio MCP Beat Builder initialized
  [FL_MCP] Bridge server escuchando en localhost:8765
  ```
- [ ] Si dice "Bridge no disponible", el package `bridge/` no se copió bien — revisar instalación

## Test 2: Ping desde el MCP

- [ ] Desde Claude Desktop (o cliente MCP), invocar la tool `ping_fl`
- [ ] Verificar que devuelve `{"pong": True}`
- [ ] Latencia esperada: <50ms

## Test 3: Get state retorna datos reales

- [ ] Cargar un proyecto FL con BPM conocido (ej. 90), >1 pattern, varios canales
- [ ] Invocar `get_fl_state`
- [ ] Verificar:
  - `bpm` ≈ 90 (tolerancia ±0.1)
  - `pattern_count` > 1
  - `channels` contiene los canales del rack
  - `mixer_tracks[0].name == "Master"`

## Test 4: Reconexión

- [ ] Con el MCP corriendo, cerrar FL Studio
- [ ] Invocar `ping_fl` — debe devolver `{"error": "..."}` (no debe colgarse)
- [ ] Reabrir FL Studio, esperar 5 segundos
- [ ] Invocar `ping_fl` de nuevo — debe devolver `{"pong": True}` (reconexión transparente)

## Test 5: Cleanup al cerrar FL

- [ ] Con el MCP corriendo, cerrar FL Studio
- [ ] Verificar que no queda ningún proceso escuchando en el puerto 8765:
  ```bash
  ss -lntp | grep 8765    # Linux
  netstat -ano | findstr 8765    # Windows
  ```

## Test 6: Mastering Tools (mezcla/mastering)

Pre-requisitos: FL Studio abierto, Test Controller cargado, un proyecto real con mixer poblado.

- [ ] `analyze_mix_static()` en un proyecto vacío devuelve "Sin problemas detectados".
- [ ] Cargar un proyecto con un track que tenga 5+ FX → `analyze_mix_static()` lo marca como `fx-heavy` por nombre.
- [ ] Subir el master fader por encima de 0dB → `analyze_mix_static()` reporta `master-clipping-risk`.
- [ ] `set_genre("phonk")` → `get_mastering_target()` devuelve `lufs -6`, `true_peak -0.3`.
- [ ] `start_peak_monitoring()` → reproducir el drop 30s → `stop_peak_monitoring()` → `analyze_master()`:
      los peaks L/R del master reportados coinciden visualmente con el master meter de FL (±1dB).
- [ ] `analyze_master()` sin monitoring previo → guía para correr `start_peak_monitoring`.
- [ ] `set_mastering_target(true_peak=-1.0)` y luego `analyze_master()` usa el override.
- [ ] `get_track_peaks(<un track sonando>)` devuelve valores dB plausibles durante playback.
- [ ] Verificar que `analyze_master()` siempre aclara que LUFS no está disponible vía FL Script API.

## Test 7: Piano roll capture (lectura de notas)

Pre-requisitos: FL Studio abierto, Test Controller **recargado** (re-seleccionar el script en MIDI Settings, o reabrir FL — FL tiene en memoria la versión vieja hasta recargar).

**Verifica el riesgo dominante:** que `OnMidiOutMsg` reciba las notas del playback.

- [ ] Abrir un pattern con notas conocidas en un canal (ej. un bajo de 4 notas en posiciones claras).
- [ ] Seleccionar ese canal en el channel rack.
- [ ] Desde Claude: `capture_pattern(bars=2)`.
- [ ] **Verificar:** la salida lista las notas con nombre correcto (ej. `C2`, `G2`) y posiciones `bar:beat` coherentes con lo que se ve en el piano roll.
- [ ] **Si devuelve "0 notas capturadas":** `OnMidiOutMsg` no recibe el playback del canal de instrumento. Aplicar fallback (rutear la salida MIDI del canal al puerto del script — "MIDI Out") o evaluar el Enfoque B (loopback). **Documentar el resultado abajo** — es la conclusión del milestone de factibilidad.
- [ ] Si las posiciones están desfasadas en pattern mode: validar el modo de `transport.getSongPos()` (actualmente `2` = SONGLENGTH_ABSTICKS).
- [ ] **Comportamiento multi-loop (clave):** `getSongPos(2)` devuelve ticks **absolutos de song**, no relativos al pattern. Si el pattern loopea dentro de la ventana de `bars`, las posiciones treparían (bar 3, 4...) en vez de wrappear, y aparecerían notas duplicadas. Probar con `bars` igual al largo real del pattern (una sola pasada) y verificar que NO hay duplicados ni posiciones fuera de rango. Si los hay → normalizar la posición contra el largo del pattern (`position_beats % pattern_beats`) en `OnMidiOutMsg`.

## Reporte

Pegar acá los resultados de cada test, con timestamps y cualquier output relevante de la consola del script de FL.
