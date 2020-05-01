import os
from datetime import datetime, timedelta
from gi.repository import Wnck, Gtk, GObject

from gtk_extras import get_window_name
from tray_icon import TrayIcon
from x_helpers import get_wm_class

APP_ID = 'speaking-eye'
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_ICON = os.path.join(SRC_DIR, '../icon/active.png')


class SpeakingEyeApp(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.icon = TrayIcon(APP_ID, ACTIVE_ICON, self.create_tray_menu())
        self.screen = None
        self.main_loop = None
        self.name_changed_handler_id = None
        self.start_time = datetime.now()

        print(f'### Start time: [{self.start_time.strftime("%Y-%m-%d %H:%M:%S")}]')

    def do_activate(self) -> None:
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        wm_class = ''
        active_window = screen.get_active_window()

        # to prevent double handler connections
        if previously_active_window and self.name_changed_handler_id:
            previously_active_window.disconnect(self.name_changed_handler_id)

        if active_window:
            self.name_changed_handler_id = active_window.connect('name-changed', self.on_name_changed)
            wm_class = get_wm_class(active_window.get_xid())

        print(f'{wm_class}')
        print(f'\t{get_window_name(active_window)}')

    def on_name_changed(self, window: Wnck.Window) -> None:
        print(f'\t-> {get_window_name(window)}')

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop_main_loop()

    def stop_main_loop(self) -> None:
        finish_time = datetime.now()
        print(f'### Finish time: [{finish_time.strftime("%Y-%m-%d %H:%M:%S")}]')

        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)
        print(f'### Work time: [{work_time}]')

        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop_main_loop()

    def create_tray_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        close_item = Gtk.MenuItem('Close')
        close_item.connect('activate', self.on_close_item_click)

        menu.append(close_item)
        menu.show_all()

        return menu
