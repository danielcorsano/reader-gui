# Build Instructions

This guide explains how to build standalone executables for macOS, Windows, and Linux.

## Prerequisites

### All Platforms

1. **Python 3.10-3.13** installed
2. **Poetry** for dependency management
3. **Reader backend** in sibling directory:
   ```bash
   # Your directory structure should be:
   # parent/
   #   ├── reader/          # Backend package
   #   └── reader-gui/      # This repository
   ```

### Platform-Specific Requirements

#### macOS
- Xcode Command Line Tools: `xcode-select --install`
- For DMG creation: `hdiutil` (included with macOS)

#### Windows
- Microsoft Visual C++ 14.0 or greater
- PowerShell for packaging scripts

#### Linux
- Build essentials: `sudo apt-get install build-essential python3-dev`
- For AppImage (optional): See https://appimage.org/

## Installation

1. Clone both repositories:
   ```bash
   cd /path/to/parent
   git clone https://github.com/danielcorsano/reader.git
   git clone https://github.com/danielcorsano/reader-gui.git
   ```

2. Install dependencies:
   ```bash
   cd reader-gui
   poetry install --with build
   ```

## Building

### macOS

Build .app bundle and DMG:
```bash
poetry run python build_scripts/build_macos.py
```

Output:
- `dist/AudiobookReader.app` - Standalone application
- `dist/AudiobookReader.dmg` - Distributable disk image

To test:
```bash
open dist/AudiobookReader.app
```

### Windows

Build executable:
```bash
poetry run python build_scripts/build_windows.py
```

Package for distribution:
```bash
poetry run python build_scripts/package_windows.py
```

Output:
- `dist/AudiobookReader/` - Application directory
- `dist/AudiobookReader-{version}-Windows.zip` - Distributable archive

To test:
```cmd
.\dist\AudiobookReader\AudiobookReader.exe
```

### Linux

Build executable:
```bash
poetry run python build_scripts/build_linux.py
```

Package for distribution:
```bash
poetry run python build_scripts/package_linux.py
```

Output:
- `dist/audiobook-reader-gui/` - Application directory
- `dist/audiobook-reader-gui-{version}-Linux.tar.gz` - Distributable archive

To test:
```bash
./dist/audiobook-reader-gui/audiobook-reader-gui
```

## Build Configuration

### Hidden Imports

All build scripts include these critical hidden imports:

**Reader Backend:**
- `reader.*` - Core backend modules
- `reader.engines.kokoro_engine` - TTS engine
- `reader.parsers.*` - File format parsers
- `reader.utils.model_downloader` - Model download functionality

**GUI Modules:**
- `reader_gui.startup_diagnostics` - Startup diagnostics
- `reader_gui.dependency_check` - FFmpeg/model detection
- `reader_gui.app_dirs` - Platform directories
- `reader_gui.threads` - Background conversion

**Dependencies:**
- `imageio_ffmpeg` - FFmpeg auto-download
- `matplotlib` - Visualization
- `ttkbootstrap` - Modern UI theme

### Data Collection

All builds collect data files from:
- `reader` - Backend package
- `kokoro_onnx` - TTS models
- `onnxruntime` - ONNX runtime
- `espeakng_loader` - Phoneme data
- `matplotlib` - Plotting data
- `ttkbootstrap` - Theme files
- `language_tags`, `babel`, `ebooklib` - Locale/format data

## Distribution

### macOS

Distribute the DMG file:
1. Upload `dist/AudiobookReader.dmg` to GitHub releases
2. Users download and mount the DMG
3. Drag `AudiobookReader.app` to Applications folder

### Windows

Distribute the ZIP archive:
1. Upload `dist/AudiobookReader-{version}-Windows.zip` to GitHub releases
2. Users extract the ZIP
3. Run `AudiobookReader.exe` from extracted folder

Optional: Create installer with Inno Setup or similar

### Linux

Distribute the tar.gz archive:
1. Upload `dist/audiobook-reader-gui-{version}-Linux.tar.gz` to GitHub releases
2. Users extract: `tar -xzf audiobook-reader-gui-*.tar.gz`
3. Run: `./audiobook-reader-gui/audiobook-reader-gui`

Optional: Create AppImage for universal compatibility

## Troubleshooting

### "Reader package not found"
Ensure the `reader` package is in `../reader/` relative to this repository.

### "Module not found" errors
Add missing modules to hidden imports in the build script for your platform.

### Large executable size
This is normal. The app bundles:
- Python runtime
- All dependencies
- TTS engine (kokoro_onnx)
- Expect 200-400MB depending on platform

### FFmpeg/Models not bundled
This is intentional. The app:
1. Detects FFmpeg on system PATH
2. Auto-downloads FFmpeg if missing (via `imageio-ffmpeg`)
3. Auto-downloads TTS models on first use
4. Stores dependencies in platform-appropriate directories

This keeps the download size smaller and allows users to use their existing FFmpeg installation.

## Clean Build

To clean build artifacts:
```bash
rm -rf dist/ build/ *.spec
```

Then rebuild from scratch.

## Development Builds

For testing during development, run directly without building:
```bash
poetry run audiobook-reader-gui
```

This uses the source code and doesn't create standalone executables.
