"""Startup dependency check for ffmpeg and model files."""

import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from pathlib import Path
import threading
import shutil
import platform
import os
import subprocess
import urllib.request
import traceback
import webbrowser

from reader_gui.app_dirs import get_app_config_dir

MODEL_BASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]


def augment_path_with_common_locations():
    """Add common package manager locations to PATH for .app environment."""
    common_paths = []

    if platform.system() == "Darwin":
        common_paths = ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin", "/sw/bin"]
    elif platform.system() == "Linux":
        common_paths = ["/usr/local/bin", "/snap/bin"]

    current_path = os.environ.get('PATH', '')
    path_parts = current_path.split(os.pathsep)

    for path in common_paths:
        if path not in path_parts and Path(path).exists():
            path_parts.insert(0, path)

    os.environ['PATH'] = os.pathsep.join(path_parts)


def get_model_locations():
    """Get possible model locations (package models/ and system cache)."""
    locations = []

    config_file = get_app_config_dir() / "models_path.conf"
    if config_file.exists():
        try:
            models_path = Path(config_file.read_text().strip())
            if models_path.exists():
                locations.append(models_path / "kokoro")
        except Exception:
            pass

    try:
        if getattr(sys, 'frozen', False):
            base_path = get_app_config_dir().parent
        else:
            base_path = Path(__file__).parent.parent

        package_models = base_path / "models" / "kokoro"
        if package_models.exists():
            locations.append(package_models)
    except Exception:
        pass

    if platform.system() == "Windows":
        cache = Path.home() / "AppData/Local/audiobook-reader/models/kokoro"
    elif platform.system() == "Darwin":
        cache = Path.home() / "Library/Caches/audiobook-reader/models/kokoro"
    else:
        cache = Path.home() / ".cache/audiobook-reader/models/kokoro"

    locations.append(cache)
    return locations


