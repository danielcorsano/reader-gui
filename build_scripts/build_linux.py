"""Build Linux executable using PyInstaller."""

import PyInstaller.__main__
import sys
import os
import shutil
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
ICON_PATH = PROJECT_ROOT / "reader_gui" / "assets" / "icon.png"
ASSETS_PATH = PROJECT_ROOT / "reader_gui" / "assets"

def build_linux():
    """Build Linux executable."""

    # Change to project root for relative paths
    os.chdir(PROJECT_ROOT)

    # Check that reader package exists
    reader_path = PROJECT_ROOT.parent / "reader"
    if not reader_path.exists():
        print(f"\nERROR: Reader package not found at {reader_path}")
        print("   Make sure the reader package is in ../reader/")
        sys.exit(1)

    print(f"Found reader package at {reader_path}")

    # Clean dist directory before building
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        print(f"Cleaning {dist_dir}...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)

    args = [
        str(PROJECT_ROOT / "reader_gui" / "gui.py"),
        "--name=audiobook-reader-gui",
        "--onedir",
        f"--icon={ICON_PATH}",
        f"--add-data={ASSETS_PATH}:reader_gui/assets",  # Note: colon for Linux
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
        "--hidden-import=reader.utils.model_downloader",
        # GUI dependencies
        "--hidden-import=tkinter",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=queue",
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.backends.backend_tkagg",
        # GUI package modules
        "--hidden-import=reader_gui.startup_diagnostics",
        "--hidden-import=reader_gui.dependency_check",
        "--hidden-import=reader_gui.app_dirs",
        "--hidden-import=reader_gui.threads",
        # Dependency auto-download
        "--hidden-import=imageio_ffmpeg",
        # Core dependencies
        "--hidden-import=ebooklib",
        "--hidden-import=PyPDF2",
        "--hidden-import=kokoro_onnx",
        "--hidden-import=onnxruntime",
        "--hidden-import=pydub",
        "--hidden-import=yaml",
        # Collect data files
        "--collect-all=kokoro_onnx",
        "--collect-all=onnxruntime",
        "--collect-all=matplotlib",
        "--collect-all=ttkbootstrap",
        "--collect-all=reader",
        "--collect-all=espeakng_loader",
        "--collect-all=language_tags",
        "--collect-all=babel",
        "--collect-all=ebooklib",
        "--collect-all=tkinter",
        "--collect-all=_tkinter",
        "--noconfirm",
        "--clean",
    ]

    print("Building Linux executable...")
    print(f"Icon: {ICON_PATH}")
    print(f"Assets: {ASSETS_PATH}")

    PyInstaller.__main__.run(args)

    print("\nBuild complete!")
    print(f"Application bundle: {PROJECT_ROOT}/dist/audiobook-reader-gui/")
    print(f"Executable: {PROJECT_ROOT}/dist/audiobook-reader-gui/audiobook-reader-gui")
    print("\nTo test:")
    print("  ./dist/audiobook-reader-gui/audiobook-reader-gui")
    print("\nTo distribute:")
    print("  Create a .tar.gz archive:")
    print("    tar -czf audiobook-reader-gui-linux.tar.gz -C dist audiobook-reader-gui")
    print("  Or create an AppImage:")
    print("    See: https://appimage.org/")

if __name__ == "__main__":
    build_linux()
