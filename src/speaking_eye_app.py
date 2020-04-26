from gi.repository import Wnck, Gtk, GObject

from gtk_extras import get_window_name


class SpeakingEyeApp(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.screen = None
        self.main_loop = None

    def do_activate(self) -> None:
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        active_window = screen.get_active_window()

        print(f'{get_window_name(previously_active_window)} -> {get_window_name(active_window)}')

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop_main_loop()

    def stop_main_loop(self) -> None:
        self.main_loop.quit()
