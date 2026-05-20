# FL Studio Python Sandbox — Capability Test Results

**Date:** 2026-05-19
**Environment:**
- FL Studio 2024 Producer Edition v24.2.2 (build 4597)
- Wine, WINEPREFIX=`/home/roska/.flstudio_prefix`
- Python embedded: 3.12.1 (`MSC v.1937 64-bit AMD64`)
- Linux host: Kali

## Context

We attempted to start a TCP server (`bridge.server.BridgeServer`) inside the FL Studio MIDI controller script `device_Test Controller.py`. The server failed to bind a socket. To understand the scope of the FL Studio sandbox, we ran a capability test from inside the script.

## Test code

```python
# Capability tests run from inside device_Test Controller.py at module load time
import os, tempfile, threading, subprocess, sys
import socket as _sock_mod

# Test file write
test_file = os.path.join(tempfile.gettempdir(), 'fl_test.txt')
with open(test_file, 'w') as _f:
    _f.write('hello')

# Test threading
_t = threading.Thread(target=lambda: None, daemon=True)
_t.start()

# Test subprocess
subprocess.run([sys.executable, '-c', 'print("ok")'], capture_output=True, text=True, timeout=3)

# Test socket creation
_s = _sock_mod.socket(_sock_mod.AF_INET, _sock_mod.SOCK_STREAM)
_s.close()
_s2 = _sock_mod.socket()
_s2.close()

# Test reading Linux file via Wine Z: drive
with open('Z:\\etc\\hostname', 'rb') as _f:
    _hostname = _f.read().decode().strip()
```

## Results

| Operation | Result | Error |
|---|---|---|
| `open(temp_path, 'w').write(...)` | FAIL | `TypeError: bad argument type for built-in operation` |
| `threading.Thread(daemon=True).start()` | FAIL | `RuntimeError: daemon threads are disabled in this (sub)interpreter` |
| `subprocess.run([...])` | FAIL | `SystemError: <built-in function CreatePipe> returned NULL without setting an exception` |
| `socket.socket(AF_INET, SOCK_STREAM)` | FAIL | `SystemError: <slot wrapper '__init__' of '_socket.socket' objects> returned NULL without setting an exception` |
| `socket.socket()` | FAIL | (same as above) |
| `open('Z:\\etc\\hostname', 'rb').read()` | FAIL | `SystemError: <class '_io.FileIO'> returned NULL without setting an exception` |

## Diagnosis

**The "daemon threads are disabled in this (sub)interpreter" error is the smoking gun.** FL Studio runs each controller script in a Python sub-interpreter (PEP 684), which:

1. **Restricts the C extension import machinery.** Many C extensions (`_socket`, `_io`, `_subprocess` via `CreatePipe`) are not sub-interpreter safe, and Python explicitly refuses to instantiate their core types in sub-interpreters that opt into strict isolation. The `<class>.__init__` returns NULL without raising — this is the marker.

2. **Disables daemon threads.** PEP 684 sub-interpreters do not allow daemon threads, because daemons can survive the interpreter's lifecycle and corrupt shared state.

3. **Sandboxes file I/O.** `_io.FileIO` fails for the same reason — the C struct uses module state that the sub-interpreter doesn't have access to.

Verified externally: the same Python (`Shared/Python/python.exe`) invoked from a Wine shell creates sockets and files without issue. The restriction is specific to the in-process sub-interpreter that FL Studio spawns for the controller script.

## Implications

- **TCP socket bridge inside FL Studio script: impossible.**
- **Local file polling: impossible** (file I/O blocked).
- **Subprocess-based escape: impossible** (CreatePipe blocked).
- **Daemon threads: impossible** (only joinable threads allowed).

The only output-side communication channel that DOES work in this sandbox is what FL Studio's own API exposes, namely `device.midiOutMsg(message, port)` (sending MIDI to a host output) and the standard FL Studio Script API for manipulating the project.

## Recommendation

For any future return channel from FL Studio → Linux:
1. **Use the MIDI output back-channel.** Configure a second virtual MIDI port (e.g. `FL_MCP_RETURN`) that Linux listens to, and have the script call `device.midiOutMsg(...)` to push events. Limited to 3 bytes per message; rich data requires SysEx encoding.
2. **Or migrate off the sandboxed controller script.** Some FL Studio integrations use VST plugins (which DO have full system access) instead of MIDI controller scripts.
