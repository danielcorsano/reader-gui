# Audiobook Reader v0.4.1

See [CHANGELOG](https://github.com/danielcorsano/reader-gui/blob/main/CHANGELOG.md) for version history.

## Downloads

- **macOS (Apple Silicon, 2020+)**: `AudiobookReader-arm64.dmg` - Download and mount. On first launch macOS will block it (unsigned app) — go to System Settings → Privacy & Security → Open Anyway, authenticate, then confirm Open.
- **macOS (Intel, pre-2020)**: `AudiobookReader-x64.dmg` - Same instructions as above.
- **Windows**: `AudiobookReader.exe` - Download and run
- **Linux**: `AudiobookReader-linux.tar.gz` - Extract and run

## Features
- **54 AI Voices in 9 Languages**: **American English** (20 voices), **British English** (8), **Japanese** (5), **Mandarin Chinese** (8), **Spanish** (3), **French** (1), **Hindi** (4), **Italian** (2), **Brazilian Portuguese** (3)
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