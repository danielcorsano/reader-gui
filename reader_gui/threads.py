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

    def write(self, text):
        """Intercept write calls and parse for progress."""
        self.buffer.write(text)

        # Parse progress from text (look for patterns like "chunk 10/100")
        # This is a simple parser - adjust based on actual output format
        if 'chunk' in text.lower() or 'progress' in text.lower():
            try:
                # Try to extract chunk numbers
                match = re.search(r'(\d+)/(\d+)', text)
                if match:
                    current = int(match.group(1))
                    total = int(match.group(2))
                    elapsed = time.time() - self.start_time

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

    def run(self):
        """Run conversion in background."""
        try:
            # Redirect stdout to capture progress in real-time
            old_stdout = sys.stdout
            sys.stdout = RealtimeStdoutCapture(self.callback)

            # Build reader options (save output_dir for later use)
            output_dir = Path(self.options.get('output_dir', Path.home() / "Downloads"))
            output_dir.mkdir(parents=True, exist_ok=True)

            # Convert file path to absolute before changing directory
            import os
            absolute_file_path = os.path.abspath(self.file_path)
            original_dir = os.getcwd()
            os.chdir(output_dir)

            convert_kwargs = {
                'file_path': absolute_file_path,
                'voice': self.options['voice'],
                'speed': self.options['speed'],
                'output_format': self.options['output_format']
            }

            # Add character voices if enabled
            if self.options.get('character_voices'):
                convert_kwargs['character_voices'] = True
                if self.options.get('character_config'):
                    convert_kwargs['character_config'] = self.options['character_config']
                if self.options.get('auto_assign'):
                    convert_kwargs['auto_assign'] = True

            # Set progress style (none works best with GUI)
            progress_style = self.options.get('progress_style', 'none')
            if progress_style != 'none':
                # Note: timeseries doesn't work well with stdout capture
                convert_kwargs['progress_style'] = 'simple'

            # Run conversion
            output_path = self.reader.convert(**convert_kwargs)

            # Restore original directory
            os.chdir(original_dir)

            # Get captured output
            progress_output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            # Send progress to GUI
            self.callback('progress', progress_output)
            self.callback('complete', str(output_path))

        except Exception as e:
            try:
                os.chdir(original_dir)
            except:
                pass
            sys.stdout = old_stdout
            self.callback('error', str(e))
