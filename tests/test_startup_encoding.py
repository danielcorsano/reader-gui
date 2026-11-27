"""Regressions for startup logging with Windows ANSI defaults."""
import builtins
import importlib
import io
import sys

import pytest

MESSAGE = '✓ tkinter import OK — 東京 café Мария العربية'


@pytest.fixture
def cp1252_diagnostics(tmp_path, monkeypatch):
    """Fresh startup_diagnostics logging to a Unicode tmp dir, with cp1252 as the default file encoding."""
    from reader_gui import app_dirs
    log_dir = tmp_path / "Logs 日本語 café"
    log_dir.mkdir()
    original_open = builtins.open
    def ansi_open(file, mode='r', *args, **kwargs):
        if 'b' not in mode and not args and 'encoding' not in kwargs:
            kwargs['encoding'] = 'cp1252'
        return original_open(file, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", ansi_open)
    monkeypatch.setattr(app_dirs, "get_app_log_dir", lambda: log_dir)
    monkeypatch.chdir(log_dir)
    sys.modules.pop('reader_gui.startup_diagnostics', None)
    yield importlib.import_module('reader_gui.startup_diagnostics')
    sys.modules.pop('reader_gui.startup_diagnostics', None)


def test_unicode_log_with_cp1252_stderr(cp1252_diagnostics, monkeypatch):
    encoded = io.BytesIO()
    stderr = io.TextIOWrapper(encoded, encoding='cp1252', errors='backslashreplace')
    monkeypatch.setattr(sys, 'stderr', stderr)
    cp1252_diagnostics.logger.log(MESSAGE)
    stderr.flush()
    content = cp1252_diagnostics.logger.log_file.read_text(encoding='utf-8')
    assert str(cp1252_diagnostics.logger.log_file.parent) in content
    assert MESSAGE in content
    assert 'tkinter import OK' in encoded.getvalue().decode('cp1252')
    assert (stderr.encoding, stderr.errors) == ('cp1252', 'backslashreplace')


def test_windowed_executable_without_stderr(cp1252_diagnostics, monkeypatch):
    encoded = io.BytesIO()
    stdout = io.TextIOWrapper(encoded, encoding='cp1252', errors='strict')
    monkeypatch.setattr(sys, 'stderr', None)
    monkeypatch.setattr(sys, 'stdout', stdout)
    cp1252_diagnostics.logger.log(MESSAGE)
    stdout.flush()
    assert MESSAGE in cp1252_diagnostics.logger.log_file.read_text(encoding='utf-8')
    assert encoded.getvalue() == b''
