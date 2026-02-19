# Audiobook Reader v0.3.9

See [CHANGELOG](https://github.com/danielcorsano/reader-gui/blob/main/CHANGELOG.md) for version history.

## Downloads

- **macOS**: `AudiobookReader.dmg` - Download and mount. On first launch macOS will block it (unsigned app) — go to System Settings → Privacy & Security → Open Anyway, authenticate, then confirm Open.
- **Windows**: `AudiobookReader.exe` - Download and run
- **Linux**: `AudiobookReader-linux.tar.gz` - Extract and run

## Features
- 54 AI Voices: Kokoro-82M TTS (9 languages)
- Multiple Formats: EPUB, PDF, TXT, Markdown, RST → MP3/WAV/M4A/M4B. For other formats see the [ConverText app](https://github.com/danielcorsano/convertext-gui/releases) or the [CLI version on PyPI](https://pypi.org/project/convertext/).
- Character Voices (beta): Assign different voices to characters
- Real-time Progress: Speed charts, ETA, conversion metrics
- Audio Preview: Play output directly from app

## Requirements

- macOS 10.15+ (Apple Silicon optimized)
- Windows 10+
- Linux: Ubuntu 20.04+ or equivalent
- FFmpeg (app offers automatic download)
- Kokoro models (~310MB, downloads on first use)

If you like this, please consider supporting via [GitHub Sponsors](https://github.com/sponsors/danielcorsano). I created and maintain this alone.

## License
[MIT](https://github.com/danielcorsano/reader-gui/blob/main/LICENSE)