"""Regressions for startup logging with Windows ANSI defaults."""
import builtins
import importlib
import io
import sys


def test_utf8_header_and_append_with_cp1252_defaults(tmp_path, monkeypatch):
    from reader_gui import app_dirs
    log_dir = tmp_path / "Logs 日本語 café"
    log_dir.mkdir()
    monkeypatch.setattr(app_dirs, "get_app_log_dir", lambda: log_dir)
    monkeypatch.chdir(log_dir)
    original_open = builtins.open
    def ansi_open(file, mode='r', *args, **kwargs):
        if 'b' not in mode and not args and 'encoding' not in kwargs:
            kwargs['encoding'] = 'cp1252'
        return original_open(file, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", ansi_open)
    # The module initializes its global logger during import.
    sys.modules.pop('reader_gui.startup_diagnostics', None)
    diagnostics = importlib.import_module('reader_gui.startup_diagnostics')
    encoded = io.BytesIO()
    stderr = io.TextIOWrapper(encoded, encoding='cp1252', errors='strict')
    monkeypatch.setattr(sys, 'stderr', stderr)
    message = '✓ tkinter import OK — 東京 café Мария العربية'
    diagnostics.logger.log(message)
    stderr.flush()
    content = diagnostics.logger.log_file.read_text(encoding='utf-8')
    assert str(log_dir) in content
    assert message in content
    assert message in encoded.getvalue().decode('utf-8')


def test_windowed_executable_without_stderr(tmp_path, monkeypatch):
    from reader_gui import startup_diagnostics
    monkeypatch.setattr(startup_diagnostics, 'get_app_log_dir', lambda: tmp_path)
    monkeypatch.setattr(sys, 'stderr', None)
    logger = startup_diagnostics.StartupLogger()
    logger.log('✓ Unicode works without a console: 日本語')
    assert '✓ Unicode works without a console: 日本語' in logger.log_file.read_text(encoding='utf-8')
