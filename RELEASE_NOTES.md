# Audiobook Reader GUI v0.1.0-beta

Mac/Win/Linux Desktop version for [audiobook-reader](https://github.com/danielcorsano/reader). Convert ebooks and text files to audiobooks with realistic AI voices up to 8x faster than real-time.

**Documentation**: [Complete README](https://github.com/danielcorsano/reader-gui)
**CLI Version**: [audiobook-reader](https://github.com/danielcorsano/reader) (command-line interface)
**Report Issues**: [GitHub Issues](https://github.com/danielcorsano/reader-gui/issues)

## Beta Release Notice

Still in beta phase. Testing and feedback welcome, please report issues on GitHub.

## Downloads

- **macOS**: `AudiobookReader-macos.zip` - Unzip and run
- **Windows**: `AudiobookReader.exe` - Download and run
- **Linux**: `AudiobookReader-linux.tar.gz` - Extract and run

## Features

- **54 AI Voices**: Kokoro-82M TTS (9 languages - American & British English, Spanish, French, Italian, Portuguese, Japanese, Chinese, Hindi)
- **Multiple Formats**: EPUB, PDF, TXT, Markdown, RST → MP3/WAV/M4A/M4B
- **Character Voices**: Assign different voices to characters with auto-detection
- **Real-time Progress**: Speed charts, ETA, conversion metrics
- **Audio Preview**: Play output directly from app

## Requirements

- **macOS**: 10.15+ (Apple Silicon M1/M2/M3/M4 optimized)
- **Windows**: Windows 10+
- **Linux**: Ubuntu 20.04+ or equivalent
- **FFmpeg**: Required for audio encoding (app offers automatic download, or install via `brew install ffmpeg` / `sudo apt install ffmpeg`)
- **Kokoro Models**: ~310MB, downloads automatically to system cache on first use

## First Launch

The app checks for the presence of FFmpeg and voice models on startup. If they are missing, a dialog appears with download buttons. If this is not working for some reason, see README for manual install instructions.

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

MIT - See [LICENSE](https://github.com/danielcorsano/reader-gui/blob/main/LICENSE)

## Credits

- **TTS**: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad (Apache 2.0)
- **Backend**: [audiobook-reader](https://github.com/danielcorsano/reader)
