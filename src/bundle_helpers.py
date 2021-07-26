import os
import sys
from pathlib import Path


def is_frozen_bundle() -> bool:
    """Check whether work now with frozen bundle (PyInstaller executable file)"""
    return getattr(sys, 'frozen', False)


def get_current_dir() -> Path:
    """
    Get _MEIPASS dir in a packed-mode and
    local directory in unpacked (development) mode
    """
    current_dir = sys._MEIPASS if is_frozen_bundle() else os.path.dirname(os.path.abspath(__file__))

    return Path(current_dir)
