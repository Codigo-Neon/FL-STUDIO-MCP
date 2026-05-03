# FL MCP Studio — Instalador Windows (Spec de Diseño)

**Fecha**: 2026-05-03
**Autor**: brainstorm con Claude
**Estado**: Aprobado por usuario, pendiente revisión final
**Proyecto relacionado siguiente**: Cliente chat multi-LLM (spec aparte, etapa 2)

---

## 1. Objetivo

Permitir que usuarios de Windows **sin conocimientos de terminal** instalen y usen el MCP de FL Studio mediante un único `.exe` con instalación guiada por wizard y administración via icono en bandeja del sistema.

Resultado esperado: usuario descarga 1 archivo, hace doble click, sigue 8 pasos visuales (uno requiere acción manual en FL Studio), y queda listo para usar Claude Desktop hablándole a FL Studio.

## 2. Alcance

### Incluido
- Instalador `.exe` de Windows (Inno Setup) que empaqueta todo
- Wizard GUI de primera vez (HTML/CSS/JS dentro de pywebview)
- Tray app persistente para monitoreo y control
- Refactor cross-platform del transporte MIDI (Linux + Windows)
- Auto-detección e instalación de dependencias (loopMIDI, WebView2)
- Auto-configuración de Claude Desktop y FL Studio MIDI script
- Sistema de logs rotativos y diagnóstico de errores
- Pipeline de build automatizado (GitHub Actions)
- Notificaciones de actualización (no auto-update silencioso)

### Excluido (proyecto separado)
- Cliente chat multi-LLM con soporte para OpenAI/Google/DeepSeek/etc. — se brainstorm por separado en etapa 2
- Code signing del `.exe` (opt-in para v2 si crece la base)
- Soporte para macOS
- Soporte para FL Studio < 21
- Soporte para Windows < 10 22H2

## 3. Arquitectura

### Capas

```
flmcp-installer.exe   (Inno Setup ~40 MB)
└─ Bundle: Python embebido + código + WebView UI
       │
       ▼ instala a C:\Program Files\FL MCP Studio
FL MCP Studio (app instalada)
├─ flmcp-gui.exe       → Wizard + Tray (pywebview + pystray)
├─ flmcp-server.py     → MCP server (trigger.py refactorizado)
├─ python-embed/       → Python 3.11 portátil
├─ ui/                 → HTML/CSS/JS del panel
├─ knowledge/          → módulos existentes
└─ device_test.py      → script para FL Studio
```

### Componentes y responsabilidades

| Componente | Responsabilidad | Tecnología |
|---|---|---|
| **Installer** | Copia archivos, registra en "Programas y características" de Windows, crea acceso directo, lanza wizard la primera vez | Inno Setup |
| **flmcp-gui.exe** | Único punto de entrada visible para el usuario. Wizard de primera vez + Tray app permanente | Python + pywebview + pystray |
| **Setup Engine** (módulo Python dentro de gui) | Detección de entorno, descarga loopMIDI, crea puerto MIDI virtual, copia script, edita config Claude | Python puro |
| **flmcp-server.py** | El MCP server actual. Lo lanza Claude Desktop por stdio (no el GUI) | FastMCP |
| **Cross-platform MIDI layer** *(nuevo)* | Abstrae `/dev/snd/midiC0D0` (Linux) vs `python-rtmidi` puerto Windows | Python |

### Cambio crítico en código existente

`trigger.py` actualmente tiene:

```python
MIDI_DEV = "/dev/snd/midiC0D0"
def send_raw_midi(hex_str): open(MIDI_DEV, 'wb').write(...)
```

Se refactoriza a un módulo nuevo `knowledge/midi_transport.py`:

```python
class MidiTransport:
    @staticmethod
    def create():
        if sys.platform == "linux":
            return LinuxRawTransport()  # /dev/snd/midiC0D0
        elif sys.platform == "win32":
            return WindowsRtmidiTransport()  # rtmidi → "FL_MCP" port
```

**Compatibilidad con Linux se mantiene 100%** — el setup actual del usuario en Kali Linux no se rompe.

## 4. Flujo del wizard de primera vez

Después del clásico Inno Setup ("Acepto licencia → Carpeta → Install"), se abre la ventana propia.

- **Tamaño**: 700×500 px, no resizable
- **Look**: dark mode, estilo VS Code / Linear
- **Estructura**: sidebar izquierdo con lista de pasos + check verde por avance, área principal a la derecha con contenido del paso actual

