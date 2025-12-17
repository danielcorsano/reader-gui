"""Startup diagnostics and error logging."""

import sys
import traceback
from pathlib import Path
from datetime import datetime
import platform
import os

from reader_gui.app_dirs import get_app_log_dir


class StartupLogger:
    """Log all startup activities to file and display errors."""

    def __init__(self):
        # Use proper platform-specific log directory
        log_dir = get_app_log_dir()
        self.log_file = log_dir / "startup.log"
        self.errors = []

        # Start fresh log for this session
        self._write_header()

    def _write_header(self):
        """Write session header."""
        with open(self.log_file, 'w') as f:
            f.write(f"=== Audiobook Reader GUI Startup Log ===\n")
            f.write(f"Session: {datetime.now()}\n")
            f.write(f"Platform: {platform.system()} {platform.release()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
            if getattr(sys, 'frozen', False):
                f.write(f"Bundle path: {getattr(sys, '_MEIPASS', 'N/A')}\n")
            f.write(f"CWD: {os.getcwd()}\n")
            f.write(f"PATH: {os.environ.get('PATH', 'N/A')}\n")
            f.write("=" * 50 + "\n\n")

    def log(self, message, level="INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_file, 'a') as f:
            f.write(log_line)

        # Also print to stderr for terminal debugging
        print(f"{log_line.rstrip()}", file=sys.stderr)

        if level == "ERROR":
            self.errors.append(message)

    def log_exception(self, exc, context=""):
        """Log an exception with full traceback."""
        exc_text = traceback.format_exc()
        self.log(f"EXCEPTION in {context}:\n{exc_text}", "ERROR")

    def get_errors(self):
        """Return all logged errors."""
        return self.errors

    def get_log_path_display(self):
        """Get user-friendly log path for display."""
        try:
            # Try to make path relative to home for cleaner display
            rel_path = self.log_file.relative_to(Path.home())
            return f"~/{rel_path}"
        except ValueError:
            # Path not relative to home, return as-is
            return str(self.log_file)


# Global logger instance
logger = StartupLogger()


def run_startup_diagnostics():
    """Run comprehensive startup diagnostics."""
    logger.log("Starting diagnostics")

    issues = []

    # 1. Check Python version
    logger.log(f"Checking Python version: {sys.version_info}")
    if sys.version_info < (3, 10):
        issues.append(f"Python version too old: {sys.version_info}. Need >= 3.10")

    # 2. Check critical imports
    logger.log("Checking critical imports...")

    try:
        import tkinter
        logger.log("✓ tkinter import OK")
    except ImportError as e:
        issues.append(f"tkinter import failed: {e}")
        logger.log_exception(e, "tkinter import")

    try:
        import ttkbootstrap
        logger.log("✓ ttkbootstrap import OK")
    except ImportError as e:
        issues.append(f"ttkbootstrap import failed: {e}")
        logger.log_exception(e, "ttkbootstrap import")

    try:
        import matplotlib
        logger.log("✓ matplotlib import OK")
    except ImportError as e:
        issues.append(f"matplotlib import failed: {e}")
        logger.log_exception(e, "matplotlib import")

    # 3. Check reader package
    logger.log("Checking reader package...")
    try:
        import reader
        logger.log(f"✓ reader import OK (version: {getattr(reader, '__version__', 'unknown')})")

        try:
            from reader import Reader
            logger.log("✓ Reader class import OK")

            try:
                r = Reader()
                logger.log("✓ Reader instance created OK")

                try:
                    voices = r.list_voices()
                    logger.log(f"✓ Reader.list_voices() OK ({len(voices)} voices)")
                except Exception as e:
                    issues.append(f"Reader.list_voices() failed: {e}")
                    logger.log_exception(e, "Reader.list_voices()")

            except Exception as e:
                issues.append(f"Reader instantiation failed: {e}")
                logger.log_exception(e, "Reader()")

        except ImportError as e:
            issues.append(f"Reader class import failed: {e}")
            logger.log_exception(e, "Reader class import")

    except ImportError as e:
        issues.append(f"reader package import failed: {e}")
        logger.log_exception(e, "reader package import")

    # 4. Check FFmpeg
    logger.log("Checking FFmpeg...")
    try:
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            logger.log(f"✓ FFmpeg found: {ffmpeg_path}")
        else:
            logger.log("⚠ FFmpeg not in PATH (will check common locations)", "WARN")

            # Check common locations
            from reader_gui.dependency_check import check_ffmpeg
            found, path = check_ffmpeg()
            if found:
                logger.log(f"✓ FFmpeg found at: {path}")
            else:
                logger.log("⚠ FFmpeg not found (will prompt user)", "WARN")
    except Exception as e:
        logger.log_exception(e, "FFmpeg check")

    # 5. Check models
    logger.log("Checking models...")
    try:
        from reader_gui.dependency_check import get_model_locations
        locations = get_model_locations()
        logger.log(f"Model search paths: {[str(p) for p in locations]}")

        model_found = False
        for location in locations:
            model = location / "kokoro-v1.0.onnx"
            voices = location / "voices-v1.0.bin"
            if model.exists() and voices.exists():
                logger.log(f"✓ Models found at: {location}")
                model_found = True
                break

        if not model_found:
            logger.log("⚠ Models not found (will download on first use)", "WARN")
    except Exception as e:
        logger.log_exception(e, "Model check")

    # 6. Check GUI creation
    logger.log("Testing GUI initialization...")
    try:
        import tkinter as tk
        test_root = tk.Tk()
        test_root.withdraw()
        logger.log("✓ Tkinter root window created OK")
        test_root.destroy()
    except Exception as e:
        issues.append(f"GUI initialization failed: {e}")
        logger.log_exception(e, "GUI test")

    logger.log("Diagnostics complete")
    logger.log(f"Issues found: {len(issues)}")

    return issues


def show_diagnostic_error(parent=None):
    """Show diagnostic error dialog with log file path.

    Args:
        parent: Parent window. If None, creates standalone window.
    """
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
    import subprocess

    # Create error window
    if parent is None:
        # No parent - create standalone root
        error_win = tk.Tk()
        is_standalone = True
    else:
        # Has parent - create toplevel
        error_win = tk.Toplevel(parent)
        is_standalone = False

    error_win.title("Startup Diagnostics - Errors Found")
    error_win.geometry("700x500")
    error_win.configure(bg="#000000")

    # Error message
    msg_frame = tk.Frame(error_win, bg="#000000")
    msg_frame.pack(fill=tk.X, padx=20, pady=20)

    tk.Label(
        msg_frame,
        text="The application encountered errors during startup:",
        bg="#000000",
        fg="#FFD700",
        font=("Monaco", 13, "bold")
    ).pack(anchor=tk.W)

    # Log viewer
    log_frame = tk.Frame(error_win, bg="#000000")
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    log_text = scrolledtext.ScrolledText(
        log_frame,
        bg="#000000",
        fg="#FFD700",
        font=("Monaco", 10),
        wrap=tk.WORD,
        height=20
    )
    log_text.pack(fill=tk.BOTH, expand=True)

    # Load and display log
    try:
        with open(logger.log_file, 'r') as f:
            log_content = f.read()
        log_text.insert("1.0", log_content)
    except Exception as e:
        log_text.insert("1.0", f"Failed to read log file: {e}")

    log_text.config(state=tk.DISABLED)

    # Buttons
    btn_frame = tk.Frame(error_win, bg="#000000")
    btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    tk.Label(
        btn_frame,
        text=f"Log: {logger.get_log_path_display()}",
        bg="#000000",
        fg="#888888",
        font=("Monaco", 10)
    ).pack(side=tk.LEFT)

    def copy_log_path():
        error_win.clipboard_clear()
        error_win.clipboard_append(str(logger.log_file))
        messagebox.showinfo("Copied", "Log path copied to clipboard")

    def open_log_file():
        """Open log file in default text editor (cross-platform)."""
        try:
            if platform.system() == 'Darwin':
                subprocess.run(['open', '-t', str(logger.log_file)])
            elif platform.system() == 'Windows':
                subprocess.run(['notepad', str(logger.log_file)])
            else:
                # Linux
                subprocess.run(['xdg-open', str(logger.log_file)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file: {e}")

    tk.Button(
        btn_frame,
        text="Open Log",
        command=open_log_file,
        bg="#FFD700",
        fg="#000000",
        font=("Monaco", 11),
        relief=tk.FLAT
    ).pack(side=tk.RIGHT, padx=5)

    tk.Button(
        btn_frame,
        text="Copy Log Path",
        command=copy_log_path,
        bg="#FFD700",
        fg="#000000",
        font=("Monaco", 11),
        relief=tk.FLAT
    ).pack(side=tk.RIGHT, padx=5)

    def continue_anyway():
        error_win.destroy()

    tk.Button(
        btn_frame,
        text="Continue Anyway",
        command=continue_anyway,
        bg="#FFD700",
        fg="#000000",
        font=("Monaco", 11),
        relief=tk.FLAT
    ).pack(side=tk.RIGHT, padx=5)

    if is_standalone:
        error_win.mainloop()
    elif parent:
        parent.wait_window(error_win)
