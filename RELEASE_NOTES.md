# Release Notes

---

## v0.3.0 (2025-11-13)

### Major Improvements

**Enhanced Dependency Detection**
- Multi-layer FFmpeg detection supports all package managers (Homebrew, MacPorts, Fink, manual installs)
- Shell PATH loading from `.zshrc`, `.bash_profile`, `.profile`
- Subprocess-based `which` command fallback
- Package manager query support (`port contents ffmpeg`)
- Proactive PATH augmentation with common locations

**Manual Dependency Configuration**
- "Specify FFmpeg" button to manually point to ffmpeg executable
- "Specify Models" button to specify existing model directory
- Persistent configuration via home directory config files
- Verification checks ensure specified paths are valid

**Model Download Options**
- Choice between app directory (permanent) and system cache
- Checkbox: "Download models to app directory (permanent)"
- Manual model specification for pre-downloaded models
- Config persistence across sessions

**Documentation Overhaul**
- New `IMPLEMENTATION_GUIDE.md` - technical decisions and lessons learned
- New `TODO.md` - task tracking and roadmap
- Consolidated plan documents, removed redundant files

**UI Improvements**
- Character Voices labeled "(beta)"
- Updated dependency popup with prominent manual options
- Better error messages showing checked paths
- Cleaner terminal command suggestions

### Technical Changes
- Reduced code bloat in FFmpeg detection
- Cleaned up unused imports
- Updated `.gitignore` for all config files
- Removed obsolete plan files

### Bug Fixes
- Fixed FFmpeg detection for MacPorts users
- Fixed bundled .app PATH inheritance issues
- Fixed dependency popup button layout

---

## v0.2.0 (2025-10-29)

Initial beta release with 54 voices, character voices, real-time visualization, and dependency management.

---

## Downloads

- **macOS**: `AudiobookReader-macos.zip` - Unzip and run
- **Windows**: `AudiobookReader.exe` - Download and run
- **Linux**: `AudiobookReader-linux.tar.gz` - Extract and run

## Features

- **54 AI Voices**: Kokoro-82M TTS (9 languages)
- **Multiple Formats**: EPUB, PDF, TXT, Markdown, RST → MP3/WAV/M4A/M4B
- **Character Voices (beta)**: Assign different voices to characters
- **Real-time Progress**: Speed charts, ETA, conversion metrics
- **Audio Preview**: Play output directly from app

## Requirements

- **macOS**: 10.15+ (Apple Silicon optimized)
- **Windows**: Windows 10+
- **Linux**: Ubuntu 20.04+ or equivalent
- **FFmpeg**: Required (app offers automatic download)
- **Kokoro Models**: ~310MB, downloads automatically on first use

## Support

[GitHub Sponsors](https://github.com/sponsors/danielcorsano)

## License

MIT
