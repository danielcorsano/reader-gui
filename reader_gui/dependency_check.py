"""Startup dependency check for ffmpeg and model files."""

import sys
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from pathlib import Path
import threading
import shutil
import platform
import os


def get_model_locations():
    """Get possible model locations (package models/ and system cache)."""
    locations = []

    # Package models/ directory (for development/bundled)
    try:
        if getattr(sys, 'frozen', False):
            # Running as bundled .app
            base_path = Path(sys._MEIPASS)
        else:
            # Running from source
            base_path = Path(__file__).parent.parent

        package_models = base_path / "models" / "kokoro"
        if package_models.exists():
            locations.append(package_models)
    except Exception:
        pass

    # System cache (standard location)
    if platform.system() == "Windows":
        cache = Path.home() / "AppData/Local/audiobook-reader/models/kokoro"
    elif platform.system() == "Darwin":
        cache = Path.home() / "Library/Caches/audiobook-reader/models/kokoro"
    else:
        cache = Path.home() / ".cache/audiobook-reader/models/kokoro"

    locations.append(cache)
    return locations


def check_ffmpeg():
    """Check if FFmpeg is installed in PATH or common locations."""
    # Check PATH first
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path

    # Check common installation locations
    common_locations = []

    if platform.system() == "Darwin":  # macOS
        common_locations = [
            Path("/opt/homebrew/bin/ffmpeg"),      # Apple Silicon Homebrew
            Path("/usr/local/bin/ffmpeg"),         # Intel Homebrew
            Path("/opt/local/bin/ffmpeg"),         # MacPorts
        ]
    elif platform.system() == "Windows":
        common_locations = [
            Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path(Path.home() / "scoop/apps/ffmpeg/current/bin/ffmpeg.exe"),
        ]
    else:  # Linux
        common_locations = [
            Path("/usr/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
            Path("/snap/bin/ffmpeg"),
            Path(Path.home() / ".local/bin/ffmpeg"),
        ]

    # Check each location
    for path in common_locations:
        if path.exists():
            return True, str(path)

    return False, None


def check_dependencies():
    """Check for ffmpeg and model, return missing dependencies."""
    missing = []

    # Check FFmpeg and add to PATH if needed
    ffmpeg_found, ffmpeg_path = check_ffmpeg()
    if not ffmpeg_found:
        missing.append("ffmpeg")
    elif ffmpeg_path:
        # Add to PATH if not already there (for bundled .app)
        ffmpeg_dir = str(Path(ffmpeg_path).parent)
        if ffmpeg_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

    # Check if models exist in any location
    model_found = False
    for location in get_model_locations():
        model = location / "kokoro-v1.0.onnx"
        voices = location / "voices-v1.0.bin"
        if model.exists() and voices.exists():
            model_found = True
            break

    if not model_found:
        missing.append("model")

    return missing


class DependencyPopup(tk.Toplevel):
    """Modal popup for downloading missing dependencies."""

    def __init__(self, parent, missing):
        super().__init__(parent)
        self.title("Missing Dependencies")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.configure(background="#000000")

        self.missing = missing
        self.download_complete = threading.Event()
        self.parent = parent

        # Consistent styling
        style = ttk.Style()
        style.configure('Dep.TFrame', background='#000000')
        style.configure('Dep.TLabel', background='#000000', foreground='#FFD700', font=("Monaco", 13))
        style.configure('Dep.TButton', background='#FFD700', foreground='#000000', font=("Monaco", 13), padding=(10, 5))
        style.configure('Dep.TLabelframe', background='#000000', foreground='#FFD700', bordercolor='#FFD700')
        style.configure('Dep.TLabelframe.Label', background='#000000', foreground='#FFD700', font=("Monaco", 13, "bold"))
        style.configure('TProgressbar', troughcolor='#333333', background='#FFD700', thickness=20)

        main_frame = ttk.Frame(self, padding=20, style='Dep.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        missing_text = "Missing: " + ", ".join(missing)
        ttk.Label(main_frame, text=missing_text, style='Dep.TLabel').pack(pady=(0, 10))

        self.status_label = ttk.Label(main_frame, text="Click Download to install dependencies", style='Dep.TLabel')
        self.status_label.pack(pady=10)

        self.progress = ttk.Progressbar(main_frame, mode='determinate', style='TProgressbar', length=400)
        self.progress.pack(pady=10)

        btn_frame = ttk.Frame(main_frame, style='Dep.TFrame')
        btn_frame.pack(pady=15)

        self.download_btn = ttk.Button(btn_frame, text="Download", command=self.start_download, style='Dep.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=10)
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_close, style='Dep.TButton')
        cancel_btn.pack(side=tk.LEFT, padx=10)

        cmd_frame = ttk.LabelFrame(main_frame, text="Alternative: Terminal Command", padding=10, style='Dep.TLabelframe')
        cmd_frame.pack(pady=10, fill=tk.X)

        self.terminal_cmd = self.get_terminal_command()
        cmd_entry = ttk.Entry(cmd_frame, font=("Monaco", 11))
        cmd_entry.insert(0, self.terminal_cmd)
        cmd_entry.config(state="readonly")
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        copy_btn = ttk.Button(cmd_frame, text="Copy", command=self.copy_command, style='Dep.TButton', width=8)
        copy_btn.pack(side=tk.LEFT)

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = 550
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def get_terminal_command(self):
        commands = []
        system = platform.system()
        if "ffmpeg" in self.missing:
            if system == 'Darwin':
                commands.append("brew install ffmpeg")
            elif system == 'Linux':
                commands.append("sudo apt install ffmpeg")
            else:
                commands.append("Download from: https://ffmpeg.org/download.html")
        if "model" in self.missing:
            commands.append("Models auto-download on first use")
        return " | ".join(commands) if commands else "No manual steps needed."

    def copy_command(self):
        self.clipboard_clear()
        self.clipboard_append(self.terminal_cmd)
        messagebox.showinfo("Copied", "Command copied to clipboard.", parent=self)

    def start_download(self):
        self.download_btn.config(state="disabled")
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        try:
            if "ffmpeg" in self.missing and not shutil.which("ffmpeg"):
                self._download_ffmpeg()
                self.after(0, lambda: self.progress.config(value=50))

            if "model" in self.missing:
                self._download_model()
                self.after(0, lambda: self.progress.config(value=100))

            self.after(0, self.on_download_complete)
        except Exception as e:
            self.after(0, lambda: self.on_download_error(e))

    def _download_ffmpeg(self):
        self.after(0, lambda: self.status_label.config(text="Downloading FFmpeg..."))
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = str(Path(ffmpeg_exe).parent)

        # Add to current PATH
        if ffmpeg_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

        # Save for future sessions
        config_file = Path.home() / ".audiobook-reader-gui-ffmpeg.conf"
        config_file.write_text(ffmpeg_dir)

    def _download_model(self):
        self.after(0, lambda: self.status_label.config(text="Downloading Kokoro models (~310MB)..."))
        from reader.utils.model_downloader import download_models

        # Downloads to package models/ if exists (dev), else system cache
        if not download_models(verbose=False):
            raise RuntimeError("Model download failed")

    def on_download_complete(self):
        self.status_label.config(text="All dependencies are installed!")
        self.progress['value'] = 100
        self.after(1000, self.close_popup)

    def on_download_error(self, e):
        messagebox.showerror("Download Failed", f"An error occurred: {e}\nPlease try the terminal command.", parent=self)
        self.status_label.config(text="Download failed. Please use terminal command.")
        self.download_btn.config(state="normal")

    def close_popup(self):
        self.download_complete.set()
        self.destroy()
        self.parent.lift()

    def _on_close(self):
        if messagebox.askyesno("Exit?", "The application cannot run without these dependencies. Exit?", parent=self):
            self.parent.destroy()
            sys.exit(0)

def run_dependency_check(parent):
    """Run check and show popup if needed. Returns True if dependencies are met."""
    # Restore FFmpeg PATH from previous session
    ffmpeg_conf = Path.home() / ".audiobook-reader-gui-ffmpeg.conf"
    if ffmpeg_conf.exists():
        try:
            ffmpeg_dir = ffmpeg_conf.read_text().strip()
            if ffmpeg_dir and ffmpeg_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
        except Exception:
            pass

    missing = check_dependencies()
    if not missing:
        parent.deiconify()
        parent.lift()
        parent.focus_force()
        return True

    popup = DependencyPopup(parent, missing)
    parent.wait_window(popup)

    # After popup, re-check and decide whether to show main window
    if not check_dependencies():
        parent.deiconify()
        return True
    else:
        parent.destroy()
        sys.exit(0)
