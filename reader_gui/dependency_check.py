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


def load_shell_path():
    """Try to load PATH from user's shell config."""
    if platform.system() != "Darwin" and platform.system() != "Linux":
        return

    shell_configs = [
        Path.home() / ".zshrc",
        Path.home() / ".bash_profile",
        Path.home() / ".profile",
    ]

    for config in shell_configs:
        if not config.exists():
            continue

        try:
            # Simple regex to extract PATH exports
            with open(config, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('export PATH=') or line.startswith('PATH='):
                        # Extract paths and add to current PATH
                        path_value = line.split('=', 1)[1].strip('\'"')
                        # Replace $PATH reference
                        if '$PATH' in path_value:
                            path_value = path_value.replace('$PATH', os.environ.get('PATH', ''))
                        os.environ['PATH'] = path_value
                        return
        except Exception:
            continue


def get_model_locations():
    """Get possible model locations (package models/ and system cache)."""
    locations = []

    # Check for manually specified model path
    config_file = Path.home() / ".audiobook-reader-gui-models.conf"
    if config_file.exists():
        try:
            models_path = Path(config_file.read_text().strip())
            if models_path.exists():
                locations.append(models_path / "kokoro")
        except Exception:
            pass

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
    checked_paths = []

    # 1. Check FFMPEG_PATH environment variable
    env_path = os.environ.get('FFMPEG_PATH')
    if env_path:
        ffmpeg_bin = Path(env_path)
        checked_paths.append(env_path)
        if ffmpeg_bin.exists() and _is_executable(ffmpeg_bin):
            return True, str(ffmpeg_bin)

    # 2. Check PATH with shutil.which
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path
    checked_paths.append("PATH")

    # 3. Try subprocess 'which' command (gets shell's PATH)
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            which_path = result.stdout.strip()
            if Path(which_path).exists():
                return True, which_path
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    # 4. Query package managers (macOS only)
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(['port', 'contents', 'ffmpeg'],
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if 'bin/ffmpeg' in line and not line.strip().endswith('/'):
                        pkg_path = Path(line.strip())
                        if pkg_path.exists() and _is_executable(pkg_path):
                            return True, str(pkg_path)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

    # 5. Check common installation locations
    common_locations = []

    if platform.system() == "Darwin":  # macOS
        common_locations = [
            Path("/opt/homebrew/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
            Path("/opt/local/bin/ffmpeg"),
            Path("/sw/bin/ffmpeg"),
            Path(Path.home() / ".local/bin/ffmpeg"),
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

    # Check each common location
    for path in common_locations:
        checked_paths.append(str(path))
        if path.exists() and _is_executable(path):
            return True, str(path)

    # Log checked paths only when not found (for debugging)
    print("FFmpeg not found. Checked:", ", ".join(checked_paths[:5]) + ("..." if len(checked_paths) > 5 else ""))

    return False, None


def _is_executable(path):
    """Check if a file is executable."""
    return os.access(str(path), os.X_OK)


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
        self.permanent_models = tk.BooleanVar(value=True)

        # Consistent styling
        style = ttk.Style()
        style.configure('Dep.TFrame', background='#000000')
        style.configure('Dep.TLabel', background='#000000', foreground='#FFD700', font=("Monaco", 13))
        style.configure('Dep.TButton', background='#FFD700', foreground='#000000', font=("Monaco", 13), padding=(10, 5))
        style.configure('Dep.TLabelframe', background='#000000', foreground='#FFD700', bordercolor='#FFD700')
        style.configure('Dep.TLabelframe.Label', background='#000000', foreground='#FFD700', font=("Monaco", 13, "bold"))
        style.configure('TProgressbar', troughcolor='#333333', background='#FFD700', thickness=20)
        style.configure('Dep.TCheckbutton', background='#000000', foreground='#FFD700', font=("Monaco", 11))

        main_frame = ttk.Frame(self, padding=20, style='Dep.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        missing_text = "Missing: " + ", ".join(missing)
        ttk.Label(main_frame, text=missing_text, style='Dep.TLabel').pack(pady=(0, 10))

        self.status_label = ttk.Label(main_frame, text="Click Download to install dependencies", style='Dep.TLabel')
        self.status_label.pack(pady=10)

        # Model location preference
        if "model" in self.missing:
            model_opts_frame = ttk.Frame(main_frame, style='Dep.TFrame')
            model_opts_frame.pack(pady=5)
            check = ttk.Checkbutton(
                model_opts_frame,
                text="Download models to app directory (permanent)",
                variable=self.permanent_models,
                style='Dep.TCheckbutton'
            )
            check.pack()

        self.progress = ttk.Progressbar(main_frame, mode='determinate', style='TProgressbar', length=400)
        self.progress.pack(pady=10)

        btn_frame = ttk.Frame(main_frame, style='Dep.TFrame')
        btn_frame.pack(pady=15)

        # Prominent "Specify Path" buttons for manual installation
        if "ffmpeg" in self.missing:
            specify_ffmpeg_btn = ttk.Button(btn_frame, text="Specify FFmpeg", command=self.specify_ffmpeg_path, style='Dep.TButton')
            specify_ffmpeg_btn.pack(side=tk.LEFT, padx=5)

        if "model" in self.missing:
            specify_models_btn = ttk.Button(btn_frame, text="Specify Models", command=self.specify_models_path, style='Dep.TButton')
            specify_models_btn.pack(side=tk.LEFT, padx=5)

        self.download_btn = ttk.Button(btn_frame, text="Auto Download", command=self.start_download, style='Dep.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self._on_close, style='Dep.TButton')
        cancel_btn.pack(side=tk.LEFT, padx=5)

        cmd_frame = ttk.Labelframe(main_frame, text="Alternative: Terminal Command", padding=10, style='Dep.TLabelframe')
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
                commands.append("brew install ffmpeg OR sudo port install ffmpeg OR download from ffmpeg.org")
            elif system == 'Linux':
                commands.append("sudo apt install ffmpeg OR download from ffmpeg.org")
            else:
                commands.append("Download from: https://ffmpeg.org/download.html")
        if "model" in self.missing:
            commands.append("Models auto-download on first use")
        return " | ".join(commands) if commands else "No manual steps needed."

    def copy_command(self):
        self.clipboard_clear()
        self.clipboard_append(self.terminal_cmd)
        messagebox.showinfo("Copied", "Command copied to clipboard.", parent=self)

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

        # Verify it's actually ffmpeg
        try:
            result = subprocess.run([str(ffmpeg_path), '-version'],
                                   capture_output=True, timeout=3)
            if result.returncode == 0 and b'ffmpeg version' in result.stdout:
                # Save to environment and config
                ffmpeg_dir = str(ffmpeg_path.parent)
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

                config_file = Path.home() / ".audiobook-reader-gui-ffmpeg.conf"
                config_file.write_text(ffmpeg_dir)

                # Remove ffmpeg from missing
                if "ffmpeg" in self.missing:
                    self.missing.remove("ffmpeg")

                if not self.missing:
                    self.status_label.config(text="FFmpeg configured successfully!")
                    self.progress['value'] = 100
                    self.after(1000, self.close_popup)
                else:
                    self.status_label.config(text="FFmpeg configured! Model will download on first use.")
                    self.progress['value'] = 50
            else:
                messagebox.showerror("Invalid File",
                                   "Selected file is not ffmpeg or failed to execute.",
                                   parent=self)
        except Exception as e:
            messagebox.showerror("Error",
                               f"Failed to verify ffmpeg: {e}",
                               parent=self)

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

        # Verify it contains kokoro models
        model_file = kokoro_path / "kokoro-v1.0.onnx"
        voices_file = kokoro_path / "voices-v1.0.bin"

        if model_file.exists() and voices_file.exists():
            # Save to config
            config_file = Path.home() / ".audiobook-reader-gui-models.conf"
            config_file.write_text(str(models_path))

            # Remove model from missing
            if "model" in self.missing:
                self.missing.remove("model")

            if not self.missing:
                self.status_label.config(text="Models configured successfully!")
                self.progress['value'] = 100
                self.after(1000, self.close_popup)
            else:
                self.status_label.config(text="Models configured! FFmpeg still needed.")
                self.progress['value'] = 50
        else:
            messagebox.showerror("Invalid Directory",
                               f"Directory must contain:\nkokoro/kokoro-v1.0.onnx\nkokoro/voices-v1.0.bin\n\nFound: {dir_path}",
                               parent=self)

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

        # Determine target directory based on user preference
        target_dir = None
        if self.permanent_models.get():
            # Download to app directory (permanent)
            if getattr(sys, 'frozen', False):
                # Bundled .app - use models/ next to executable
                target_dir = Path(sys._MEIPASS).parent / "models"
            else:
                # Development - use models/ in project root
                target_dir = Path(__file__).parent.parent / "models"
            target_dir.mkdir(parents=True, exist_ok=True)
            self.after(0, lambda: self.status_label.config(text=f"Downloading to {target_dir.name}/ (~310MB)..."))

        if not download_models(verbose=False, target_dir=target_dir):
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
    # Augment PATH with common package manager locations
    augment_path_with_common_locations()

    # Try loading PATH from shell configs
    load_shell_path()

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
