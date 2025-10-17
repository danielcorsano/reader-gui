# Audiobook Reader GUI

Desktop GUI application for [audiobook-reader](https://pypi.org/project/audiobook-reader/) converter with Monaco monospace typography and minimalist black/yellow design.

Convert text files and ebooks to high-quality audiobooks using neural TTS with real-time progress visualization and 48 professional voices.

## Features

- **File Conversion**: EPUB, PDF, TXT, Markdown, RST to audiobook
- **48 Voices**: Kokoro-82M neural TTS with 8 languages
- **Real-time Progress**: Live speed charts and ETA visualization
- **Character Voices**: Optional character-specific voice mapping
- **Audio Preview**: Play converted audiobook directly from GUI
- **Checkpoint Resume**: Continue interrupted conversions
- **Professional UI**: Monaco monospace, black/yellow theme
- **Cross-platform**: Windows, macOS, Linux

## Installation

### Option 1: Download Standalone App (Recommended)

Download the pre-built application for your platform:

- **macOS**: `AudiobookReader.app` (coming soon)
- **Windows**: `AudiobookReader.exe` (coming soon)
- **Linux**: `audiobook-reader-gui` (coming soon)

No Python installation required!

### Option 2: Run from Source

Requires Python 3.10-3.13 and the audiobook-reader package installed in `../reader`.

```bash
# Clone repository
git clone https://github.com/danielcorsano/reader-gui.git
cd reader-gui

# Install dependencies
poetry install

# Run application
poetry run audiobook-reader-gui
```

## Usage

1. **Select File**: Click "Browse..." to choose your EPUB, PDF, or text file
2. **Choose Voice**: Select from 48 neural voices (Male/Female, 8 languages)
3. **Adjust Speed**: Slide between 0.5x - 2.0x playback speed
4. **Select Format**: Choose MP3, WAV, M4A, or M4B output
5. **Optional**: Enable character voices and upload `.characters.yaml` config
6. **Convert**: Click "Convert" and watch real-time progress
7. **Preview**: When done, click "Preview" to play audiobook

### Keyboard Shortcuts

- `Ctrl+O` - Open file browser
- `Ctrl+Enter` - Start conversion
- `Ctrl+Q` or `Escape` - Quit application

## Character Voices

For books with dialogue, assign different voices to each character:

1. Create a `yourbook.characters.yaml` file:
```yaml
characters:
  - name: Alice
    voice: af_sarah
    gender: female
  - name: Bob
    voice: am_michael
    gender: male
```

2. Check "Enable Character Voices"
3. Browse to your `.characters.yaml` file
4. Convert as normal

The GUI auto-detects `filename.characters.yaml` files placed next to your input file.

## Supported Formats

### Input
- EPUB ebooks
- PDF documents
- Plain text (.txt)
- Markdown (.md)
- ReStructuredText (.rst)

**Need other formats?** Use [convertext](https://pypi.org/project/convertext/) to convert DOCX, MOBI, HTML, etc. first.

### Output
- MP3 (48kHz mono, default)
- WAV (uncompressed, high quality)
- M4A (Apple-friendly)
- M4B (audiobook format with chapters)

## Development

### Requirements
- Python 3.10-3.13
- Poetry for dependency management
- audiobook-reader package installed in `../reader`

### Setup
```bash
# Install dependencies
poetry install

# Install with build tools
poetry install --with build

# Run from source
poetry run python reader_gui/gui.py

# Run tests
poetry run pytest
```

### Building Standalone App

Build platform-specific executables using PyInstaller:

```bash
# Install build dependencies
poetry install --with build

# Build for macOS
poetry run python build_scripts/build_macos.py

# Build for Windows (on Windows)
poetry run python build_scripts/build_windows.py

# Build for Linux (on Linux)
poetry run python build_scripts/build_linux.py
```

Built applications will be in `dist/`:
- **macOS**: `AudiobookReader.app`
- **Windows**: `AudiobookReader.exe`
- **Linux**: `audiobook-reader-gui`

## Architecture

This GUI is a separate frontend for the audiobook-reader backend:

```toml
audiobook-reader = { path = "../reader", develop = true }
```

- GUI and backend developed independently
- GUI always uses latest backend from `../reader`
- No version coupling during development
- Single executable bundles both in production

## Troubleshooting

### "No module named _tkinter"
```bash
# macOS
brew install tcl-tk
pyenv install --force 3.13.3
poetry env remove --all
poetry install
```

### "Module 'reader' not found"
Ensure audiobook-reader is installed in `../reader`:
```bash
cd ../reader
poetry install
cd ../reader-gui
```

### Built app won't launch
- Check icon files exist in `reader_gui/assets/`
- Verify all hidden imports in build script
- Try `--onedir` instead of `--onefile` in PyInstaller

## Technical Details

- **Backend**: [audiobook-reader](https://pypi.org/project/audiobook-reader/) v0.1.6+
- **GUI Framework**: Tkinter + ttkbootstrap
- **Build Tool**: PyInstaller
- **Theme**: ttkbootstrap "darkly"
- **Font**: Monaco monospace
- **Threading**: Background conversion, non-blocking UI

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- **Backend**: [audiobook-reader](https://github.com/danielcorsano/reader)
- **TTS Model**: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad (Apache 2.0)
- **GUI Framework**: [ttkbootstrap](https://ttkbootstrap.readthedocs.io/)

## Support

- 📖 [Documentation](https://github.com/danielcorsano/reader-gui)
- 🐛 [Issue Tracker](https://github.com/danielcorsano/reader-gui/issues)
- 💬 [Discussions](https://github.com/danielcorsano/reader-gui/discussions)
