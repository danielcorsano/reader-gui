# Audiobook Reader GUI

Desktop GUI for [audiobook-reader](https://github.com/danielcorsano/reader). Convert ebooks and text files to audiobooks with realistic AI voices up to 8x faster than real-time.

## Download

**[Download latest release](https://github.com/danielcorsano/reader-gui/releases)**

- **macOS**: Download `AudiobookReader-macos.zip`, unzip, run `AudiobookReader.app`
- **Windows**: Download `AudiobookReader.exe` and run
- **Linux**: Download `AudiobookReader-linux.tar.gz`, extract, and run

## First Launch

The app checks for required dependencies on startup:

**FFmpeg** (audio encoding):
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Or use the app's automatic download

**Kokoro AI Models** (~310MB): Downloads automatically to system cache

## Features

- **48 AI Voices**: Kokoro-82M TTS (8 languages - English, Spanish, French, Italian, Portuguese, Japanese, Chinese, Hindi)
- **Multiple Formats**: EPUB, PDF, TXT, Markdown, RST → MP3/WAV/M4A/M4B
- **Character Voices**: Assign different voices to characters with auto-detection
- **Real-time Progress**: Speed charts, ETA, conversion metrics
- **Audio Preview**: Play output directly from app
- **Clean Design**: Monaco monospace, black/yellow theme

## Usage

1. Click **Browse** to select EPUB, PDF, or text file
2. Choose voice (default: am_michael)
3. Adjust speed (0.5x - 2.0x)
4. Select output format (MP3/WAV/M4A/M4B)
5. Optional: Enable **Character Voices** for dialogue
6. Click **Read** to start
7. Preview audio when complete

## Character Voices (Optional)

For books with dialogue, create `yourbook.characters.yaml` next to your ebook:

```yaml
characters:
  - name: Alice
    voice: af_sarah
  - name: Bob
    voice: am_michael
```

The app auto-detects this file, or browse to it manually.

## Requirements

- **macOS**: 10.15+ (Apple Silicon M1/M2/M3/M4 optimized)
- **Windows**: Windows 10+
- **Linux**: Ubuntu 20.04+ or equivalent
- **FFmpeg**: Required (see First Launch)

## Development

Build from source:

```bash
# Clone repos
git clone https://github.com/danielcorsano/reader.git
git clone https://github.com/danielcorsano/reader-gui.git

# Install
cd reader-gui
pip install -e ../reader
pip install -e .

# Run
python reader_gui/gui.py

# Build standalone app (requires pyinstaller)
pip install pyinstaller
python build_scripts/build_macos.py  # or build_windows.py, build_linux.py
```

## Support

If you like this product, please consider [supporting me](https://github.com/sponsors/danielcorsano). I created it and maintain it alone as a public service. Donations will be used to improve it and to develop requested features.

## License

MIT - See [LICENSE](LICENSE)

## Credits

- **TTS**: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad (Apache 2.0)
- **Backend**: [audiobook-reader](https://github.com/danielcorsano/reader)
