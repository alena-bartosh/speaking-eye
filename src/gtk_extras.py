from gi.repository import Gtk


def get_window_name(window: Gtk.Window) -> str:
    return window.get_name() if window else 'EMPTY WINDOW'
