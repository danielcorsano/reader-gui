"""Real-time visualization window with matplotlib."""

import tkinter as tk
from collections import deque
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ttkbootstrap as ttk


class VisualizationWindow(tk.Toplevel):
    """Real-time processing speed visualization window."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Processing Visualization")
        self.geometry("900x600")
        self.configure(background='#000000')

        # Data storage
        self.time_history = deque(maxlen=50)
        self.speed_history = deque(maxlen=50)
        self.start_time = None

        # Initialize with zeros
        self.time_history.append(0)
        self.speed_history.append(0)

        self._setup_ui()

    def _setup_ui(self):
        """Build the visualization interface."""
        # Stats frame at top
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=21, pady=21)

        # Stats labels - Monaco font, yellow text
        self.progress_label = ttk.Label(
            stats_frame,
            text="Progress: 0%",
            font=("Monaco", 13),
            foreground="#FFD700",
            background="#000000"
        )
        self.progress_label.pack(side=tk.LEFT, padx=(0, 21))

        self.speed_label = ttk.Label(
            stats_frame,
            text="Speed: 0 chunks/min",
            font=("Monaco", 13),
            foreground="#FFD700",
            background="#000000"
        )
        self.speed_label.pack(side=tk.LEFT, padx=(0, 21))

        self.eta_label = ttk.Label(
            stats_frame,
            text="ETA: --",
            font=("Monaco", 13),
            foreground="#FFD700",
            background="#000000"
        )
        self.eta_label.pack(side=tk.LEFT)

        # Matplotlib figure
        self.fig = Figure(figsize=(9, 4), facecolor='#000000')
        self.ax = self.fig.add_subplot(111, facecolor='#000000')

        # Style the plot - yellow line, white text, black background
        self.ax.set_title('Processing Speed Over Time', color='#FFFFFF', fontsize=14, pad=15)
        self.ax.set_xlabel('Time (minutes)', color='#FFFFFF', fontsize=11)
        self.ax.set_ylabel('Speed (chunks/min)', color='#FFFFFF', fontsize=11)
        self.ax.tick_params(colors='#FFFFFF', labelsize=9)
        self.ax.grid(True, alpha=0.2, color='#555555')
        self.ax.spines['bottom'].set_color('#FFD700')
        self.ax.spines['left'].set_color('#FFD700')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        # Initial plot
        self.line, = self.ax.plot(
            list(self.time_history),
            list(self.speed_history),
            color='#FFD700',
            linewidth=2,
            marker='o',
            markersize=3
        )

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 10)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=21, pady=(0, 21))

    def update_progress(self, chunk, total, speed, elapsed, eta):
        """Update visualization with new progress data."""
        import time

        if self.start_time is None:
            self.start_time = time.time() - elapsed

        # Update stats labels
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
        self.line.set_data(list(self.time_history), list(self.speed_history))

        # Auto-scale axes
        if len(self.time_history) > 1:
            max_time = max(self.time_history)
            max_speed = max(self.speed_history) if max(self.speed_history) > 0 else 10
            self.ax.set_xlim(0, max(1, max_time * 1.1))
            self.ax.set_ylim(0, max(10, max_speed * 1.2))

        # Redraw
        self.canvas.draw()
        self.update()
