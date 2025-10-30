# Audiobook Reader GUI v0.1.0-beta

Desktop GUI for [audiobook-reader](https://github.com/danielcorsano/reader). Convert ebooks and text files to audiobooks with realistic AI voices up to 8x faster than real-time.

## Beta Release Notice

First public release. Testing and feedback welcome, please report issues on GitHub.

## Downloads

- **macOS**: `AudiobookReader-macos.zip` - Unzip and run
- **Windows**: `AudiobookReader.exe` - Download and run
- **Linux**: `AudiobookReader-linux.tar.gz` - Extract and run

## Features

- **48 AI Voices**: Kokoro-82M TTS (8 languages - English, Spanish, French, Italian, Portuguese, Japanese, Chinese, Hindi)
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

## Links

- **Documentation**: [README](https://github.com/danielcorsano/reader-gui)
- **Backend CLI**: [audiobook-reader](https://github.com/danielcorsano/reader)
- **Report Issues**: [GitHub Issues](https://github.com/danielcorsano/reader-gui/issues)
- **TTS Credits**: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad (Apache 2.0)
