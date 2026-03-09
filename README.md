# FL Studio MCP Server

**by Franco Doanti**

Servidor MCP (Model Context Protocol) que conecta Claude con FL Studio a traves de MIDI. Controla FL Studio desde una IA: genera beats, melodias, progresiones de acordes, lineas de bajo, configura el mixer, y recibe guias de produccion profesional — todo con lenguaje natural.

Funciona en **Linux** (Kali, Ubuntu, etc.) con FL Studio corriendo en **Wine**.

---

## Como Funciona

```
┌─────────────┐       MIDI        ┌──────────────────┐
│   Claude     │  ──────────────► │   FL Studio      │
│   (MCP)      │  /dev/snd/midi   │   (Wine)         │
│              │  VirMIDI 0-0     │                  │
│  trigger.py  │                  │  device_test.py  │
└─────────────┘                   └──────────────────┘
```

1. **Claude** interpreta tus instrucciones en lenguaje natural
2. **trigger.py** (servidor MCP) traduce las acciones a mensajes MIDI
3. Los mensajes viajan por **VirMIDI** (`/dev/snd/midiC0D0`)
4. **device_test.py** (MIDI script de FL Studio) recibe el MIDI y ejecuta las acciones en FL Studio via su API

La comunicacion es **unidireccional**: Claude envia comandos a FL Studio, pero no puede leer el estado actual del proyecto.

---

## Herramientas Disponibles (43 tools)

### Transporte y Control

| Herramienta | Descripcion |
|---|---|
| `play` | Reproducir el proyecto |
| `stop` | Detener la reproduccion |
| `set_bpm` | Establecer BPM del proyecto (20-999). Sincroniza con FL Studio |
| `get_bpm` | Ver BPM actual con contexto de genero y patrones compatibles |
| `list_midi_ports` | Listar puertos MIDI disponibles |

### Composicion y Generacion

| Herramienta | Descripcion |
|---|---|
| `send_melody` | Grabar notas en el piano roll de FL Studio en tiempo real |
| `send_midi_note` | Enviar una nota MIDI individual |
| `generate_drum_pattern` | Generar patron de bateria (9 estilos) con opcion de enviar a FL |
| `generate_chord_progression` | Generar progresion de acordes (7 tipos) en cualquier tonalidad |
| `generate_bassline` | Generar linea de bajo adaptada al BPM (4 estilos) |
| `generate_scale_notes` | Obtener todas las notas de una escala en rango de octavas |

### Mixer (11 comandos)

| Herramienta | Descripcion |
|---|---|
| `mixer_set_track_volume` | Volumen de pista (en dB) |
| `mixer_set_track_pan` | Paneo de pista (-1.0 a 1.0) |
| `mixer_create_route` | Crear/eliminar ruteo entre pistas (buses, sends, sidechain) |
| `mixer_mute_track` | Mutear/desmutear pista |
| `mixer_solo_track` | Solo toggle en pista |
| `mixer_link_channel_to_track` | Conectar canal del Channel Rack al mixer |
| `mixer_name_track` | Nombrar pista del mixer |
| `mixer_set_track_color` | Colorear pista (RGB) |
| `setup_sidechain` | Configurar ruteo de sidechain (kick → bajo) |
| `apply_mixer_template` | Aplicar template completo de mixer (nombres, colores, buses) |
| `get_sidechain_guide` | Guia completa de compresion sidechain |

### Asesoria de Mezcla

| Herramienta | Descripcion |
|---|---|
| `get_plugin_chain` | Cadena de plugins recomendada por elemento (kick, snare, bass, vocals...) |
| `get_vocal_processing` | Cadena vocal completa (10 slots con settings exactos) |
| `get_mastering_guide` | Cadena de mastering con Ozone 12 + targets LUFS por plataforma |
| `get_mix_reference_levels` | Niveles de referencia y paneo para cada elemento |
| `get_eq_frequency_guide` | Guia de frecuencias EQ por elemento |
| `get_send_effects` | Configuracion de sends (reverb, delay, compresion paralela) |
| `get_bass_technique` | Tecnicas de bajo por genero con cadena de procesamiento |
| `get_bass_growl_guide` | Guia de distorsion/growl para bajo |
| `get_mixing_checklist` | Checklist completo de mezcla paso a paso |
| `get_soundtoys_plugins_guide` | Guia de Soundtoys para produccion hip-hop |

