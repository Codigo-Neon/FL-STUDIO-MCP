; FL MCP Studio — Inno Setup script
; Builds a single .exe installer that drops the staged tree into
; "Program Files\FL MCP Studio" and creates a Start Menu shortcut.
; The build orchestrator (build.sh) populates ./build/staging/ before
; calling iscc on this file.

#define MyAppName "FL MCP Studio"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "FL MCP"
#define MyAppExeName "flmcp.bat"

[Setup]
AppId={{CE2CB97E-03FB-4F5A-9336-79397DBEDD39}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=FL-MCP-Studio-Setup-v{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; The python-embed/ directory is staged by build.sh before iscc runs
Source: "build\staging\python-embed\*"; DestDir: "{app}\python-embed"; Flags: recursesubdirs createallsubdirs ignoreversion
; Project source files
Source: "build\staging\trigger.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\staging\device_test.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\staging\knowledge\*"; DestDir: "{app}\knowledge"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "build\staging\installer\*"; DestDir: "{app}\installer"; Flags: recursesubdirs createallsubdirs ignoreversion
; bridge/ and indexer/ are imported at module level by trigger.py. The wizard
; also copies bridge/ from {app} into FL Studio's Hardware dir.
Source: "build\staging\bridge\*"; DestDir: "{app}\bridge"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "build\staging\indexer\*"; DestDir: "{app}\indexer"; Flags: recursesubdirs createallsubdirs ignoreversion
; Launcher
Source: "build\staging\flmcp.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Comment: "Configurar FL MCP Studio"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar configuración ahora"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; Clean up runtime state. Do NOT delete user's claude_desktop_config.json — it
; was modified by us (with .bak) but is owned by Claude Desktop.
Type: filesandordirs; Name: "{userappdata}\FL MCP Studio"
Type: filesandordirs; Name: "{app}\python-embed\Lib\site-packages\__pycache__"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
