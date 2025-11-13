# TODO - Audiobook Reader GUI

**Task tracking and feature roadmap**

---

## Current Status

**Version**: 0.2.0
**Status**: Feature-complete beta, ready for wider testing

---

## Active Tasks

### High Priority

- [ ] Test build on clean macOS system (no Homebrew, no Python)
- [ ] Test build on Windows 10/11
- [ ] Test build on Linux (Ubuntu 22.04/24.04)
- [ ] Verify all 54 voices work in built app
- [ ] Test character voices feature with sample EPUB
- [ ] Verify model download to permanent location works
- [ ] Test "Specify FFmpeg" and "Specify Models" buttons

### Medium Priority

- [ ] Add progress persistence (save/resume long conversions)
- [ ] Add batch conversion (multiple files)
- [ ] Add audio preview for voice selection
- [ ] Improve error messages for common issues
- [ ] Add dark/light theme toggle

### Low Priority

- [ ] Add keyboard shortcuts
- [ ] Add drag-and-drop file input
- [ ] Remember last selected voice
- [ ] Add conversion history log

---

## Bug Fixes

### Critical
- None known

### Minor
- [ ] Debug console doesn't wrap long lines
- [ ] Window position not saved between sessions
- [ ] Character voices checkbox label could be clearer

---

## Side Quests

### Documentation
- [ ] Create video tutorial (2-3 min)
- [ ] Add troubleshooting section to README
- [ ] Create CONTRIBUTING.md
- [ ] Add issue templates

### Quality of Life
- [ ] Add "Check for Updates" button
- [ ] Show estimated time before starting conversion
- [ ] Add "Recent Files" menu
- [ ] Add tooltips to UI elements

### Advanced Features
- [ ] Voice blending UI (currently CLI-only)
- [ ] Custom speed per chapter
- [ ] Emotion detection visualization
- [ ] Audio normalization options
- [ ] Chapter splitting UI

### Platform-Specific
- [ ] macOS: Add to Dock right-click menu
- [ ] Windows: Add to context menu (right-click EPUB)
- [ ] Linux: Create .desktop file
- [ ] All: File associations

---

## Release Checklist

### Pre-Release (v0.2.0)
- [x] FFmpeg detection for all package managers
- [x] Model download with permanent/cache option
- [x] Manual path specification for ffmpeg/models
- [x] Character voices (beta)
- [x] Real-time visualization
- [x] All 54 voices supported
- [ ] Test on all three platforms
- [ ] Update RELEASE_NOTES.md
- [ ] Build all platform binaries

### v0.3.0 Goals
- [ ] Batch conversion
- [ ] Progress persistence
- [ ] Audio preview
- [ ] Improved error handling

### v1.0.0 Goals (Stable)
- [ ] 1000+ downloads
- [ ] No critical bugs for 2 weeks
- [ ] Documentation complete
- [ ] All platforms tested
- [ ] Community feedback addressed

---

## Research & Exploration

### Potential Features to Investigate
- [ ] Cloud model hosting (reduce first-run download)
- [ ] Voice cloning integration
- [ ] GPU acceleration for faster conversion
- [ ] Integration with e-reader apps
- [ ] Browser extension for web-based ebooks
- [ ] Mobile app (iOS/Android)

### Performance Improvements
- [ ] Profile conversion performance
- [ ] Investigate faster audio encoding
- [ ] Parallel chunk processing
- [ ] Memory usage optimization

### Alternative Approaches
- [ ] Investigate Tauri instead of PyInstaller
- [ ] Consider webview-based UI
- [ ] Evaluate other TTS engines

---

## Known Limitations

### Current
- Windows antivirus may flag PyInstaller executables (false positive)
- First conversion is slower (model loading)
- Character voices requires manual YAML file
- No auto-update mechanism

### By Design
- No cloud storage integration
- No DRM removal (legal reasons)
- No audio editing features (out of scope)

---

## Tracking

### Last Updated
2025-11-13

### Next Review
Review this TODO weekly to update priorities and add new tasks.
