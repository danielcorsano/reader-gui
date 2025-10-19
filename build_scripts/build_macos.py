"""Build macOS .app bundle using PyInstaller."""

import PyInstaller.__main__
import sys
import os
from pathlib import Path
import shutil

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
ICON_PATH = PROJECT_ROOT / "reader_gui" / "assets" / "icon.icns"
ASSETS_PATH = PROJECT_ROOT / "reader_gui" / "assets"

def build_macos():
    """Build macOS application bundle."""

    # Change to project root for relative paths
    os.chdir(PROJECT_ROOT)

    # Check that reader package exists
    reader_path = PROJECT_ROOT.parent / "reader"
    if not reader_path.exists():
        print(f"\n❌ ERROR: Reader package not found at {reader_path}")
        print("   Make sure the reader package is in ../reader/")
        sys.exit(1)

    print(f"✓ Found reader package at {reader_path}")

    args = [
        str(PROJECT_ROOT / "reader_gui" / "gui.py"),
        "--name=AudiobookReader",
        "--windowed",
        "--onedir",
        f"--icon={ICON_PATH}",
        f"--add-data={ASSETS_PATH}{os.pathsep}reader_gui/assets",
        f"--paths={reader_path}",  # Tell PyInstaller where to find reader
        # Reader backend package
        "--hidden-import=reader",
        "--hidden-import=reader.cli",
        "--hidden-import=reader.api",
        "--hidden-import=reader.config",
        "--hidden-import=reader.engines",
        "--hidden-import=reader.engines.kokoro_engine",
        "--hidden-import=reader.parsers",
        "--hidden-import=reader.parsers.epub_parser",
        "--hidden-import=reader.parsers.pdf_parser",
        "--hidden-import=reader.parsers.text_parser",
        "--hidden-import=reader.interfaces",
        "--hidden-import=reader.interfaces.text_parser",
        "--hidden-import=reader.batch",
        "--hidden-import=reader.batch.neural_processor",
        "--hidden-import=reader.batch.batch_processor",
        "--hidden-import=reader.analysis",
        "--hidden-import=reader.analysis.emotion_detector",
        "--hidden-import=reader.analysis.dialogue_detector",
        "--hidden-import=reader.voices",
        "--hidden-import=reader.voices.character_mapper",
        "--hidden-import=reader.voices.voice_previewer",
        "--hidden-import=reader.processors",
        "--hidden-import=reader.processors.ffmpeg_processor",
        "--hidden-import=reader.chapters",
        "--hidden-import=reader.chapters.chapter_manager",
        "--hidden-import=reader.utils",
        "--hidden-import=reader.utils.setup",
        # GUI dependencies
        "--hidden-import=tkinter",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=queue",
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.backends.backend_tkagg",
        # Core dependencies
        "--hidden-import=ebooklib",
        "--hidden-import=PyPDF2",
        "--hidden-import=kokoro_onnx",
        "--hidden-import=onnxruntime",
        "--hidden-import=pydub",
        "--hidden-import=yaml",
        # Collect data files from dependencies
        "--collect-all=reader",  # Entire reader package
        "--collect-all=kokoro_onnx",
        "--collect-all=onnxruntime",
        "--collect-all=matplotlib",
        "--collect-all=ttkbootstrap",
        "--collect-all=language_tags",  # Fix for missing JSON data files
        "--collect-all=babel",  # Locale data
        "--collect-all=ebooklib",  # EPUB data
        # Exclude test frameworks and unused modules to reduce size
        "--exclude-module=pytest",
        "--exclude-module=pytest_cov",
        "--exclude-module=unittest",
        "--exclude-module=test",
        "--exclude-module=matplotlib.tests",
        "--exclude-module=PIL.tests",
        "--exclude-module=numpy.tests",
        "--noconfirm",
        "--clean",
    ]

    print("Building macOS application...")
    print(f"Icon: {ICON_PATH}")
    print(f"Assets: {ASSETS_PATH}")

    PyInstaller.__main__.run(args)

    # Clean up redundant AudiobookReader directory created by onedir mode
    redundant_dir = PROJECT_ROOT / "dist" / "AudiobookReader"
    if redundant_dir.exists():
        shutil.rmtree(redundant_dir)
        print(f"\nCleaned up: {redundant_dir}")

    print("\n✓ Build complete!")
    print(f"Application: {PROJECT_ROOT}/dist/AudiobookReader.app")
    print("\nTo test:")
    print("  open dist/AudiobookReader.app")

if __name__ == "__main__":
    build_macos()
