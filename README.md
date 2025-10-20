# Audiobook Reader GUI

Desktop GUI for [audiobook-reader](https://github.com/danielcorsano/reader). Convert ebooks and text files to audiobooks with realistic AI voices up to 8x faster than real-time.

## Features

- **48 Voices**: Kokoro-82M TTS (8 languages)
- **Multiple Input Formats**: EPUB, PDF, TXT, Markdown, RST → MP3/WAV/M4A/M4B
- **Character Voices**: Assign different voices to characters with auto-detection
- **Real-time Progress**: Timeseries visualization with speed graphs and ETA
- **Audio Preview**: Play output directly from GUI
- **Clean Design**: Monaco monospace, pure black/yellow theme

## Installation

### Run from Source

Requires Python 3.10-3.13 and the audiobook-reader package in `../reader`.

```bash
# Clone both repos
git clone https://github.com/danielcorsano/reader.git
git clone https://github.com/danielcorsano/reader-gui.git

# Install backend
cd reader && poetry install && cd ../reader-gui

# Install GUI
poetry install

# Run
poetry run python reader_gui/gui.py
```

## Usage

1. Click "Browse..." to select EPUB, PDF, or text file
2. Choose voice (default: am_michael)
3. Adjust speed (0.5x - 2.0x)
4. Select output format (MP3/WAV/M4A/M4B)
5. Optional: Enable character voices (auto-detects `.characters.yaml`)
6. Click **Convert**
7. Preview audio when complete

## Character Voices

Create `yourbook.characters.yaml`:
```yaml
characters:
  - name: Alice
    voice: af_sarah
  - name: Bob
    voice: am_michael
```

Enable "Character Voices" and browse to config, or place next to input file for auto-detection.

## Development

```bash
# Run from source
poetry run python reader_gui/gui.py

# Build standalone (macOS)
poetry install --with build
poetry run python build_scripts/build_macos.py
```

## Architecture

Separate frontend for audiobook-reader backend via path dependency:
```toml
audiobook-reader = { path = "../reader", develop = true }
```

## License

MIT
