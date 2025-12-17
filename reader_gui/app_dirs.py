"""Application directory utilities for cross-platform file storage."""

import os
import platform
from pathlib import Path


def get_app_config_dir():
    """Get application config directory following platform conventions.

    Returns:
        Path: Platform-appropriate config directory
        - macOS: ~/Library/Application Support/audiobook-reader-gui
        - Windows: %APPDATA%/audiobook-reader-gui
        - Linux: ~/.config/audiobook-reader-gui
    """
    if platform.system() == 'Darwin':
        config_dir = Path.home() / "Library" / "Application Support" / "audiobook-reader-gui"
    elif platform.system() == 'Windows':
        config_dir = Path(os.environ.get('APPDATA', Path.home())) / "audiobook-reader-gui"
    else:
        # Linux/Unix
        config_dir = Path.home() / ".config" / "audiobook-reader-gui"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_app_log_dir():
    """Get application log directory following platform conventions.

    Returns:
        Path: Platform-appropriate log directory
        - macOS: ~/Library/Logs/audiobook-reader-gui
        - Windows: %LOCALAPPDATA%/audiobook-reader-gui/logs
        - Linux: ~/.local/state/audiobook-reader-gui
    """
    if platform.system() == 'Darwin':
        log_dir = Path.home() / "Library" / "Logs" / "audiobook-reader-gui"
    elif platform.system() == 'Windows':
        log_dir = Path(os.environ.get('LOCALAPPDATA', Path.home())) / "audiobook-reader-gui" / "logs"
    else:
        # Linux/Unix
        log_dir = Path.home() / ".local" / "state" / "audiobook-reader-gui"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_app_cache_dir():
    """Get application cache directory following platform conventions.

    Returns:
        Path: Platform-appropriate cache directory
        - macOS: ~/Library/Caches/audiobook-reader-gui
        - Windows: %LOCALAPPDATA%/audiobook-reader-gui/cache
        - Linux: ~/.cache/audiobook-reader-gui
    """
    if platform.system() == 'Darwin':
        cache_dir = Path.home() / "Library" / "Caches" / "audiobook-reader-gui"
    elif platform.system() == 'Windows':
        cache_dir = Path(os.environ.get('LOCALAPPDATA', Path.home())) / "audiobook-reader-gui" / "cache"
    else:
        # Linux/Unix
        cache_dir = Path.home() / ".cache" / "audiobook-reader-gui"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
