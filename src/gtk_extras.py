from typing import Optional, cast

from gi.repository import Gtk


def get_window_name(window: Optional[Gtk.Window]) -> str:
    return cast(str, window.get_name()) if window else 'EMPTY WINDOW'