| # | Pantalla | Acción del usuario | Acción automática |
|---|---|---|---|
| 1 | **Bienvenida** | Click "Comenzar" | Cierra alertas si FL Studio está abierto |
| 2 | **Diagnóstico** | Mira los ✅/❌ | Detecta Claude Desktop, FL Studio, loopMIDI, WebView2 |
| 3 | **Resolver faltantes** | Click "Instalar todo" o links de descarga | Baja loopMIDI silencioso desde sitio oficial. Si falta Claude/FL Studio → botón abre el sitio oficial y marca el paso como "lo hago después" |
| 4 | **Crear puerto MIDI** | Solo mira progreso | Ejecuta `loopMIDI.exe /AddPort:FL_MCP` |
| 5 | **Instalar script en FL** | Solo mira | Copia `device_test.py` + metadata a `Documents\Image-Line\FL Studio\Settings\Hardware\FL_MCP\` (ruta vía `%USERPROFILE%`) |
| 6 | **Registrar en Claude Desktop** | Solo mira | Edita `%APPDATA%\Claude\claude_desktop_config.json` con backup `.bak` |
| 7 | **Paso manual en FL Studio** | Sigue las instrucciones, click "Ya lo hice" | Muestra GIF de 8 segundos: Options → MIDI Settings → Enable FL_MCP → Refresh |
| 8 | **Test de conexión** | Click "Probar" | Manda nota MIDI 60 → si FL recibe ✅; si no, modo diagnóstico |
| 9 | **Listo** | Click "Cerrar" | App se minimiza a la bandeja, queda corriendo |

### Manejo de fallos por paso

Cada paso tiene botón "Saltar" + "Ver log". Si un paso falla, queda marcado en amarillo y se puede reintentar desde el tray. **El wizard nunca bloquea**.

### Decisiones sobre dependencias externas

- **loopMIDI**: se descarga desde el sitio oficial del autor (`tobias-erichsen.de`) durante el paso 3. Sin internet → fallback automático a abrir el navegador para descarga manual. Justificación: legalmente limpio + siempre obtenemos la última versión.
- **Paso 7 manual en FL Studio**: no se intenta automatizar. La API de scripting de FL Studio para auto-asignar dispositivos es frágil entre versiones. Un GIF claro de 8 segundos + un botón "Ya lo hice" es más robusto.

## 5. Tray app (post-wizard)

Ícono pequeño en la bandeja del sistema.

### Interacción
- **Click izquierdo**: menú compacto con estado y acciones rápidas
- **Click derecho**: menú clásico de Windows

### Menú

```
🟢 FL MCP Studio
─────────────────
Estado: Conectado a FL Studio ✅
MCP Server: Corriendo (PID 4823)
─────────────────
▸ Abrir panel completo
▸ Probar conexión MIDI
▸ Reabrir wizard de setup
▸ Ver logs en vivo
─────────────────
▸ Buscar actualizaciones
▸ Acerca de
▸ Salir
```

### Estados del ícono

| Color | Significado |
|---|---|
| 🟢 Verde | Todo OK, server corriendo, FL responde |
| 🟡 Amarillo | Server corriendo pero FL no responde a pings |
| 🔴 Rojo | Server caído o config rota |
| ⚪ Gris | Pausado por el usuario |

## 6. Sistema de actualizaciones

- Tray al iniciar (máx 1 vez por día) hace `GET` a la API de releases de GitHub
- Si hay versión nueva → notificación toast nativa de Windows
- Click en la notificación → abre el navegador en la página de release
- **No instala silencioso** — es invasivo y a usuarios no-técnicos los desconcierta
- Settings opcional: "Avisarme cada X días" o "Nunca avisar"

## 7. Manejo de errores

**Filosofía**: el usuario no técnico nunca ve un stack trace. Toda excepción se traduce a un mensaje accionable + botón "Copiar log" (formato listo para pegar en GitHub Issues).

| Tipo de error | Qué ve el usuario | Qué pasa por dentro |
|---|---|---|
| loopMIDI no se descarga (sin internet) | "No pudimos bajar loopMIDI. ¿Tenés conexión? [Reintentar] [Descargar manualmente]" | Detecta `requests.ConnectionError`, sugiere fallback |
| Puerto MIDI ya existe | "El puerto FL_MCP ya estaba creado, lo reutilizamos ✅" | No es error real, salta el paso |
| `claude_desktop_config.json` corrupto | "Tu config de Claude Desktop tiene un error. ¿Querés que la arreglemos? Vamos a hacer backup primero." | Restaura desde `.bak` o crea config nueva |
| FL Studio no encontrado | "No detectamos FL Studio. Si lo instalaste en otra carpeta, indicanos dónde está." | Selector de carpeta manual |
| Test de conexión falla (paso 8) | "FL Studio no respondió. Lo más común: olvidaste 'Enable' en MIDI Settings. Volvé al paso 7." | Detecta timeout en respuesta del script |
| Server crashea en runtime | Tray pasa a 🔴, notificación: "El server se cayó. [Reiniciar] [Ver log]" | Supervisor de proceso en pystray |

### Logs

- Ubicación: `%APPDATA%\FL MCP Studio\logs\`
- Rotativos: máx 5 archivos × 1 MB
- Nivel: INFO por defecto, DEBUG activable desde tray

## 8. Build & distribución

### Estructura de repo

```
src/                       (código actual + nuevo)
installer/
├─ flmcp.iss              (script Inno Setup)
├─ build_windows.sh       (cross-build desde Linux)
└─ assets/                (icono .ico, GIF del paso 7, banner wizard)
.github/workflows/
└─ release.yml            (CI: tag → build .exe → publish release)
```

### Pipeline (GitHub Actions, runner `windows-latest`)

1. Checkout
2. Descarga Python 3.11 embedded distribution (~15 MB)
3. `pip install` deps a una carpeta local (`pywebview`, `pystray`, `python-rtmidi`, `mcp`, etc.)
4. Compila el GUI con PyInstaller en modo `--onedir` (más estable que `--onefile`, menos AV-flagging)
5. Inno Setup compila `flmcp.iss` → `FL-MCP-Studio-Setup-vX.Y.Z.exe`
6. Sube el `.exe` como asset al release de GitHub

### Cross-build local (Linux dev)

Usar `wine` + `iscc` (Inno Setup CLI) para testear builds sin reiniciar a Windows. CI usa runner Windows real para builds finales.

### Code signing

Opt-in, no obligatorio en v1. Sin firma, Windows SmartScreen muestra "Editor desconocido" la primera vez (un click en "Más info → Ejecutar de todos modos"). Certificado Sectigo ~$80/año — se evalúa para v2 si crece la base de usuarios.

## 9. Testing

| Capa | Cómo se testea |
|---|---|
| `MidiTransport` (Linux/Win abstraction) | Tests unitarios con mocks de `rtmidi` y `/dev/snd`. CI Linux y Windows |
| Detección de entorno (paso 2 del wizard) | Tests con fixtures de filesystems falsos (`pyfakefs`) |
| Edición de `claude_desktop_config.json` | Tests con configs sample (vacía, válida, corrupta, con otros MCPs ya registrados) |
| Wizard end-to-end | Manual — VM Windows 10 limpia + Windows 11 limpia. Checklist en `installer/QA_CHECKLIST.md` |
| MCP server (`trigger.py`) | Suite actual sigue funcionando (no rompemos Linux) |

### Promesa de no-regresión Linux

CI corre el flujo actual `device_test.py` en runner Linux para garantizar que el refactor del transport no rompe el setup existente del usuario.

## 10. Versiones soportadas

- **Windows 10 22H2+** y **Windows 11** (WebView2 preinstalado en ambos)
- **FL Studio 21+** (versiones anteriores tienen API de scripting distinta)
- **Claude Desktop**: cualquier versión actual
- **Linux**: setup actual del usuario no cambia

## 11. Decisiones tomadas

| Decisión | Opción elegida | Razón |
|---|---|---|
| Nivel de automatización | C — todo automático | Pedido del usuario para audiencia no-técnica |
| Tipo de UX | Wizard primera vez + tray después | Combina guía paso a paso con uso liviano post-setup |
| Tecnología GUI | pywebview + Inno Setup | Look moderno, AV-friendly, reutilizable para el chat multi-LLM futuro |
| Distribución loopMIDI | Descarga del sitio oficial | Limpio legalmente + siempre versión actual |
| Paso 7 (FL Studio settings) | Manual con GIF | Auto-via-API es frágil entre versiones de FL |
| Auto-update | Notificación, no instalación silenciosa | Menos invasivo para usuarios no-técnicos |
| Code signing | Diferido a v2 | $80/año no justificado hasta tener base de usuarios |
| Multi-LLM support | Proyecto aparte (etapa 2) | Es construir un host MCP entero — alcance independiente |

## 12. Riesgos conocidos

| Riesgo | Mitigación |
|---|---|
| PyInstaller flagged por antivirus | Modo `--onedir` (no `--onefile`), Inno Setup como wrapper |
| WebView2 falta en Windows 10 viejo | Detección en paso 2 + link de descarga oficial Microsoft |
| FL Studio cambia ruta de scripts | Auto-detección con fallback a selector manual |
| loopMIDI descontinuado | Documentar alternativa: LoopBe1. Versión bundleable en assets si fuera necesario |
| Claude Desktop cambia formato de config | Tests de no-regresión con sample configs + backup automático |
| Usuario instala en carpeta sin permisos | Inno Setup pide elevación de admin; default a `C:\Program Files\` |

## 13. Próximos pasos

1. Aprobación final de este documento por el usuario
2. Invocar skill `writing-plans` para producir el plan de implementación detallado paso por paso
3. Ejecutar el plan (etapa de implementación, separada)
4. Proyecto siguiente (separado): brainstorm + spec del cliente chat multi-LLM
