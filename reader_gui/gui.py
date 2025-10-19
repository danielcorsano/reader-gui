"""Main GUI application for audiobook-reader."""

import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from pathlib import Path
import queue
import platform
import subprocess


class AudiobookReaderGUI(ttk.Window):
    """Main application window."""

    def __init__(self):
        super().__init__(
            themename="darkly",
            title="Audiobook Reader",
            size=(800, 900),
            resizable=(True, True)
        )

        # Customize theme to match convertext-gui (black/yellow Monaco)
        style = ttk.Style()

        # Base styles
        style.configure('TFrame', background='#000000')
        style.configure('TLabel', background='#000000', foreground='#FFD700', font=("Monaco", 13))
        style.configure('TLabelframe', background='#000000', foreground='#FFD700', font=("Monaco", 13), bordercolor='#FFD700')
        style.configure('TLabelframe.Label', background='#000000', foreground='#FFD700', font=("Monaco", 13, "bold"))

        # Buttons - yellow with white hover
        style.configure('TButton', background='#FFD700', foreground='#000000', font=("Monaco", 13),
                       borderwidth=0, relief='flat', focuscolor='none')
        style.map('TButton',
                 background=[('disabled', '#555555'), ('active', '#FFFFFF'), ('!active', '#FFD700')],
                 foreground=[('disabled', '#888888'), ('active', '#000000'), ('!active', '#000000')])

        # Convert button - large with hover
        style.configure('Convert.TButton',
                       font=("Monaco", 21, "bold"),
                       background="#FFD700",
                       foreground="#000000",
                       borderwidth=0,
                       relief='flat',
                       focuscolor='none')
        style.map('Convert.TButton',
                 background=[('active', '#FFFFFF'), ('!active', '#FFD700')],
                 foreground=[('active', '#000000'), ('!active', '#000000')])

        # Checkbuttons - yellow/white, no blue
        style.configure('TCheckbutton', background='#000000', foreground='#FFD700', font=("Monaco", 13),
                       focuscolor='#000000', borderwidth=0)
        style.map('TCheckbutton',
                 background=[('active', '#000000'), ('selected', '#000000')],
                 foreground=[('active', '#FFFFFF'), ('selected', '#FFFFFF'), ('!selected', '#FFD700')])

        # Radiobuttons - yellow/white, no blue
        style.configure('TRadiobutton', background='#000000', foreground='#FFD700', font=("Monaco", 13),
                       focuscolor='#000000', borderwidth=0, indicatorcolor='#FFD700')
        style.map('TRadiobutton',
                 background=[('active', '#000000'), ('selected', '#000000')],
                 foreground=[('active', '#FFFFFF'), ('selected', '#FFFFFF'), ('!selected', '#FFD700')],
                 indicatorcolor=[('selected', '#FFFFFF'), ('!selected', '#FFD700')])

        # Entry fields - no blue focus
        style.configure('TEntry', background='#000000', foreground='#FFD700', fieldbackground='#000000',
                       font=("Monaco", 13), insertcolor='#FFD700', bordercolor='#FFD700',
                       focuscolor='#FFD700', lightcolor='#FFD700', darkcolor='#FFD700')
        style.map('TEntry',
                 fieldbackground=[('focus', '#000000')],
                 foreground=[('focus', '#FFD700')],
                 bordercolor=[('focus', '#FFD700')])

        # Combobox - no blue
        style.configure('TCombobox', background='#000000', foreground='#FFD700', fieldbackground='#000000',
                       font=("Monaco", 13), bordercolor='#FFD700', arrowcolor='#FFD700',
                       focuscolor='#000000', selectbackground='#FFD700', selectforeground='#000000')
        style.map('TCombobox',
                 fieldbackground=[('focus', '#000000'), ('readonly', '#000000')],
                 foreground=[('focus', '#FFD700'), ('readonly', '#FFD700')],
                 bordercolor=[('focus', '#FFD700'), ('readonly', '#FFD700')],
                 selectbackground=[('readonly', '#FFD700')],
                 selectforeground=[('readonly', '#000000')])

        # Configure window
        self.configure(background='#000000')

        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                # PyInstaller bundle - assets in Resources/reader_gui/
                base_path = Path(sys._MEIPASS) / "reader_gui"
            else:
                # Running from source
                base_path = Path(__file__).parent

            icon_path = base_path / "assets" / "icon.png"
            if icon_path.exists():
                icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon)
        except Exception:
            pass

        # Initialize reader with bundled FFmpeg as fallback
        try:
            import imageio_ffmpeg
            import os
            ffmpeg_dir = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
            # Append to PATH (system ffmpeg takes priority if present)
            os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + ffmpeg_dir

            from reader import Reader
            self.reader = Reader()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize reader: {e}")
            sys.exit(1)

        # Variables
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.voice = tk.StringVar(value="am_michael")
        self.speed = tk.DoubleVar(value=1.0)
        self.output_format = tk.StringVar(value="mp3")
        self.character_voices_enabled = tk.BooleanVar(value=False)
        self.character_config_path = tk.StringVar()
        self.auto_assign_voices = tk.BooleanVar(value=False)
        self.progress_style = tk.StringVar(value="none")
        self.show_visualization = tk.BooleanVar(value=True)

        # State
        self.output_path = None
        self.progress_queue = queue.Queue()
        self.conversion_thread = None
        self.is_paused = False
        self._load_last_directory()

        self.setup_ui()
        self._center_window()
        self._process_queue()

    def setup_ui(self):
        """Build the interface."""
        # Main scrollable container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # File selection
        file_frame = ttk.LabelFrame(main_container, text="Input File", padding=8)
        file_frame.pack(fill=tk.X, padx=21, pady=(13, 5))

        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)

        # Output directory
        output_frame = ttk.LabelFrame(main_container, text="Output Directory", padding=8)
        output_frame.pack(fill=tk.X, padx=21, pady=5)

        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(output_frame, text="Open", command=self.open_output_folder).pack(side=tk.LEFT)

        # Voice and speed controls
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(fill=tk.X, padx=21, pady=5)

        # Voice selection
        voice_frame = ttk.LabelFrame(controls_frame, text="Voice", padding=8)
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        voices = self._get_voice_list()
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice, values=voices, state="readonly")
        voice_combo.pack(fill=tk.X)

        # Speed control
        speed_frame = ttk.LabelFrame(controls_frame, text="Speed", padding=8)
        speed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        speed_container = ttk.Frame(speed_frame)
        speed_container.pack(fill=tk.X)

        self.speed_label = ttk.Label(speed_container, text="1.0x")
        self.speed_label.pack(side=tk.RIGHT)

        speed_slider = ttk.Scale(
            speed_container,
            from_=0.5,
            to=2.0,
            variable=self.speed,
            command=self.update_speed_label,
            orient=tk.HORIZONTAL
        )
        speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Format and visualization
        options_frame = ttk.Frame(main_container)
        options_frame.pack(fill=tk.X, padx=21, pady=5)

        # Output format
        format_frame = ttk.LabelFrame(options_frame, text="Format", padding=8)
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        formats = ["mp3", "wav", "m4a", "m4b"]
        for fmt in formats:
            ttk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                variable=self.output_format,
                value=fmt
            ).pack(side=tk.LEFT, padx=8)

        # Visualization options
        viz_frame = ttk.LabelFrame(options_frame, text="Options", padding=8)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Checkbutton(
            viz_frame,
            text="Show Visualization",
            variable=self.show_visualization
        ).pack(anchor=tk.W, padx=8, pady=3)

        # Character voices
        char_frame = ttk.LabelFrame(main_container, text="Character Voices", padding=8)
        char_frame.pack(fill=tk.X, padx=21, pady=5)

        # Enable checkbox and auto-assign button
        top_row = ttk.Frame(char_frame)
        top_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Checkbutton(
            top_row,
            text="Enable Character Voices",
            variable=self.character_voices_enabled,
            command=self.toggle_character_config
        ).pack(side=tk.LEFT)

        ttk.Checkbutton(
            top_row,
            text="Auto-assign Voices",
            variable=self.auto_assign_voices
        ).pack(side=tk.LEFT, padx=(13, 0))

        # Config file selector
        char_config_container = ttk.Frame(char_frame)
        char_config_container.pack(fill=tk.X)

        ttk.Label(char_config_container, text="Config:").pack(side=tk.LEFT, padx=(0, 8))

        self.char_config_entry = ttk.Entry(
            char_config_container,
            textvariable=self.character_config_path,
            state="disabled"
        )
        self.char_config_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.char_config_btn = ttk.Button(
            char_config_container,
            text="Browse...",
            command=self.browse_character_config,
            state="disabled"
        )
        self.char_config_btn.pack(side=tk.LEFT)

        # Progress display - fixed height to keep Read button visible
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding=8)
        progress_frame.pack(fill=tk.X, padx=21, pady=5)

        # Visualization canvas (hidden by default)
        self.viz_container = ttk.Frame(progress_frame)
        self.viz_canvas = None
        self.viz_fig = None
        self.viz_ax = None
        self.viz_line = None
        self.time_history = None
        self.speed_history = None

        # Stats labels
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 5))

        self.progress_label = ttk.Label(stats_frame, text="")
        self.speed_label = ttk.Label(stats_frame, text="")
        self.eta_label = ttk.Label(stats_frame, text="")

        # Monospace text widget with scrollbar
        text_container = ttk.Frame(progress_frame)
        text_container.pack(fill=tk.X)

        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.progress_text = tk.Text(
            text_container,
            font=("Monaco", 10),
            bg="#000000",
            fg="#FFD700",
            wrap=tk.WORD,
            height=6,
            yscrollcommand=scrollbar.set
        )
        self.progress_text.pack(side=tk.LEFT, fill=tk.X)
        scrollbar.config(command=self.progress_text.yview)

        # Placeholder text
        self.progress_text.insert("1.0", "Ready to read. Select a file and click Read.\n")
        self.progress_text.config(state="disabled")

        # Big yellow Read button - centered, always visible
        convert_frame = ttk.Frame(main_container)
        convert_frame.pack(side=tk.BOTTOM, pady=13)

        self.convert_btn = ttk.Button(
            convert_frame,
            text="Read",
            command=self.toggle_conversion,
            style='Convert.TButton',
            width=13
        )
        self.convert_btn.pack()


    def _get_voice_list(self):
        """Get available voices grouped by language and sorted alphabetically."""
        try:
            voices = self.reader.list_voices()

            # Group voices by language
            from collections import defaultdict
            by_language = defaultdict(list)

            for vid, info in voices.items():
                lang = info.get('lang', 'unknown')
                gender = info.get('gender', 'unknown')
                name = info.get('name', vid)
                by_language[lang].append((name, vid, gender, lang))

            # Sort languages alphabetically, then voices within each language
            result = []
            for lang in sorted(by_language.keys()):
                # Sort voices alphabetically by name within language
                sorted_voices = sorted(by_language[lang], key=lambda x: x[0])
                for name, vid, gender, lang in sorted_voices:
                    result.append(f"{vid} ({gender}, {lang})")

            return result
        except Exception:
            return ["am_michael (male, en-us)"]

    def browse_file(self):
        """Open file dialog for input file."""
        filetypes = [
            ("All supported", "*.epub *.pdf *.txt *.md *.rst"),
            ("EPUB files", "*.epub"),
            ("PDF files", "*.pdf"),
            ("Text files", "*.txt"),
            ("Markdown files", "*.md"),
            ("RST files", "*.rst"),
        ]
        filename = filedialog.askopenfilename(title="Select file", filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
            self._check_auto_config()

    def browse_output_dir(self):
        """Open directory dialog for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
            self._save_last_directory()

    def _check_auto_config(self):
        """Check for auto-detected character config file."""
        if self.file_path.get():
            input_file = Path(self.file_path.get())
            auto_config = input_file.with_suffix('.characters.yaml')
            if auto_config.exists():
                self.character_config_path.set(str(auto_config))

    def browse_character_config(self):
        """Open file dialog for character config."""
        filename = filedialog.askopenfilename(
            title="Select character config",
            filetypes=[("YAML files", "*.yaml *.yml")]
        )
        if filename:
            self.character_config_path.set(filename)

    def toggle_character_config(self):
        """Enable/disable character config controls."""
        if self.character_voices_enabled.get():
            self.char_config_entry.config(state="normal")
            self.char_config_btn.config(state="normal")
        else:
            self.char_config_entry.config(state="disabled")
            self.char_config_btn.config(state="disabled")

    def update_speed_label(self, value):
        """Update speed display label."""
        self.speed_label.config(text=f"{float(value):.1f}x")

    def toggle_conversion(self):
        """Toggle between read and pause."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            # Currently running, so pause it
            self.pause_conversion()
        else:
            # Not running, so start/resume
            self.start_conversion()

    def start_conversion(self):
        """Start conversion."""
        # Validate
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file to convert")
            return

        # Extract voice ID from dropdown selection
        voice_selection = self.voice.get()
        voice_id = voice_selection.split()[0] if voice_selection else "am_michael"

        # Save last directory
        self._save_last_directory()

        # Build options
        options = {
            'voice': voice_id,
            'speed': self.speed.get(),
            'output_format': self.output_format.get(),
            'output_dir': self.output_dir.get(),
            'character_voices': self.character_voices_enabled.get(),
            'character_config': self.character_config_path.get() if self.character_voices_enabled.get() else None,
            'auto_assign': self.auto_assign_voices.get(),
            'progress_style': self.progress_style.get()
        }

        # Clear progress and update UI
        self.progress_text.config(state="normal")
        self.progress_text.delete("1.0", "end")
        self.progress_text.insert("end", f"Starting conversion...\n")
        self.progress_text.insert("end", f"Input: {Path(self.file_path.get()).name}\n")
        self.progress_text.insert("end", f"Voice: {voice_id}\n")
        self.progress_text.insert("end", f"Speed: {self.speed.get()}x\n")
        self.progress_text.insert("end", f"Format: {self.output_format.get().upper()}\n")
        self.progress_text.insert("end", f"Output: {self.output_dir.get()}\n\n")
        self.progress_text.config(state="disabled")

        # Change button to Pause
        self.is_paused = False
        self.convert_btn.config(text="Pause")

        # Setup visualization if enabled
        if self.show_visualization.get():
            self._setup_visualization()

        # Start thread
        try:
            from .threads import ConversionThread
        except ImportError:
            from threads import ConversionThread

        self.conversion_thread = ConversionThread(
            self.reader,
            self.file_path.get(),
            options,
            self._on_conversion_event
        )
        self.conversion_thread.start()

    def pause_conversion(self):
        """Pause ongoing conversion."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            self.conversion_thread.cancel()
            self.is_paused = True
            self.progress_text.config(state="normal")
            self.progress_text.insert("end", "\n\nPaused. Click Read to resume from checkpoint.\n")
            self.progress_text.config(state="disabled")
            self.convert_btn.config(text="Read")
            # Backend will save checkpoint before stopping, allowing resume

    def _on_conversion_event(self, event_type, data):
        """Handle conversion events from thread."""
        self.progress_queue.put((event_type, data))

    def _process_queue(self):
        """Process queue updates in main thread."""
        try:
            while True:
                event_type, data = self.progress_queue.get_nowait()

                if event_type == 'progress':
                    self.progress_text.config(state="normal")
                    self.progress_text.insert("end", data)
                    self.progress_text.see("end")
                    self.progress_text.config(state="disabled")

                elif event_type == 'realtime_progress':
                    # Update embedded visualization
                    if self.viz_canvas:
                        self._update_visualization(
                            data['chunk'],
                            data['total'],
                            data['speed'],
                            data['elapsed'],
                            data['eta']
                        )

                elif event_type == 'complete':
                    self.output_path = data
                    self.is_paused = False
                    self.conversion_thread = None
                    self.convert_btn.config(state="normal", text="Read")
                    self._cleanup_visualization()
                    messagebox.showinfo("Success", f"Conversion complete!\n\nOutput: {data}")

                elif event_type == 'error':
                    self.is_paused = False
                    self.conversion_thread = None
                    self.convert_btn.config(state="normal", text="Read")
                    self._cleanup_visualization()
                    messagebox.showerror("Error", f"Conversion failed:\n\n{data}")

        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_queue)

    def preview_audio(self):
        """Preview audio file."""
        if not self.output_path:
            messagebox.showwarning("Warning", "No audio file to preview")
            return

        try:
            if platform.system() == 'Darwin':
                subprocess.run(['open', self.output_path])
            elif platform.system() == 'Windows':
                subprocess.run(['start', self.output_path], shell=True)
            else:
                subprocess.run(['xdg-open', self.output_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open audio file:\n\n{e}")

    def open_output_folder(self):
        """Open output folder."""
        if self.output_path:
            folder = Path(self.output_path).parent
        elif self.file_path.get():
            folder = Path(self.file_path.get()).parent
        else:
            messagebox.showwarning("Warning", "No output folder to open")
            return

        try:
            if platform.system() == 'Darwin':
                subprocess.run(['open', str(folder)])
            elif platform.system() == 'Windows':
                subprocess.run(['explorer', str(folder)])
            else:
                subprocess.run(['xdg-open', str(folder)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n\n{e}")


    def _center_window(self):
        """Center window on screen, size based on content."""
        self.update_idletasks()

        # Let content determine height, set reasonable width
        width = 610

        # Get actual required height from packed widgets
        required_height = self.winfo_reqheight()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Don't exceed 85% of screen
        max_width = int(screen_width * 0.85)
        max_height = int(screen_height * 0.85)

        height = min(required_height + 50, max_height)
        if width > max_width:
            width = max_width

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.minsize(377, 610)

    def _load_last_directory(self):
        """Load last used directory from config."""
        config_file = Path.home() / ".audiobook-reader-gui.conf"
        if config_file.exists():
            try:
                last_dir = config_file.read_text().strip()
                if Path(last_dir).exists():
                    self.output_dir.set(last_dir)
            except Exception:
                pass

    def _save_last_directory(self):
        """Save last used directory to config."""
        config_file = Path.home() / ".audiobook-reader-gui.conf"
        try:
            config_file.write_text(self.output_dir.get())
        except Exception:
            pass

    def _setup_visualization(self):
        """Setup embedded matplotlib visualization."""
        from collections import deque
        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # Hide progress text when showing visualization
        self.progress_text.master.pack_forget()

        # Initialize data
        self.time_history = deque(maxlen=50)
        self.speed_history = deque(maxlen=50)
        self.time_history.append(0)
        self.speed_history.append(0)

        # Show stats labels
        self.progress_label.pack(side=tk.LEFT, padx=(0, 13))
        self.speed_label.pack(side=tk.LEFT, padx=(0, 13))
        self.eta_label.pack(side=tk.LEFT)

        # Create figure with constrained size to not push button off screen
        self.viz_fig = Figure(figsize=(5.5, 2), facecolor='#000000')
        self.viz_ax = self.viz_fig.add_subplot(111, facecolor='#000000')

        # Style
        self.viz_ax.set_xlabel('Time (min)', color='#FFD700', fontsize=9)
        self.viz_ax.set_ylabel('Speed (chunks/min)', color='#FFD700', fontsize=9)
        self.viz_ax.tick_params(colors='#FFD700', labelsize=8)
        self.viz_ax.grid(True, alpha=0.2, color='#555555')
        self.viz_ax.spines['bottom'].set_color('#FFD700')
        self.viz_ax.spines['left'].set_color('#FFD700')
        self.viz_ax.spines['top'].set_visible(False)
        self.viz_ax.spines['right'].set_visible(False)

        # Plot
        self.viz_line, = self.viz_ax.plot(
            list(self.time_history),
            list(self.speed_history),
            color='#FFD700',
            linewidth=2
        )
        self.viz_ax.set_xlim(0, 1)
        self.viz_ax.set_ylim(0, 10)

        # Embed in container with fixed height to prevent window resize
        self.viz_container.pack(fill=tk.X, pady=(0, 8))
        self.viz_canvas = FigureCanvasTkAgg(self.viz_fig, master=self.viz_container)
        self.viz_canvas.draw()
        canvas_widget = self.viz_canvas.get_tk_widget()
        canvas_widget.configure(height=160)  # Fixed pixel height
        canvas_widget.pack(fill=tk.X)

    def _update_visualization(self, chunk, total, speed, elapsed, eta):
        """Update embedded visualization."""
        if not self.viz_canvas:
            return

        # Update stats
        progress_pct = (chunk / total) * 100 if total > 0 else 0
        self.progress_label.config(text=f"Progress: {progress_pct:.1f}%")
        self.speed_label.config(text=f"Speed: {speed:.1f} chunks/min")
        eta_mins = int(eta // 60)
        eta_secs = int(eta % 60)
        self.eta_label.config(text=f"ETA: {eta_mins}m {eta_secs}s")

        # Update data
        time_mins = elapsed / 60
        self.time_history.append(time_mins)
        self.speed_history.append(speed)

        # Update plot
        self.viz_line.set_data(list(self.time_history), list(self.speed_history))

        # Auto-scale
        if len(self.time_history) > 1:
            max_time = max(self.time_history)
            max_speed = max(self.speed_history) if max(self.speed_history) > 0 else 10
            self.viz_ax.set_xlim(0, max(1, max_time * 1.1))
            self.viz_ax.set_ylim(0, max(10, max_speed * 1.2))

        self.viz_canvas.draw()

    def _cleanup_visualization(self):
        """Remove visualization after completion."""
        if self.viz_canvas:
            self.viz_container.pack_forget()
            self.viz_canvas = None
            self.viz_fig = None
            self.viz_ax = None
            self.viz_line = None
            self.progress_label.pack_forget()
            self.speed_label.pack_forget()
            self.eta_label.pack_forget()
            # Show progress text again
            self.progress_text.master.pack(fill=tk.X)


def main():
    """Entry point."""
    app = AudiobookReaderGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
