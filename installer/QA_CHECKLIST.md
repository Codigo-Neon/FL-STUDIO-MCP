# FL MCP Studio — QA Checklist

Manual end-to-end tests that require a real Windows 10/11 machine with FL Studio
21+ and Claude Desktop installed. These cannot be automated because they
exercise loopMIDI installation, FL Studio MIDI integration, and Claude Desktop's
config file mutation against real apps.

## Pre-flight

- [ ] Windows 10 22H2 or Windows 11
- [ ] FL Studio 21+ installed AND opened at least once (creates Settings dir)
- [ ] Claude Desktop installed
- [ ] No prior `FL_MCP` loopMIDI port (test fresh-install flow)

## First run

- [ ] Run `python -m installer.main`
- [ ] Wizard window opens (720×540, dark theme)
- [ ] Step 1 "Bienvenida" shown by default
- [ ] Sidebar shows all 9 steps with the first marked current
- [ ] Click "Comenzar" → moves to step 2

## Step 2 — Diagnóstico

- [ ] Auto-runs detection
- [ ] Each item shows ✅ or ❌ correctly
- [ ] Missing items show "no detectado"
- [ ] "Siguiente" enabled after detection

## Step 3 — Instalar loopMIDI

- [ ] Click "Instalar"
- [ ] Status box shows progress
- [ ] Network failure (disable Wi-Fi briefly) shows readable error
- [ ] Success → green border + checkmark + Siguiente enabled
- [ ] Verify loopMIDI now in Program Files

## Step 4 — Crear puerto MIDI

- [ ] Click "Crear puerto"
- [ ] Verify port `FL_MCP` appears in loopMIDI's window
- [ ] Re-run is no-op (port already exists, returns OK)

## Step 5 — Instalar script

- [ ] Click "Instalar script"
- [ ] Verify `device_test.py` exists at `%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Hardware\FL_MCP\`
- [ ] Verify `device_FL_MCP.nfo` companion exists

## Step 6 — Registrar Claude

- [ ] Click "Registrar"
- [ ] Verify `%APPDATA%\Claude\claude_desktop_config.json` has `flstudio` entry under `mcpServers`
- [ ] Verify `claude_desktop_config.json.bak` was created
- [ ] If a corrupted config exists, error message is friendly (not a stack trace)

## Step 7 — Manual FL Studio activation

- [ ] Open FL Studio → Options → MIDI Settings
- [ ] Find `FL_MCP` in Input list, Enable, set Controller type to `FL_MCP`
- [ ] Click Refresh, close Settings
- [ ] Return to wizard, click "Ya lo hice, continuar"

## Step 8 — Probar conexión

- [ ] Click "Probar"
- [ ] FL Studio should briefly show MIDI activity (either piano roll lights up or sounds play)
- [ ] Wizard shows ✅
- [ ] If FL Studio doesn't respond, error suggests revisiting step 7

## Step 9 — Listo

- [ ] Click "Cerrar e ir a la bandeja"
- [ ] Wizard window closes
- [ ] Tray icon appears in notification area (green)

## Tray app

- [ ] Right-click → menu shows all entries
- [ ] "Probar conexión MIDI" → toast notification with result
- [ ] "Reabrir wizard de setup" → wizard window reopens
- [ ] "Ver logs en vivo" → opens `%APPDATA%\FL MCP Studio\logs\` in Explorer
- [ ] Icon color changes when MCP server starts/stops in Claude Desktop

## Re-launch

- [ ] Close tray (Salir), re-run `python -m installer.main`
- [ ] Skips wizard (setup_completed=True), goes straight to tray

## Re-run wizard

- [ ] From tray menu → "Reabrir wizard de setup"
- [ ] Wizard opens at step 1
- [ ] Step 4 (create-port) reports "ya existía, OK"
- [ ] Step 6 (register-mcp) preserves any other MCP servers in the config

## Negative tests

- [ ] Run with FL Studio closed during step 8 → error explains the situation
- [ ] Manually corrupt `claude_desktop_config.json` then re-run step 6 → wizard offers backup-restore flow