def check_ffmpeg():
    """Check if FFmpeg is installed using reliable methods."""
    env_path = os.environ.get('FFMPEG_PATH')
    if env_path:
        ffmpeg_bin = Path(env_path)
        if ffmpeg_bin.exists() and _is_executable(ffmpeg_bin):
            return True, str(ffmpeg_bin)

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path

    common_locations = []
    if platform.system() == "Darwin":
        common_locations = [
            Path("/opt/homebrew/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
            Path("/opt/local/bin/ffmpeg"),
            Path("/sw/bin/ffmpeg"),
            Path(Path.home() / ".local/bin/ffmpeg"),
        ]
    elif platform.system() == "Linux":
        common_locations = [
            Path("/usr/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
            Path("/snap/bin/ffmpeg"),
            Path(Path.home() / ".local/bin/ffmpeg"),
        ]
    elif platform.system() == "Windows":
        common_locations = [
            Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path(Path.home() / "scoop/apps/ffmpeg/current/bin/ffmpeg.exe"),
        ]

    for path in common_locations:
        if path.exists() and _is_executable(path):
            return True, str(path)

    return False, None


def _is_executable(path):
    return os.access(str(path), os.X_OK)


def check_dependencies():
    """Check for ffmpeg and model, return missing dependencies."""
    missing = []

    ffmpeg_found, ffmpeg_path = check_ffmpeg()
    if not ffmpeg_found:
        missing.append("ffmpeg")
    elif ffmpeg_path:
        ffmpeg_dir = str(Path(ffmpeg_path).parent)
        if ffmpeg_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

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
    """Modal popup for downloading missing dependencies — two-column layout with per-dep progress."""

    def __init__(self, parent, missing):
        super().__init__(parent)
        self.title("Dependency Downloader")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.configure(background="#000000")

        self.missing = list(missing)
        self.download_complete = threading.Event()
        self.parent = parent
        self.permanent_models = tk.BooleanVar(value=True)
        self._ffmpeg_resolved = "ffmpeg" not in missing
        self._model_resolved = "model" not in missing
        self._ffmpeg_error_tb = None
        self._model_error_tb = None

        if hasattr(parent, 'style'):
            style = parent.style
        else:
            style = ttk.Style()

        style.configure('Dep.TFrame', background='#000000')
        style.configure('Dep.TLabel', background='#000000', foreground='#FFD700', font=("Monaco", 13))
        style.configure('Dep.Bold.TLabel', background='#000000', foreground='#FFD700', font=("Monaco", 15, "bold"))
        style.configure('Dep.Ok.TLabel', background='#000000', foreground='#00CC44', font=("Monaco", 13))
        style.configure('Dep.TButton', background='#FFD700', foreground='#000000', font=("Monaco", 13),
                        borderwidth=0, relief='flat', focuscolor='none', padding=(8, 4))
        style.map('Dep.TButton',
                  background=[('disabled', '#555555'), ('active', '#FFFFFF'), ('!active', '#FFD700')],
                  foreground=[('disabled', '#888888'), ('active', '#000000'), ('!active', '#000000')])
        style.configure('Dep.TCheckbutton', background='#000000', foreground='#FFD700', font=("Monaco", 13),
                        focuscolor='#000000', borderwidth=0)
        style.map('Dep.TCheckbutton',
                  background=[('active', '#000000'), ('selected', '#000000')],
                  foreground=[('active', '#FFFFFF'), ('selected', '#FFFFFF'), ('!selected', '#FFD700')])
        style.configure('TProgressbar', troughcolor='#333333', background='#FFD700', thickness=16)

        # Top bar
        top = ttk.Frame(self, style='Dep.TFrame')
        top.pack(fill=tk.X, padx=15, pady=(12, 8))
        ttk.Label(top, text="Dependency Downloader", style='Dep.Bold.TLabel').pack(side=tk.LEFT)
        tk.Button(top, text="?", bg="#FFD700", fg="#000000", font=("Monaco", 13, "bold"),
                  relief="flat", cursor="hand2", padx=8,
                  command=self._open_help).pack(side=tk.RIGHT)

        # Divider
        tk.Frame(self, bg="#333333", height=1).pack(fill=tk.X, padx=15)

        # Two-column body
        body = ttk.Frame(self, style='Dep.TFrame')
        body.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        self.ffmpeg_col = ttk.Frame(body, style='Dep.TFrame')
        self.ffmpeg_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Frame(body, bg="#333333", width=1).pack(side=tk.LEFT, fill=tk.Y)

        self.model_col = ttk.Frame(body, style='Dep.TFrame')
        self.model_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self._build_ffmpeg_column()
        self._build_model_column()

        self.center_window()

    # ── Column builders ──────────────────────────────────────────────────────

    def _build_ffmpeg_column(self):
        col = self.ffmpeg_col

        ttk.Label(col, text="FFmpeg", style='Dep.Bold.TLabel').pack(pady=(0, 8))

        if self._ffmpeg_resolved:
            ttk.Label(col, text="✓ Already installed", style='Dep.Ok.TLabel').pack(pady=2)
        else:
            self.ffmpeg_dl_btn = ttk.Button(col, text="Auto Download", style='Dep.TButton',
                                            command=self._start_ffmpeg_download)
            self.ffmpeg_dl_btn.pack(pady=2)

            self.ffmpeg_progress = ttk.Progressbar(col, mode='indeterminate',
                                                   style='TProgressbar', length=220)
            # hidden until download starts

            self.ffmpeg_ok_label = ttk.Label(col, text="✓ Installed", style='Dep.Ok.TLabel')

            self.ffmpeg_error_label = ttk.Label(col, text="[!] Error — click for details",
                                                background='#000000', foreground='#FF4444',
                                                font=("Monaco", 13), cursor="hand2")
            self.ffmpeg_error_label.bind("<Button-1>", lambda e: self._show_ffmpeg_error())

        ttk.Button(col, text="Manual Install", style='Dep.TButton',
                   command=self._show_ffmpeg_manual).pack(pady=2)
        ttk.Button(col, text="Specify FFmpeg", style='Dep.TButton',
                   command=self.specify_ffmpeg_path).pack(pady=2)

    def _build_model_column(self):
        col = self.model_col

        ttk.Label(col, text="Models", style='Dep.Bold.TLabel').pack(pady=(0, 8))

        if self._model_resolved:
            ttk.Label(col, text="✓ Already installed", style='Dep.Ok.TLabel').pack(pady=2)
        else:
            self.model_dl_btn = ttk.Button(col, text="Auto Download", style='Dep.TButton',
                                           command=self._start_model_download)
            self.model_dl_btn.pack(pady=2)

            self.model_progress_var = tk.DoubleVar(value=0)
            self.model_progress = ttk.Progressbar(col, mode='determinate',
                                                  style='TProgressbar', length=220,
                                                  variable=self.model_progress_var)
            # hidden until download starts

            self.model_status_label = ttk.Label(col, text="", style='Dep.TLabel')
            # hidden until download starts

            self.model_ok_label = ttk.Label(col, text="✓ Models ready", style='Dep.Ok.TLabel')

            self.model_error_label = ttk.Label(col, text="[!] Error — click for details",
                                               background='#000000', foreground='#FF4444',
                                               font=("Monaco", 13), cursor="hand2")
            self.model_error_label.bind("<Button-1>", lambda e: self._show_model_error())

        ttk.Button(col, text="Manual Install", style='Dep.TButton',
                   command=self._show_models_manual).pack(pady=2)
        ttk.Button(col, text="Specify Models", style='Dep.TButton',
                   command=self.specify_models_path).pack(pady=2)

        self.model_perm_check = ttk.Checkbutton(
            col, text="Save permanently",
            variable=self.permanent_models, style='Dep.TCheckbutton')
        self.model_perm_check.pack(pady=(8, 2))

    # ── FFmpeg download ───────────────────────────────────────────────────────

    def _start_ffmpeg_download(self):
        self.ffmpeg_dl_btn.config(state="disabled")
        if hasattr(self, 'ffmpeg_error_label'):
            self.ffmpeg_error_label.pack_forget()
        self.ffmpeg_progress.pack(pady=4)
        self.ffmpeg_progress.start(10)
        threading.Thread(target=self._download_ffmpeg_worker, daemon=True).start()

    def _download_ffmpeg_worker(self):
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            ffmpeg_dir = str(Path(ffmpeg_exe).parent)

            if ffmpeg_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

            config_file = get_app_config_dir() / "ffmpeg_path.conf"
            config_file.write_text(ffmpeg_dir)

            self.after(0, self._on_ffmpeg_success)
        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda err=tb: self._on_ffmpeg_error(err))

    def _on_ffmpeg_success(self):
        self.ffmpeg_progress.stop()
        self.ffmpeg_progress.pack_forget()
        self.ffmpeg_ok_label.pack(pady=2)
        self._ffmpeg_resolved = True
        if "ffmpeg" in self.missing:
            self.missing.remove("ffmpeg")
        self._check_both_done()

    def _on_ffmpeg_error(self, tb):
        self._ffmpeg_error_tb = tb
        self.ffmpeg_progress.stop()
        self.ffmpeg_progress.pack_forget()
        self.ffmpeg_error_label.pack(pady=2)
        self.ffmpeg_dl_btn.config(state="normal")

    # ── Model download ────────────────────────────────────────────────────────

    def _start_model_download(self):
        self.model_dl_btn.config(state="disabled")
        if hasattr(self, 'model_error_label'):
            self.model_error_label.pack_forget()
        self.model_progress.pack(pady=4)
        self.model_status_label.pack()
        threading.Thread(target=self._download_model_worker, daemon=True).start()

    def _download_model_worker(self):
        try:
            target_dir = None
            if self.permanent_models.get():
                target_dir = get_app_config_dir() / "models"
                target_dir.mkdir(parents=True, exist_ok=True)

            cache = (target_dir or self._default_cache()) / "kokoro"
            cache.mkdir(parents=True, exist_ok=True)

            n_files = len(MODEL_FILES)
            for i, name in enumerate(MODEL_FILES):
                dest = cache / name
                if dest.exists():
                    self.after(0, lambda p=(i + 1) * (100 // n_files): self.model_progress_var.set(p))
                    continue
                offset = i * (100 // n_files)
                share = 100 // n_files

                def make_hook(off, sh):
                    def hook(block_num, block_size, total_size):
                        if total_size > 0:
                            pct = off + min(sh, block_num * block_size * sh / total_size)
                            self.after(0, lambda p=pct: self.model_progress_var.set(p))
                    return hook

                self.after(0, lambda n=name: self.model_status_label.config(text=f"Downloading {n}..."))
                urllib.request.urlretrieve(
                    f"{MODEL_BASE_URL}/{name}", dest,
                    reporthook=make_hook(offset, share)
                )

            self.after(0, lambda: self.model_progress_var.set(100))

            if target_dir:
                os.environ['AUDIOBOOK_READER_MODELS_DIR'] = str(target_dir)
                config_file = get_app_config_dir() / "models_path.conf"
                config_file.write_text(str(target_dir))

            self.after(0, self._on_model_success)
        except Exception:
            tb = traceback.format_exc()
            self.after(0, lambda err=tb: self._on_model_error(err))

    def _default_cache(self):
        if platform.system() == "Windows":
            return Path.home() / "AppData/Local/audiobook-reader/models"
        elif platform.system() == "Darwin":
            return Path.home() / "Library/Caches/audiobook-reader/models"
        else:
            return Path.home() / ".cache/audiobook-reader/models"

    def _on_model_success(self):
        self.model_progress.pack_forget()
        self.model_status_label.pack_forget()
        self.model_ok_label.pack(pady=2)
        self._model_resolved = True
        if "model" in self.missing:
            self.missing.remove("model")
        self._check_both_done()

    def _on_model_error(self, tb):
        self._model_error_tb = tb
        self.model_progress.pack_forget()
        self.model_status_label.pack_forget()
        self.model_error_label.pack(pady=2)
        self.model_dl_btn.config(state="normal")

    # ── Auto-close ────────────────────────────────────────────────────────────

    def _check_both_done(self):
        if self._ffmpeg_resolved and self._model_resolved:
            self.after(1500, self.close_popup)

    # ── Error display ─────────────────────────────────────────────────────────

    def _show_ffmpeg_error(self):
        if self._ffmpeg_error_tb:
            messagebox.showerror("FFmpeg Download Error", self._ffmpeg_error_tb, parent=self)

    def _show_model_error(self):
        if self._model_error_tb:
            messagebox.showerror("Model Download Error", self._model_error_tb, parent=self)

    # ── Manual install popups ─────────────────────────────────────────────────

    def _show_ffmpeg_manual(self):
        win = tk.Toplevel(self)
        win.title("FFmpeg Manual Install")
        win.configure(background="#000000")
        win.transient(self)
        win.grab_set()

        f = ttk.Frame(win, style='Dep.TFrame', padding=20)
        f.pack(fill=tk.BOTH, expand=True)

        system = platform.system()
        if system == "Darwin":
            cmds = ["brew install ffmpeg", "sudo port install ffmpeg"]
        elif system == "Linux":
            cmds = ["sudo apt install ffmpeg", "sudo dnf install ffmpeg"]
        else:
            cmds = []
        url = "https://ffmpeg.org/download.html"

        ttk.Label(f, text="Install FFmpeg with one of these commands:",
                  style='Dep.TLabel').pack(anchor="w", pady=(0, 8))

        for cmd in cmds:
            self._cmd_row(f, cmd)

        ttk.Label(f, text=f"Or download from: {url}",
                  style='Dep.TLabel').pack(anchor="w", pady=(10, 0))
        ttk.Button(f, text="Open in Browser", style='Dep.TButton',
                   command=lambda: webbrowser.open(url)).pack(anchor="w", pady=6)
        ttk.Button(f, text="Close", style='Dep.TButton',
                   command=win.destroy).pack(anchor="e", pady=(6, 0))

    def _show_models_manual(self):
        win = tk.Toplevel(self)
        win.title("Models Manual Install")
        win.configure(background="#000000")
        win.transient(self)
        win.grab_set()

        f = ttk.Frame(win, style='Dep.TFrame', padding=20)
        f.pack(fill=tk.BOTH, expand=True)

        system = platform.system()
        models_dir = str(get_app_config_dir() / "models" / "kokoro")

        ttk.Label(f, text="1. Create the models folder:",
                  style='Dep.TLabel').pack(anchor="w", pady=(0, 4))
        self._cmd_row(f, f'mkdir -p "{models_dir}"' if system != "Windows"
                      else f'mkdir "{models_dir}"')

        ttk.Label(f, text="2. Download the model files into that folder:",
                  style='Dep.TLabel').pack(anchor="w", pady=(10, 4))
        for name in MODEL_FILES:
            url = f"{MODEL_BASE_URL}/{name}"
            dest = f'"{models_dir}/{name}"' if system != "Windows" else f'"{models_dir}\\{name}"'
            self._cmd_row(f, f'curl -L -o {dest} "{url}"')

        ttk.Label(f, text="3. Use \"Specify Models\" to point the app to the folder.",
                  style='Dep.TLabel').pack(anchor="w", pady=(10, 0))
        ttk.Button(f, text="Close", style='Dep.TButton',
                   command=win.destroy).pack(anchor="e", pady=(12, 0))

    def _cmd_row(self, parent, cmd):
        """Row with a monospace command label and a Copy button."""
        row = ttk.Frame(parent, style='Dep.TFrame')
        row.pack(anchor="w", pady=2)
        tk.Label(row, text=cmd, bg="#111111", fg="#FFFFFF", font=("Monaco", 11),
                 padx=8, pady=4, justify="left").pack(side=tk.LEFT)
        ttk.Button(row, text="Copy", style='Dep.TButton',
                   command=lambda c=cmd: self._copy(c)).pack(side=tk.LEFT, padx=(6, 0))

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _open_help(self):
        webbrowser.open("https://github.com/danielcorsano/reader-gui")

    # ── Specify path methods ──────────────────────────────────────────────────

    def specify_ffmpeg_path(self):
        """Allow user to manually specify ffmpeg path."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select ffmpeg executable",
            filetypes=[("Executable", "ffmpeg*"), ("All files", "*")]
        )
        if not file_path:
            return

        ffmpeg_path = Path(file_path)
        try:
            result = subprocess.run([str(ffmpeg_path), '-version'], capture_output=True, timeout=3)
            if result.returncode == 0 and b'ffmpeg version' in result.stdout:
                ffmpeg_dir = str(ffmpeg_path.parent)
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                config_file = get_app_config_dir() / "ffmpeg_path.conf"
                config_file.write_text(ffmpeg_dir)
                if "ffmpeg" in self.missing:
                    self.missing.remove("ffmpeg")
                self._ffmpeg_resolved = True
                self._check_both_done()
            else:
                messagebox.showerror("Invalid File",
                                     "Selected file is not ffmpeg or failed to execute.",
                                     parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to verify ffmpeg: {e}", parent=self)

    def specify_models_path(self):
        """Allow user to manually specify models directory."""
        dir_path = filedialog.askdirectory(
            parent=self,
            title="Select models directory (should contain 'kokoro' folder)"
        )
        if not dir_path:
            return

        models_path = Path(dir_path)
        kokoro_path = models_path / "kokoro"
        model_file = kokoro_path / "kokoro-v1.0.onnx"
        voices_file = kokoro_path / "voices-v1.0.bin"

        if model_file.exists() and voices_file.exists():
            config_file = get_app_config_dir() / "models_path.conf"
            config_file.write_text(str(models_path))
            os.environ['AUDIOBOOK_READER_MODELS_DIR'] = str(models_path)
            if "model" in self.missing:
                self.missing.remove("model")
            self._model_resolved = True
            self._check_both_done()
        else:
            messagebox.showerror("Invalid Directory",
                                 f"Directory must contain:\nkokoro/kokoro-v1.0.onnx\nkokoro/voices-v1.0.bin\n\nFound: {dir_path}",
                                 parent=self)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def center_window(self):
        self.update_idletasks()
        width = 720
        height = 440
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def close_popup(self):
        self.download_complete.set()
        self.destroy()
        self.parent.lift()

    def _on_close(self):
        if messagebox.askyesno("Exit?",
                               "The application cannot run without these dependencies. Exit?",
                               parent=self):
            self.parent.destroy()
            sys.exit(0)


def run_dependency_check(parent):
    """Run check and show popup if needed. Returns True if dependencies are met."""
    import traceback

    try:
        from reader_gui.startup_diagnostics import logger
    except Exception:
        logger = None

    try:
        if logger:
            logger.log("Augmenting PATH with common locations...")
        augment_path_with_common_locations()

        ffmpeg_conf = get_app_config_dir() / "ffmpeg_path.conf"
        if ffmpeg_conf.exists():
            try:
                ffmpeg_dir = ffmpeg_conf.read_text().strip()
                if logger:
                    logger.log(f"Restoring FFmpeg PATH from config: {ffmpeg_dir}")
                if ffmpeg_dir and ffmpeg_dir not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
            except Exception as e:
                if logger:
                    logger.log(f"Failed to restore FFmpeg PATH: {e}", "WARN")
                print(f"Warning: Failed to restore FFmpeg PATH: {e}", file=sys.stderr)

        models_conf = get_app_config_dir() / "models_path.conf"
        if models_conf.exists():
            try:
                models_dir = models_conf.read_text().strip()
                if logger:
                    logger.log(f"Restoring models path from config: {models_dir}")
                if models_dir:
                    os.environ['AUDIOBOOK_READER_MODELS_DIR'] = models_dir
            except Exception as e:
                if logger:
                    logger.log(f"Failed to restore models path: {e}", "WARN")
                print(f"Warning: Failed to restore models path: {e}", file=sys.stderr)

        if logger:
            logger.log("Checking dependencies...")
        missing = check_dependencies()

        if not missing:
            if logger:
                logger.log("All dependencies satisfied")
            return True

        if logger:
            logger.log(f"Missing dependencies: {missing}", "WARN")

        if logger:
            logger.log("Showing dependency popup...")
        try:
            popup = DependencyPopup(parent, missing)
            parent.wait_window(popup)
        except Exception as popup_error:
            error_details = traceback.format_exc()
            if logger:
                logger.log_exception(popup_error, "dependency popup")
            print(f"ERROR: Dependency popup failed:\n{error_details}", file=sys.stderr)

            result = messagebox.askokcancel(
                "Missing Dependencies",
                f"Missing: {', '.join(missing)}\n\n"
                f"The dependency installer failed to load.\n\n"
                f"Please install manually:\n"
                f"- FFmpeg: brew install ffmpeg (macOS)\n"
                f"- Models will auto-download on first use\n\n"
                f"Error: {str(popup_error)}\n\n"
                f"Continue anyway?",
                parent=parent
            )
            return result if result else False

        if logger:
            logger.log("Re-checking dependencies after popup...")
        if not check_dependencies():
            if logger:
                logger.log("Dependencies now satisfied")
            return True
        else:
            if logger:
                logger.log("Dependencies still missing", "WARN")
            return False

    except Exception as e:
        error_details = traceback.format_exc()
        if logger:
            logger.log_exception(e, "run_dependency_check")
        print(f"ERROR: Dependency check failed:\n{error_details}", file=sys.stderr)

        try:
            from reader_gui.startup_diagnostics import logger
            log_path = logger.get_log_path_display()
        except Exception:
            log_path = "See application logs directory"

        messagebox.showerror(
            "Dependency Check Error",
            f"Error during dependency check:\n\n{str(e)}\n\n"
            f"Check startup log:\n{log_path}\n\n"
            "Or run from terminal:\n"
            "/Applications/AudiobookReader.app/Contents/MacOS/AudiobookReader"
        )
        return False
