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

## Reporte

Pegar acá los resultados de cada test, con timestamps y cualquier output relevante de la consola del script de FL.
