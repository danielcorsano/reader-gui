"""Main GUI application for audiobook-reader."""

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from pathlib import Path


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

        # Buttons
        style.configure('TButton', background='#FFD700', foreground='#000000', font=("Monaco", 13), borderwidth=0, relief='flat')

        # Convert button - large with hover
        style.configure('Convert.TButton',
                       font=("Monaco", 21, "bold"),
                       background="#FFD700",
                       foreground="#000000",
                       borderwidth=0,
                       relief='flat')
        style.map('Convert.TButton',
                 background=[('active', '#FFFFFF'), ('!active', '#FFD700')],
                 foreground=[('active', '#000000'), ('!active', '#000000')])

        # Checkbuttons
        style.configure('TCheckbutton', background='#000000', foreground='#FFD700', font=("Monaco", 13))

        # Radiobuttons
        style.configure('TRadiobutton', background='#000000', foreground='#FFD700', font=("Monaco", 13))

        # Entry fields
        style.configure('TEntry', background='#000000', foreground='#FFD700', fieldbackground='#000000',
                       font=("Monaco", 13), insertcolor='#FFD700')

        # Combobox
        style.configure('TCombobox', background='#000000', foreground='#FFD700', fieldbackground='#000000',
                       font=("Monaco", 13))

        # Configure window
        self.configure(background='#000000')

        # Variables
        self.file_path = tk.StringVar()
        self.voice = tk.StringVar(value="af_sarah")
        self.speed = tk.DoubleVar(value=1.0)
        self.output_format = tk.StringVar(value="mp3")
        self.character_voices_enabled = tk.BooleanVar(value=False)
        self.character_config_path = tk.StringVar()
        self.auto_assign_voices = tk.BooleanVar(value=False)
        self.progress_style = tk.StringVar(value="timeseries")

        self.setup_ui()
        self._center_window()

    def setup_ui(self):
        """Build the interface."""
        # File selection
        file_frame = ttk.LabelFrame(self, text="Input File", padding=13)
        file_frame.pack(fill=tk.X, padx=21, pady=21)

        ttk.Entry(file_frame, textvariable=self.file_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 13))
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)

        # Voice and speed controls
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=21, pady=13)

        # Voice selection
        voice_frame = ttk.LabelFrame(controls_frame, text="Voice", padding=13)
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        voices = self._get_voice_list()
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice, values=voices, state="readonly")
        voice_combo.pack(fill=tk.X)

        # Speed control
        speed_frame = ttk.LabelFrame(controls_frame, text="Speed", padding=13)
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
        speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 13))

        # Format and visualization
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, padx=21, pady=13)

        # Output format
        format_frame = ttk.LabelFrame(options_frame, text="Output Format", padding=13)
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        formats = ["mp3", "wav", "m4a", "m4b"]
        for fmt in formats:
            ttk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                variable=self.output_format,
                value=fmt
            ).pack(side=tk.LEFT, padx=13)

        # Visualization style
        viz_frame = ttk.LabelFrame(options_frame, text="Progress Visualization", padding=13)
        viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        viz_styles = ["timeseries", "simple", "none"]
        for style in viz_styles:
            ttk.Radiobutton(
                viz_frame,
                text=style.capitalize(),
                variable=self.progress_style,
                value=style
            ).pack(side=tk.LEFT, padx=13)

        # Character voices
        char_frame = ttk.LabelFrame(self, text="Character Voices", padding=13)
        char_frame.pack(fill=tk.X, padx=21, pady=13)

        # Enable checkbox and auto-assign button
        top_row = ttk.Frame(char_frame)
        top_row.pack(fill=tk.X, pady=(0, 8))

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
        ).pack(side=tk.LEFT, padx=(21, 0))

        # Config file selector
        char_config_container = ttk.Frame(char_frame)
        char_config_container.pack(fill=tk.X)

        ttk.Label(char_config_container, text="Config File:").pack(side=tk.LEFT, padx=(0, 8))

        self.char_config_entry = ttk.Entry(
            char_config_container,
            textvariable=self.character_config_path,
            state="disabled"
        )
        self.char_config_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 13))

        self.char_config_btn = ttk.Button(
            char_config_container,
            text="Browse...",
            command=self.browse_character_config,
            state="disabled"
        )
        self.char_config_btn.pack(side=tk.LEFT)

        # Progress display
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=13)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=21, pady=13)

        # Monospace text widget with scrollbar
        text_container = ttk.Frame(progress_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.progress_text = tk.Text(
            text_container,
            font=("Monaco", 10),
            bg="#000000",
            fg="#FFD700",
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.progress_text.yview)

        # Placeholder text
        self.progress_text.insert("1.0", "Ready to convert. Select a file and click Convert.\n")
        self.progress_text.config(state="disabled")

        # Big convert button
        self.convert_btn = ttk.Button(
            self,
            text="Convert",
            command=self.start_conversion,
            style='Convert.TButton',
            width=21
        )
        self.convert_btn.pack(pady=21)

        # Secondary action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=21, pady=(0, 21))

        self.preview_btn = ttk.Button(
            button_frame,
            text="Preview",
            command=self.preview_audio,
            state="disabled"
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 13))

        ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self.open_output_folder
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


    def _center_window(self):
        """Center window on screen."""
        self.update_idletasks()
        width = 800
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.minsize(700, 800)


def main():
    """Entry point."""
    app = AudiobookReaderGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
