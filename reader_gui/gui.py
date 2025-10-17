"""Main GUI application for audiobook-reader."""

import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from pathlib import Path


class AudiobookReaderGUI:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("Audiobook Reader")
        self.root.geometry("900x700")

        # Variables
        self.file_path = tk.StringVar()
        self.voice = tk.StringVar(value="af_sarah")
        self.speed = tk.DoubleVar(value=1.0)
        self.output_format = tk.StringVar(value="mp3")
        self.character_voices_enabled = tk.BooleanVar(value=False)
        self.character_config_path = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Build the interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Input File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(file_frame, text="Browse...", command=self.browse_file, bootstyle="warning").pack(side=tk.LEFT)

        # Voice and speed controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Voice selection
        voice_frame = ttk.LabelFrame(controls_frame, text="Voice", padding=10)
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        voices = self._get_voice_list()
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice, values=voices, state="readonly", width=30)
        voice_combo.pack(fill=tk.X)

        # Speed control
        speed_frame = ttk.LabelFrame(controls_frame, text="Speed", padding=10)
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
        speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Format and options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Output format
        format_frame = ttk.LabelFrame(options_frame, text="Output Format", padding=10)
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        formats = ["mp3", "wav", "m4a", "m4b"]
        for fmt in formats:
            ttk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                variable=self.output_format,
                value=fmt
            ).pack(side=tk.LEFT, padx=5)

        # Character voices
        char_frame = ttk.LabelFrame(options_frame, text="Character Voices", padding=10)
        char_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Checkbutton(
            char_frame,
            text="Enable",
            variable=self.character_voices_enabled,
            command=self.toggle_character_config
        ).pack(anchor=tk.W)

        char_config_container = ttk.Frame(char_frame)
        char_config_container.pack(fill=tk.X, pady=(5, 0))

        self.char_config_entry = ttk.Entry(
            char_config_container,
            textvariable=self.character_config_path,
            state="disabled",
            width=30
        )
        self.char_config_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.char_config_btn = ttk.Button(
            char_config_container,
            text="Browse...",
            command=self.browse_character_config,
            state="disabled",
            bootstyle="secondary"
        )
        self.char_config_btn.pack(side=tk.LEFT)

        # Progress display
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Monospace text widget with scrollbar
        text_container = ttk.Frame(progress_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.progress_text = tk.Text(
            text_container,
            font=("Monaco", 10),
            bg="#1a1a1a",
            fg="#ffd700",
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.progress_text.yview)

        # Placeholder text
        self.progress_text.insert("1.0", "Ready to convert. Select a file and click Convert.\n")
        self.progress_text.config(state="disabled")

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="Convert",
            command=self.start_conversion,
            bootstyle="warning",
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.preview_btn = ttk.Button(
            button_frame,
            text="Preview",
            command=self.preview_audio,
            state="disabled",
            bootstyle="success",
            width=15
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self.open_output_folder,
            bootstyle="secondary",
            width=20
        ).pack(side=tk.LEFT)

    def _get_voice_list(self):
        """Get available voices."""
        try:
            from reader import Reader
            r = Reader()
            voices = r.list_voices()
            return [f"{vid} ({info.get('gender', 'unknown')}, {info.get('language', 'unknown')})"
                   for vid, info in voices.items()]
        except Exception:
            # Fallback to sample voices if reader not available
            return ["af_sarah (female, en-us)", "am_michael (male, en-us)",
                   "bf_emma (female, en-gb)", "bm_george (male, en-gb)"]

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

    def start_conversion(self):
        """Start conversion (placeholder)."""
        self.progress_text.config(state="normal")
        self.progress_text.insert("end", "\n[Conversion logic not yet implemented]\n")
        self.progress_text.config(state="disabled")
        self.progress_text.see("end")

    def preview_audio(self):
        """Preview audio file (placeholder)."""
        pass

    def open_output_folder(self):
        """Open output folder (placeholder)."""
        pass


def main():
    """Entry point."""
    root = ttk.Window(themename="darkly")
    app = AudiobookReaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
