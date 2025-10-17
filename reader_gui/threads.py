"""Background conversion thread."""

import sys
import threading
from io import StringIO
from pathlib import Path


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
            # Redirect stdout to capture progress
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            # Build reader options
            output_dir = Path(self.options.get('output_dir', Path.home() / "Downloads"))
            output_dir.mkdir(parents=True, exist_ok=True)

            convert_kwargs = {
                'file_path': str(self.file_path),
                'voice': self.options['voice'],
                'speed': self.options['speed'],
                'output_format': self.options['output_format'],
                'output_dir': str(output_dir)
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

            # Get captured output
            progress_output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            # Send progress to GUI
            self.callback('progress', progress_output)
            self.callback('complete', str(output_path))

        except Exception as e:
            sys.stdout = old_stdout
            self.callback('error', str(e))
