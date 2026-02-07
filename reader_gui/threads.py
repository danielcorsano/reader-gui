"""Background conversion thread."""

import sys
import threading
import time
import re
from io import StringIO
from pathlib import Path


class RealtimeStdoutCapture:
    """Capture stdout and parse progress in real-time."""

    def __init__(self, callback):
        self.callback = callback
        self.buffer = StringIO()
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 0.1  # Send updates every 100ms for smoother visualization

    def write(self, text):
        """Intercept write calls and parse for progress."""
        self.buffer.write(text)

        # Parse progress from text more aggressively
        # Look for various progress patterns: "chunk X/Y", "X/Y", "Processing chunk X"
        try:
            # Multiple pattern matching for better coverage
            match = re.search(r'(\d+)\s*/\s*(\d+)', text)  # Matches "X/Y" or "X / Y"
            if not match:
                match = re.search(r'chunk\s+(\d+).*?(\d+)', text, re.IGNORECASE)  # "chunk X of Y"

            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                elapsed = time.time() - self.start_time

                # Throttle updates to avoid flooding GUI (but still more frequent than before)
                current_time = time.time()
                if current_time - self.last_update < self.update_interval:
                    return
                self.last_update = current_time

                # Estimate speed and ETA
                if current > 0 and elapsed > 0:
                    speed = (current / elapsed) * 60  # chunks per minute
                    remaining = total - current
                    eta = (remaining / speed) * 60 if speed > 0 else 0

                    # Send progress event
                    self.callback('realtime_progress', {
                        'chunk': current,
                        'total': total,
                        'speed': speed,
                        'elapsed': elapsed,
                        'eta': eta
                    })
        except Exception:
            pass  # Ignore parsing errors

    def flush(self):
        """Flush buffer."""
        pass

    def getvalue(self):
        """Get captured output."""
        return self.buffer.getvalue()


class ConversionThread(threading.Thread):
    """Background thread for audiobook conversion."""

    def __init__(self, reader_instance, file_path, options, callback):
        super().__init__(daemon=True)
        self.reader = reader_instance
        self.file_path = Path(file_path)
        self.options = options
        self.callback = callback
        self.cancel_event = threading.Event()

    def run(self):
        """Run conversion in background."""
        old_stdout = sys.stdout
        debug = self.options.get('debug', False)

        try:
            # Redirect stdout to capture progress in real-time
            sys.stdout = RealtimeStdoutCapture(self.callback)

            convert_kwargs = {
                'file_path': str(self.file_path),
                'voice': self.options['voice'],
                'speed': self.options['speed'],
                'output_format': self.options['output_format'],
                'output_dir': self.options.get('output_dir')
            }

            # Add character voices if enabled
            if self.options.get('character_voices'):
                convert_kwargs['character_voices'] = True
                if self.options.get('character_config'):
                    convert_kwargs['character_config'] = self.options['character_config']
            # Use progress style from options (timeseries for visualization)
            if self.options.get('progress_style'):
                convert_kwargs['progress_style'] = self.options['progress_style']

            if debug:
                self.callback('debug', f"Starting conversion with: {convert_kwargs}")

            # Run conversion - backend handles all temp files and output location
            output_path = self.reader.convert(**convert_kwargs)

            # Get captured output
            progress_output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            # Send progress to GUI
            self.callback('progress', progress_output)
            self.callback('complete', str(output_path))

        except Exception as e:
            sys.stdout = old_stdout
            if debug:
                import traceback
                error_msg = f"{str(e)}\n\n[DEBUG] Traceback:\n{traceback.format_exc()}"
                self.callback('error', error_msg)
            else:
                self.callback('error', str(e))

    def cancel(self):
        """Request cancellation of the conversion."""
        self.cancel_event.set()
