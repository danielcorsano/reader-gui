"""Build Windows .exe using PyInstaller."""

import PyInstaller.__main__
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
ICON_PATH = PROJECT_ROOT / "reader_gui" / "assets" / "icon.ico"

def build_windows():
    """Build Windows executable."""

    args = [
        str(PROJECT_ROOT / "reader_gui" / "gui.py"),
        "--name=AudiobookReader",
        "--noconsole",
        "--onefile",
        f"--icon={ICON_PATH}" if ICON_PATH.exists() else "",
        "--add-data=reader_gui/assets;reader_gui/assets",  # Note: semicolon for Windows
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
        # Collect data files
        "--collect-all=kokoro_onnx",
        "--collect-all=onnxruntime",
        "--collect-all=matplotlib",
        "--collect-all=ttkbootstrap",
        "--noconfirm",
        "--clean",
    ]

    # Remove empty icon arg if file doesn't exist
    args = [arg for arg in args if arg]

    print("Building Windows executable...")
    if ICON_PATH.exists():
        print(f"Icon: {ICON_PATH}")
    else:
        print("Warning: icon.ico not found, building without icon")

    PyInstaller.__main__.run(args)

    print("\nBuild complete!")
    print(f"Executable: {PROJECT_ROOT}/dist/AudiobookReader.exe")
    print("\nTo test:")
    print("  dist\\AudiobookReader.exe")

if __name__ == "__main__":
    build_windows()