### Analisis y Recomendaciones

| Herramienta | Descripcion |
|---|---|
| `suggest_for_bpm` | Recomendaciones completas segun BPM (patrones, bajo, acordes) |
| `suggest_scale` | Recomendar escalas por genero y mood |
| `suggest_progression` | Recomendar progresiones por tonalidad, genero y mood |
| `list_available_drum_patterns` | Listar patrones de bateria disponibles |
| `list_available_progressions` | Listar progresiones de acordes disponibles |

### Produccion y Referencia

| Herramienta | Descripcion |
|---|---|
| `get_producer_info` | Perfil completo de productores legendarios (13 disponibles) |
| `get_song_structure_template` | Estructura de cancion por genero |
| `get_vocal_tricks_guide` | Trucos avanzados de produccion vocal |
| `get_quick_start_guide` | Guia rapida de 10 pasos para hacer un beat |
| `get_mixer_layout` | Layout recomendado del mixer |
| `get_velocity_guide` | Guia de velocidades MIDI para programacion realista |

---

## Generos Soportados

- **Boom Bap** (80-95 BPM) — Escalas menores, swing 60%, drums secos
- **Jazz Hip-Hop** (75-95 BPM) — Dorica, acordes min7/maj9, swing alto
- **Lo-fi** (70-90 BPM) — Pentatonicas, bitcrush, chill
- **Trap** (130-160 BPM) — 808s con sustain, hi-hats rapidos, escalas menores
- **Phonk** (130-145 BPM) — Memphis style, 808 distorsionado
- **UK Drill** (140-145 BPM) — Slides de 808, frigia
- **Reggaeton** (85-100 BPM) — Dembow pattern

---

## Escalas

8 escalas con descripciones, formulas, mood, y tracks de referencia:

| Escala | Mood | Referencia |
|---|---|---|
| Menor Natural | Oscura, melancolica | Illmatic, The Infamous |
| Pentatonica Menor | Simple, poderosa | DJ Premier, Pete Rock |
| Blues | Soulful, tension | Gang Starr, Wu-Tang |
| Dorica | Jazzy, sofisticada | A Tribe Called Quest, J Dilla |
| Menor Armonica | Dramatica, cinematica | RZA, Alchemist |
| Frigia | Oscura, exotica | MF DOOM, Madlib |
| Mayor | Brillante, positiva | Kanye, Pharrell |
| Pentatonica Mayor | Feliz, soulful | Nujabes |

---

## Patrones de Bateria

9 patrones con datos de step/velocity exactos:

- `boom_bap_basic` — Patron clasico de boom bap
- `premier_style` — Estilo DJ Premier (kick en offbeats)
- `pete_rock_groove` — Groove jazzy de Pete Rock (ride cymbal)
- `havoc_minimal` — Minimalista estilo Havoc (Mobb Deep)
- `dilla_drunk` — Swing extremo J Dilla
- `9th_wonder_clean` — Limpio, programado (9th Wonder)
- `rza_wu_tang` — Crudo y agresivo (Wu-Tang)
- `advanced_2bar` — Patron avanzado de 2 compases
- `trap_basic` — Patron basico de trap

Cada patron incluye: velocidades por pieza (kick, snare, hi-hat), valores de swing, y rango de BPM recomendado.

---

## Progresiones de Acordes

7 progresiones transponibles a cualquier tonalidad:

- `classic_dark` — Clasica oscura
- `jazz_hiphop` — Jazz hip-hop (min7, dom7)
- `soul_feel` — Soul feel
- `melancholic` — Melancolica
- `minimal_jazz` — Jazz minimalista
- `phrygian_dark` — Oscura frigia
- `neo_soul` — Neo soul (min9, maj9)

---

## Perfiles de Productores

13 productores legendarios con guias de replicacion:

DJ Premier, Pete Rock, RZA, J Dilla, 9th Wonder, Madlib, Havoc, Large Professor, Alchemist, Hi-Tek, Buckwild, Lord Finesse, Marley Marl

