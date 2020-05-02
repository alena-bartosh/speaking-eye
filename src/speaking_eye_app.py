from datetime import datetime, timedelta
import json
import os

from gi.repository import Wnck, Gtk, GObject, Notify

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
        self.notify = Notify
        self.name_changed_handler_id = None
        self.start_time = datetime.now()
        self.active_window_start_time = datetime.now()
        self.wm_class = ''

        self.active_tab_start_time = datetime.now()
        self.active_tab_work_time = 0

        self.apps_time = {}

        self.notify.init(APP_ID)

        start_msg = f'### Start time: [{self.start_time.strftime("%Y-%m-%d %H:%M:%S")}]'
        print(start_msg)
        self.show_notification(msg=start_msg)

    def do_activate(self) -> None:
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        self.on_close_window()

        # to prevent double handler connections
        if previously_active_window and self.name_changed_handler_id:
            previously_active_window.disconnect(self.name_changed_handler_id)

        self.active_window_start_time = datetime.now()

        active_window = screen.get_active_window()

        if active_window:
            self.name_changed_handler_id = active_window.connect('name-changed', self.on_name_changed)
            self.wm_class = get_wm_class(active_window.get_xid())

        print(f'OPEN {self.wm_class}')
        print(f'\t{get_window_name(active_window)}')

    def on_close_window(self) -> None:
        if not self.wm_class:
            return

        active_window_work_time = datetime.now() - self.active_window_start_time

        print(f'CLOSE {self.wm_class} [{active_window_work_time}]')

        if self.wm_class in self.apps_time:
            self.apps_time[self.wm_class] += active_window_work_time
        else:
            self.apps_time[self.wm_class] = active_window_work_time

    def on_name_changed(self, window: Wnck.Window) -> None:
        self.active_tab_work_time = round((datetime.now() - self.active_tab_start_time).total_seconds(), 3)
        print(f'\t[{self.active_tab_work_time}] -> {get_window_name(window)}')
        self.active_tab_start_time = datetime.now()

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.on_close_window()

        finish_time = datetime.now()
        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)

        finish_msg = f'### Finish time: [{finish_time.strftime("%Y-%m-%d %H:%M:%S")}]'
        work_time_msg = f'### Work time: [{work_time}]'

        print(f'{finish_msg}\n{work_time_msg}')
        print(f'### Apps time: {json.dumps(self.apps_time, indent=2, default=str)}')

        self.show_notification(msg=finish_msg)
        self.show_notification(msg=work_time_msg)
        self.notify.uninit()

        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def create_tray_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        close_item = Gtk.MenuItem('Close')
        close_item.connect('activate', self.on_close_item_click)

        menu.append(close_item)
        menu.show_all()

        return menu

    def show_notification(self, msg: str) -> None:
        self.notify.Notification.new(f'|SPEAKING EYE| {msg}').show()
