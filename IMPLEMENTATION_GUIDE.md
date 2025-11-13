# Audiobook Reader GUI - Implementation Guide

**Educational guide explaining technical choices, architecture patterns, and implementation techniques**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack Decisions](#technology-stack-decisions)
3. [Dependency Management Strategy](#dependency-management-strategy)
4. [Threading Model](#threading-model)
5. [Dependency Detection System](#dependency-detection-system)
6. [Build System](#build-system)
7. [Key Implementation Patterns](#key-implementation-patterns)
8. [Lessons Learned](#lessons-learned)

---

## Architecture Overview

### Separate Repository Pattern

**Decision**: GUI and backend in separate repositories

```toml
# pyproject.toml
audiobook-reader = { path = "../reader", develop = true }
```

**Why this approach:**
- **Independent deployment**: Users can use CLI or GUI independently
- **No version coupling**: GUI always uses latest backend during development
- **Simpler debugging**: Changes in backend immediately reflected in GUI
- **Cleaner separation**: Frontend concerns separate from backend logic

**Alternative considered**: Monorepo with shared codebase
- **Rejected because**: Would complicate CLI-only installations, harder to maintain separate release cycles

**Lesson**: For desktop apps wrapping CLI tools, separate repos with path dependencies provide flexibility without complexity.

---

## Technology Stack Decisions

### GUI Framework: Tkinter + ttkbootstrap

**Decision**: Use Tkinter instead of Qt, Electron, or web-based frameworks

**Why Tkinter:**
- **Zero external dependencies**: Ships with Python
- **Small bundle size**: No massive framework overhead (~50MB vs 200MB+ for Electron)
- **Cross-platform**: Works on macOS/Windows/Linux without platform-specific code
- **Simple threading**: Easy to run background tasks with Python's threading module

**Why ttkbootstrap:**
- **Modern styling**: Built-in dark themes, professional appearance
- **Tkinter-compatible**: Drop-in replacement for ttk widgets
- **Minimal overhead**: Just a theme layer, not a full framework

**Alternatives considered**:
- **PyQt/PySide**: Rejected due to licensing complexity and large binary size
- **Electron**: Rejected due to 200MB+ bundle size for simple app
- **Web (FastAPI + browser)**: Rejected due to complexity and requiring browser

**Lesson**: For simple desktop apps, standard library + thin styling layer beats heavy frameworks in size, simplicity, and maintainability.

---

### Build Tool: PyInstaller

**Decision**: PyInstaller for creating standalone executables

**Why PyInstaller:**
- **Single-file mode**: Can create `.app`, `.exe`, or Linux binary
- **Handles dependencies**: Automatically bundles Python packages
- **Hidden imports**: Can explicitly include dynamic imports
- **Cross-platform**: Same build script pattern for all OSes

**Configuration pattern**:
```python
# build_scripts/build_macos.py
pyi_args = [
    '--name=AudiobookReader',
    '--windowed',
    '--onefile',
    '--icon=reader_gui/assets/icon.icns',
    '--paths=' + str(reader_path),  # Tell PyInstaller where backend is
    '--collect-all=reader',  # Bundle entire backend package
    '--hidden-import=reader.engines.kokoro_engine',  # Dynamic imports
]
```

**Key technique**: Path dependency bundling requires:
1. `--paths` pointing to backend location
2. `--collect-all` to include all submodules
3. `--hidden-import` for any dynamically loaded modules

**Lesson**: When bundling packages with path dependencies, PyInstaller needs explicit configuration to find and include all modules.

---

## Dependency Management Strategy

### Runtime Dependencies: Download on Demand

**Decision**: Don't bundle FFmpeg or models in executable

**Why download on demand:**
- **Smaller initial download**: ~15MB app vs ~350MB with bundled dependencies
- **User choice**: Lets users with existing FFmpeg installations skip download
- **Version flexibility**: Can update models without rebuilding app
- **Cross-platform**: Avoids platform-specific bundling issues

**Implementation**: Startup dependency check
```python
def run_dependency_check(parent):
    augment_path_with_common_locations()  # Add /opt/local/bin, etc. to PATH
    load_shell_path()  # Load user's shell PATH

    missing = check_dependencies()
    if missing:
        popup = DependencyPopup(parent, missing)
        # Show modal popup with download/specify options
```

**Alternative considered**: Bundle everything
- **Rejected because**: 350MB download, no flexibility, harder updates

**Lesson**: For dependencies that users may already have installed, detection + download beats bundling.

---

## Dependency Detection System

### Multi-Layer FFmpeg Detection

**Problem**: macOS `.app` bundles don't inherit user's shell PATH, so system-installed FFmpeg isn't found

**Solution**: 5-layer detection strategy

```python
def check_ffmpeg():
    # Layer 1: FFMPEG_PATH environment variable (user override)
    if env_path := os.environ.get('FFMPEG_PATH'):
        if is_executable(env_path):
            return True, env_path

    # Layer 2: Standard PATH (shutil.which)
    if ffmpeg_path := shutil.which("ffmpeg"):
        return True, ffmpeg_path

    # Layer 3: Shell PATH (subprocess which)
    result = subprocess.run(['which', 'ffmpeg'], capture_output=True)
    if result.returncode == 0:
        return True, result.stdout.strip()

    # Layer 4: Package manager query
    result = subprocess.run(['port', 'contents', 'ffmpeg'], capture_output=True)
    # Parse output for binary path

    # Layer 5: Common installation paths
    for path in ['/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/opt/local/bin/ffmpeg']:
        if path.exists() and is_executable(path):
            return True, path
```

**Why this complexity:**
- **Layer 1**: Lets users override with environment variable
- **Layer 2**: Works for normal terminal usage
- **Layer 3**: Catches shell-specific PATHs (.zshrc, .bash_profile)
- **Layer 4**: Finds package manager installations even if not in PATH
- **Layer 5**: Fallback for known locations

**Key technique**: Augment PATH at startup
```python
def augment_path_with_common_locations():
    common_paths = ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin"]
    current_path = os.environ.get('PATH', '')
    for path in common_paths:
        if path not in current_path and Path(path).exists():
            os.environ['PATH'] = path + os.pathsep + current_path
```

**Lesson**: Desktop apps need aggressive PATH augmentation because they don't inherit user's shell environment.

---

### Persistent Configuration

**Pattern**: Store user preferences and paths in home directory

```python
# Save ffmpeg location for future sessions
config_file = Path.home() / ".audiobook-reader-gui-ffmpeg.conf"
config_file.write_text(ffmpeg_dir)

# Restore on next launch
if config_file.exists():
    ffmpeg_dir = config_file.read_text().strip()
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
```

**Why home directory:**
- **Survives reinstalls**: Config persists even if app is deleted
- **Cross-platform**: All OSes support `Path.home()`
- **User-specific**: Each user can have different settings

**Lesson**: For desktop apps, home directory config files are simpler than OS-specific config locations (AppData, Application Support, etc.).

---

## Threading Model

### Background Conversion with Queue Communication

**Problem**: Long-running conversion blocks UI if run on main thread

**Solution**: Background thread with queue-based communication

```python
# threads.py
class ConversionThread(threading.Thread):
    def __init__(self, queue, **kwargs):
        self.queue = queue
        self.kwargs = kwargs

    def run(self):
        try:
            result = reader.convert(**self.kwargs)
            self.queue.put(('success', result))
        except Exception as e:
            self.queue.put(('error', str(e)))

# gui.py
def start_conversion(self):
    self.queue = queue.Queue()
    thread = ConversionThread(self.queue, file_path=path, voice=voice)
    thread.start()
    self.check_queue()  # Poll queue every 100ms

def check_queue(self):
    try:
        msg_type, data = self.queue.get_nowait()
        if msg_type == 'success':
            self.on_conversion_complete(data)
    except queue.Empty:
        self.after(100, self.check_queue)  # Check again in 100ms
```

**Why queue.Queue:**
- **Thread-safe**: No race conditions
- **Simple**: No locks or semaphores needed
- **Tkinter-compatible**: Can poll from main thread safely

**Alternative considered**: asyncio
- **Rejected because**: Tkinter's event loop doesn't integrate well with asyncio

**Lesson**: For Tkinter apps, threading + Queue is simpler and more reliable than asyncio.

---

## Build System

### Hidden Imports for Dynamic Modules

**Problem**: PyInstaller can't detect modules loaded via `importlib` or string-based imports

**Solution**: Explicitly declare hidden imports

```python
# Backend uses: importlib.import_module(f'reader.parsers.{format}_parser')
# PyInstaller doesn't see this, so we declare:
'--hidden-import=reader.parsers.epub_parser',
'--hidden-import=reader.parsers.pdf_parser',
'--hidden-import=reader.parsers.txt_parser',
```

**Debugging technique**: If built app fails with `ModuleNotFoundError`:
1. Check error message for missing module name
2. Add `--hidden-import=<module>` to build script
3. Rebuild and test

**Lesson**: Any dynamically imported module needs explicit `--hidden-import` declaration.

---

### Path Dependency Bundling

**Problem**: PyInstaller doesn't know where to find `../reader` path dependency

**Solution**: Three-step configuration

```python
# 1. Tell PyInstaller where to look
'--paths=' + str(reader_path),

# 2. Bundle entire package
'--collect-all=reader',

# 3. Explicit imports for dynamic modules
'--hidden-import=reader.cli',
'--hidden-import=reader.engines.kokoro_engine',
```

**Why all three:**
- `--paths`: Tells PyInstaller where package is located
- `--collect-all`: Includes all submodules, even unused ones
- `--hidden-import`: Ensures dynamic imports are included

**Lesson**: Path dependencies require explicit configuration; PyInstaller can't infer them from pyproject.toml.

---

## Key Implementation Patterns

### Modal Startup Checks

**Pattern**: Block app launch until dependencies are satisfied

```python
def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # Run dependency check (shows modal popup if needed)
    run_dependency_check(root)

    # Only show main window after dependencies satisfied
    root.deiconify()
    root.mainloop()
```

**Why hide-then-show:**
- **Clean UX**: User sees dependency popup, not broken main window
- **Prevents errors**: Can't start conversion without dependencies
- **Progressive disclosure**: Show complexity only when needed

---

### Manual Path Specification

**Pattern**: Always provide manual fallback for auto-detection

```python
# DependencyPopup buttons
[Specify FFmpeg] [Specify Models] [Auto Download] [Cancel]
```

**Why manual option:**
- **Power users**: May have custom installations
- **Corporate environments**: May block downloads, require system-installed tools
- **Debugging**: Lets users override broken detection

**Implementation**:
```python
def specify_ffmpeg_path(self):
    file_path = filedialog.askopenfilename(title="Select ffmpeg executable")
    if not file_path:
        return

    # Verify it's actually ffmpeg
    result = subprocess.run([file_path, '-version'], capture_output=True)
    if b'ffmpeg version' in result.stdout:
        # Save to config
        config_file.write_text(str(Path(file_path).parent))
```

**Lesson**: Auto-detection should be convenient default, but always provide manual override.

---

## Lessons Learned

### 1. Desktop App PATH Issues

**Problem**: `.app` bundles don't inherit shell PATH

**Solution**: Aggressively augment PATH at startup with common locations

**Takeaway**: Desktop apps live in a different environment than terminal apps. Always augment PATH with known package manager locations.

---

### 2. Dependency Detection is Hard

**Problem**: Users install tools via different package managers (Homebrew, MacPorts, manual)

**Solution**: Multi-layer detection + manual override

**Takeaway**: Never assume one installation method. Provide multiple detection strategies and manual fallback.

---

### 3. Download > Bundle for Optional Dependencies

**Problem**: Bundling FFmpeg + models creates 350MB download

**Solution**: Detect or download on first run

**Takeaway**: For dependencies users may already have, detection beats bundling in size and flexibility.

---

### 4. Threading is Simpler Than Asyncio for Tkinter

**Problem**: Long-running tasks block UI

**Solution**: `threading.Thread` + `queue.Queue`

**Takeaway**: For Tkinter, traditional threading is simpler and more reliable than asyncio.

---

### 5. PyInstaller Needs Explicit Configuration

**Problem**: Path dependencies and dynamic imports not detected

**Solution**: `--paths`, `--collect-all`, `--hidden-import`

**Takeaway**: Don't rely on PyInstaller's auto-detection. Explicitly declare all dependencies.

---

## Technical Specifications

### Architecture Stack
- **Frontend**: Python 3.10+, Tkinter + ttkbootstrap
- **Backend**: audiobook-reader (path dependency)
- **Build**: PyInstaller
- **Threading**: stdlib threading + queue
- **Packaging**: Poetry

### File Structure
```
reader-gui/
├── reader_gui/
│   ├── gui.py              # Main Tkinter app
│   ├── threads.py          # Background conversion
│   ├── visualization.py    # matplotlib chart
│   └── dependency_check.py # Startup checks
├── build_scripts/          # PyInstaller configs
├── IMPLEMENTATION_GUIDE.md # This file
├── TODO.md                 # Task tracking
└── plan/
    └── release-plan.md     # Launch strategy
```

### Config Files (all in `~`)
- `.audiobook-reader-gui.conf` - Last output directory
- `.audiobook-reader-gui-ffmpeg.conf` - FFmpeg path
- `.audiobook-reader-gui-models.conf` - Models directory

---

## References

- **Backend**: https://github.com/danielcorsano/reader
- **Kokoro TTS**: https://huggingface.co/hexgrad/Kokoro-82M
- **ttkbootstrap**: https://ttkbootstrap.readthedocs.io/
- **PyInstaller**: https://pyinstaller.org/