Cada perfil incluye: estilo, drum machine, swing, enfoque de sampleo, escalas recomendadas, progresiones, efectos, tracks de referencia, y tips para replicar su sonido.

---

## Lineas de Bajo

4 estilos adaptativos al BPM:

| Estilo | Descripcion |
|---|---|
| `root_follow` | Sigue las fundamentales de los acordes |
| `808_sustain` | 808 con sustain largo (trap/phonk) |
| `walking` | Walking bass jazzy con notas de paso |
| `octave_bounce` | Rebote entre octavas |

---

## Sistema de Mixer

El template de mixer configura automaticamente:

```
Tracks 1-5:    Drums (Kick, Snare, HiHats, Percs, Clap)
Track 6:       Bass
Track 7:       808
Tracks 8-10:   Melodics (Sample, Melody, Pads)
Tracks 11-13:  Vocals (Main, Doubles, Ad-libs)
Track 100:     Bus Drums
Track 101:     Bus Melodies
Track 102:     Bus Vocals
```

Incluye: nombres, colores por elemento, ruteo a buses, y sidechain kick→bass.

---

## Requisitos

- **Linux** (probado en Kali Linux)
- **FL Studio** corriendo en Wine
- **Python 3.8+** con `mcp` (FastMCP)
- **VirMIDI** configurado (`modprobe snd-virmidi`)
- **aconnect** para conectar VirMIDI al input MIDI de Wine/FL Studio

### Instalacion

```bash
# 1. Cargar modulo VirMIDI
sudo modprobe snd-virmidi

# 2. Conectar VirMIDI a Wine ALSA
aconnect 20:0 128:0  # (ajustar numeros segun tu sistema)

# 3. Instalar dependencias
pip install mcp

# 4. Copiar device_test.py a la carpeta de MIDI scripts de FL Studio
# Ubicacion tipica: ~/.wine/drive_c/.../FL Studio/Settings/Hardware/

# 5. En FL Studio: MIDI Settings > seleccionar el controller "Test Controller"

# 6. Ejecutar el servidor MCP
python trigger.py
```

### Conexion con Claude Desktop

Agregar en `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flstudio": {
      "command": "python",
      "args": ["/ruta/completa/a/trigger.py"]
    }
  }
}
```

---

## Configuracion en Windows

En Windows, FL Studio corre nativamente (sin Wine), pero necesitas un **driver MIDI virtual** para que `trigger.py` pueda comunicarse con FL Studio. El concepto es el mismo: crear un cable MIDI virtual entre Python y FL Studio.

### Paso 1: Instalar loopMIDI (driver MIDI virtual)

loopMIDI reemplaza a VirMIDI de Linux. Crea puertos MIDI virtuales en Windows.

