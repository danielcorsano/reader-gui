"""Startup dependency check for ffmpeg and model files."""

import sys
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from pathlib import Path
import threading
import shutil
import platform
from urllib.request import urlretrieve
import os

# Define model path using a robust method
try:
    # This is the ideal way, if reader is installed
    from reader.utils.setup import get_model_path
    MODEL_PATH = get_model_path()
except (ImportError, ModuleNotFoundError):
    # Fallback for bundled app or initial setup
    MODEL_PATH = Path.home() / ".local" / "share" / "reader" / "model.onnx"


def check_dependencies():
    """Check for ffmpeg and model, return missing dependencies."""
    missing = []
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")
    if not MODEL_PATH.exists():
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
...
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
        cmd_entry = ttk.Entry(cmd_frame, font=("Monaco", 11), style='Dep.TEntry')
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
            if system == 'Darwin': commands.append("brew install ffmpeg")
            elif system == 'Linux': commands.append("sudo apt update && sudo apt install ffmpeg")
            else: commands.append("winget install -e --id Gyan.FFmpeg")
        if "model" in self.missing:
            commands.append("python3 -m reader.download")
        return " && ".join(commands) or "No command available."

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
            if "model" in self.missing and not MODEL_PATH.exists():
                self._download_model()
            self.after(0, self.on_download_complete)
        except Exception as e:
            self.after(0, lambda: self.on_download_error(e))

    def _download_ffmpeg(self):
        self.after(0, lambda: self.status_label.config(text="Downloading FFmpeg..."))
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg_dir = str(Path(ffmpeg_exe).parent)
            if ffmpeg_dir not in os.environ.get('PATH', ''):
                 os.environ['PATH'] += os.pathsep + ffmpeg_dir
            self.after(0, lambda: self.progress.config(value=50))
        except Exception as e:
            raise RuntimeError(f"FFmpeg download failed: {e}")

    def _download_model(self):
        self.after(0, lambda: self.status_label.config(text="Downloading model (~100MB)..."))
        MODEL_URL = "https://github.com/danielcorsano/reader/releases/download/v0.1.15/model.onnx"
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(MODEL_URL, MODEL_PATH, self._progress_hook)

    def _progress_hook(self, count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        # Model is second half of progress bar
        value = 50 + (percent // 2)
        self.after(0, lambda: self.progress.config(value=value))
        self.after(0, lambda: self.status_label.config(text=f"Downloading model... {percent}%"))

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
    # Hide parent window during check
    parent.withdraw()
    missing = check_dependencies()
    if not missing:
        parent.deiconify()
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