1. Descargar **loopMIDI** de [Tobias Erichsen](https://www.tobias-erichsen.de/software/loopmidi.html) (gratuito)
2. Instalar y ejecutar loopMIDI
3. En la ventana de loopMIDI, escribir un nombre para el puerto (ej: `MCP-FL`) y hacer click en **"+"**
4. Dejar loopMIDI abierto (se minimiza al system tray)

> **Tip:** Podes configurar loopMIDI para que arranque con Windows desde sus opciones.

### Paso 2: Instalar Python y dependencias

1. Descargar **Python 3.11+** de [python.org](https://www.python.org/downloads/)
   - **IMPORTANTE:** Marcar la casilla **"Add Python to PATH"** durante la instalacion
2. Abrir **CMD** o **PowerShell** e instalar las dependencias:

```powershell
pip install mcp mido python-rtmidi
```

> En Windows usamos **mido + python-rtmidi** en lugar de escribir directo a `/dev/snd/midi`. Esto requiere modificar `trigger.py` (ver Paso 5).

### Paso 3: Copiar el MIDI Script a FL Studio

1. Copiar `device_test.py` a la carpeta de MIDI scripts de FL Studio:
   ```
   C:\Program Files\Image-Line\FL Studio 2024\Settings\Hardware\
   ```
   > La ruta puede variar segun tu version. Buscar la carpeta `Settings\Hardware\` dentro del directorio de FL Studio.

2. Si la carpeta `Hardware` no existe, crearla.

### Paso 4: Configurar FL Studio

1. Abrir **FL Studio**
2. Ir a **OPTIONS > MIDI Settings** (o presionar F10 y pestaña MIDI)
3. En la seccion **Input**:
   - Buscar el puerto **"MCP-FL"** (o el nombre que pusiste en loopMIDI)
   - Seleccionarlo y habilitarlo (que quede resaltado)
4. En la seccion **Controller type** (abajo del input seleccionado):
   - Elegir **"Test Controller"** del desplegable
   - Este es el nombre que `device_test.py` registra como MIDI script
5. Hacer click en el boton **"Enable"** si no esta habilitado
6. Cerrar la ventana de MIDI Settings

> **Verificacion:** En la ventana de debug de FL Studio (View > Script output), deberia aparecer: `"FL Studio MCP Beat Builder initialized"`

### Paso 5: Modificar trigger.py para Windows

El `trigger.py` original escribe directamente a `/dev/snd/midiC0D0` (Linux). En Windows hay que usar `mido` con el puerto loopMIDI.

Reemplazar las lineas de MIDI device al inicio de `trigger.py`:

**Original (Linux):**
```python
MIDI_DEV = "/dev/snd/midiC0D0"
midi_dev = open(MIDI_DEV, "wb", buffering=0)

def send_raw_midi(hex_string):
    """Send raw MIDI bytes directly to device"""
    data = bytes.fromhex(hex_string.replace(" ", ""))
    midi_dev.write(data)
    midi_dev.flush()
```

**Modificado (Windows):**
```python
import mido
import sys

# Detectar sistema operativo y abrir MIDI
if sys.platform == "win32":
    # Windows: usar mido con loopMIDI
    MIDI_PORT_NAME = "MCP-FL"  # Nombre del puerto creado en loopMIDI
    # Buscar el puerto que coincida
    available = mido.get_output_names()
    port_name = None
    for name in available:
        if MIDI_PORT_NAME in name:
            port_name = name
            break
    if port_name is None:
        print(f"ERROR: No se encontro el puerto '{MIDI_PORT_NAME}'")
        print(f"Puertos disponibles: {available}")
        print("Asegurate de que loopMIDI esta corriendo con un puerto llamado 'MCP-FL'")
        sys.exit(1)
    midi_port = mido.open_output(port_name)
    print(f"Conectado a MIDI: {port_name}")

    def send_raw_midi(hex_string):
        """Send raw MIDI bytes via mido (Windows)"""
        data = bytes.fromhex(hex_string.replace(" ", ""))
        msg = mido.Message.from_bytes(data)
        midi_port.send(msg)
else:
    # Linux: escritura directa al device
    MIDI_DEV = "/dev/snd/midiC0D0"
    midi_dev = open(MIDI_DEV, "wb", buffering=0)

    def send_raw_midi(hex_string):
        """Send raw MIDI bytes directly to device (Linux)"""
        data = bytes.fromhex(hex_string.replace(" ", ""))
        midi_dev.write(data)
        midi_dev.flush()
```

> **Nota:** Esta modificacion hace que `trigger.py` funcione en **ambos** sistemas operativos automaticamente.

### Paso 6: Configurar Claude Desktop

Localizar el archivo de configuracion de Claude Desktop:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Normalmente esta en:
```
C:\Users\TU_USUARIO\AppData\Roaming\Claude\claude_desktop_config.json
```

Agregar la configuracion del servidor MCP:

```json
{
  "mcpServers": {
    "flstudio": {
      "command": "python",
      "args": ["C:\\Users\\TU_USUARIO\\ruta\\al\\proyecto\\trigger.py"]
    }
  }
}
```

> **Importante:** Usar doble barra invertida `\\` en las rutas de Windows dentro del JSON.

### Paso 7: Ejecutar

1. Asegurarse de que **loopMIDI** esta corriendo con el puerto "MCP-FL"
2. Abrir **FL Studio** (verificar que el MIDI script cargo correctamente)
3. Abrir **Claude Desktop** (el servidor MCP arranca automaticamente)
4. Hablarle a Claude: *"Poneme 90 BPM y haceme un patron boom bap"*

### Solucion de Problemas (Windows)

| Problema | Solucion |
|---|---|
| "No se encontro el puerto MCP-FL" | Verificar que loopMIDI esta corriendo y el puerto se llama exactamente "MCP-FL" |
| FL Studio no reconoce el controller | Ir a MIDI Settings, deseleccionar y volver a seleccionar el input + controller type |
| `pip install mido` falla | Verificar que Python esta en el PATH: `python --version` en CMD |
| `python-rtmidi` no instala | Instalar Visual C++ Build Tools: `pip install --only-binary :all: python-rtmidi` |
| Las notas no llegan a FL Studio | Abrir el MIDI monitor de loopMIDI para verificar que los mensajes salen. Verificar que el puerto correcto esta seleccionado como Input en FL Studio |
| Error "port already in use" | Cerrar cualquier otro programa que este usando el puerto MIDI (otro DAW, MIDI monitor, etc.) |
| Claude Desktop no encuentra trigger.py | Usar ruta absoluta completa con dobles barras invertidas en el JSON |
| Script output no muestra nada | Ir a View > Script output en FL Studio. Si no aparece "initialized", el script no cargo. Verificar ruta del archivo |

### Resumen de Diferencias Linux vs Windows

| Componente | Linux | Windows |
|---|---|---|
| MIDI Virtual | VirMIDI (`modprobe snd-virmidi`) | loopMIDI (aplicacion) |
| Conexion MIDI | `aconnect` | Se configura en FL Studio MIDI Settings |
| Transporte MIDI | Escritura directa a `/dev/snd/midiC0D0` | `mido` + `python-rtmidi` via loopMIDI |
| FL Studio | Wine | Nativo |
| Python | Preinstalado (Linux) | Instalar desde python.org |
| Config Claude | `~/.config/claude/claude_desktop_config.json` | `%APPDATA%\Claude\claude_desktop_config.json` |
| Dependencias extra | `mcp` | `mcp`, `mido`, `python-rtmidi` |

---

## Protocolo MIDI

La comunicacion usa notas MIDI con protocolos especializados:

| Protocolo | Nota Inicio | Nota Fin | Uso |
|---|---|---|---|
| Melodia (recording) | 76 | 77 | Activa rec+play, envia notas en tiempo real, detiene |
| Tempo | 72 | 73 | Envia BPM codificado en bytes MIDI |
| Mixer | 74 | 75 | Envia comando + parametros del mixer |

Las notas se envian escribiendo directamente a `/dev/snd/midiC0D0` para minima latencia (no usa mido ni amidi subprocess).

---

## Knowledge Base

10 modulos Python con conocimiento de produccion profesional:

| Modulo | Contenido |
|---|---|
| `scales.py` | 8 escalas con intervalos, descripciones, recomendaciones por genero/mood |
| `chords.py` | 12 tipos de acordes, 7 progresiones con voicings |
| `drum_patterns.py` | 9 patrones con step/velocity exactos, guia de swing |
| `basslines.py` | 4 estilos de bajo, cadena de procesamiento, reglas de oro |
| `plugin_chains.py` | 2500+ lineas: cadenas de plugins, EQ, mastering, gain staging |
| `vocal_chains.py` | Cadenas vocales completas, trucos avanzados |
| `producers.py` | 13 perfiles de productores con guias de replicacion |
| `song_structures.py` | Templates de estructura, transiciones, guia rapida |
| `constants.py` | Mapeo MIDI, nombres de notas, generos |
| `__init__.py` | Package init |

---

## Ejemplos de Uso

```
"Poneme un BPM de 90 y haceme un patron boom bap basico"
→ set_bpm(90) + generate_drum_pattern("boom_bap_basic", send_to_fl=True)

"Que escalas me recomendas para algo oscuro en La menor?"
→ suggest_scale(genre="boom_bap", mood="dark")

"Armame el mixer completo para boom bap"
→ apply_mixer_template("boom_bap")

"Como mixearia DJ Premier este beat?"
→ get_producer_info("dj_premier")

"Grabame una progresion jazz en Re menor"
→ generate_chord_progression("jazz_hiphop", key="D", send_to_fl=True)

"Configurame el sidechain del kick al bajo"
→ setup_sidechain(kick_track=1, bass_track=6)

"Dame la cadena de plugins para las vocales"
→ get_vocal_processing("standard")
```

---

## Licencia

Proyecto personal de Franco Doanti.
