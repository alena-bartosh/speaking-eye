from datetime import datetime, timedelta, date
from typing import Dict
import json
import os
import signal
from types import FrameType

from gi.repository import Wnck, Gtk, GObject, Notify, GLib
import pandas as pd

from gtk_extras import get_window_name
from tray_icon import TrayIcon
from x_helpers import get_wm_class

APP_ID = 'speaking-eye'
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_ICON = os.path.join(SRC_DIR, '../icon/active.png')
RAW_DATA_TSV = os.path.join(SRC_DIR, f'../dist/{date.today()}_speaking_eye_raw_data.tsv')


class SpeakingEyeApp(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.icon = TrayIcon(APP_ID, ACTIVE_ICON, self.create_tray_menu())
        self.screen = None
        self.main_loop = None
        self.name_changed_handler_id = None
        self.start_time = datetime.now()
        self.active_window_start_time = datetime.now()
        self.active_tab_start_time = None
        self.active_window_name = None
        self.wm_class = None
        self.apps_time = self.try_load_apps_time()
        self.raw_data_tsv_file = open(RAW_DATA_TSV, 'a')
        self.save_timer_id = None

        Notify.init(APP_ID)

        start_msg = f'Start time: [{self.start_time.strftime("%H:%M:%S")}]'
        print(start_msg)
        self.show_notification(msg=start_msg)

    def do_activate(self) -> None:
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()
        self.start_save_timer()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        now = datetime.now()

        # self.wm_class is None only for Speaking Eye start (only for the first check)
        if self.wm_class:
            self.on_close_window(now)
            self.save_app_work_time(now)

        # to prevent double handler connections
        if previously_active_window and self.name_changed_handler_id:
            previously_active_window.disconnect(self.name_changed_handler_id)

        self.active_window_start_time = now

        active_window = screen.get_active_window()

        if active_window:
            self.name_changed_handler_id = active_window.connect('name-changed', self.on_name_changed)
            self.wm_class = get_wm_class(active_window.get_xid())
            self.active_window_name = get_window_name(active_window)
        else:
            self.wm_class = 'Desktop'
            self.active_window_name = 'Desktop'

        print(f'OPEN {self.wm_class}')

    def on_close_window(self, now: datetime) -> None:
        active_window_work_time = now - self.active_window_start_time

        print(f'CLOSE {self.wm_class} [{active_window_work_time}]')

    def save_activity_time(self, work_time: timedelta) -> None:
        app = f'|{self.wm_class}|{self.active_window_name}'

        if app in self.apps_time:
            self.apps_time[app] += work_time
        else:
            self.apps_time[app] = work_time

    def on_name_changed(self, window: Wnck.Window) -> None:
        now = datetime.now()
        self.on_close_tab(now)
        self.save_app_work_time(now)

        self.active_window_name = get_window_name(window)
        self.active_tab_start_time = now

    def on_close_tab(self, now: datetime) -> None:
        active_tab_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time

        active_tab_work_time = now - active_tab_start_time
        print(f'\t[{active_tab_work_time}]\t{self.active_window_name}')

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        now = datetime.now()

        self.on_close_tab(now)
        self.on_close_window(now)
        self.save_app_work_time(now)

        finish_time = now
        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)

        finish_msg = f'Finish time: [{finish_time.strftime("%H:%M:%S")}]'
        work_time_msg = f'Work time: [{work_time}]'

        print()
        print(f'{finish_msg}\n{work_time_msg}')
        print(f'Apps time: {json.dumps(self.apps_time, indent=2, default=str)}')

        self.show_notification(msg=f'{finish_msg}; {work_time_msg}')
        Notify.uninit()

        self.raw_data_tsv_file.close()
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
        Notify.Notification.new('Speaking Eye', msg, ACTIVE_ICON).show()

    def save_activity_line_to_file(self, start_time: datetime, end_time: datetime, work_time: timedelta) -> None:
        line = f'{start_time}\t{end_time}\t{work_time}\t{self.wm_class}\t{self.active_window_name}\n'
        self.raw_data_tsv_file.write(line)
        self.raw_data_tsv_file.flush()

    def try_load_apps_time(self) -> Dict[str, timedelta]:
        if not os.path.exists(RAW_DATA_TSV):
            return {}

        col_names = ['start_time', 'end_time', 'work_time', 'wm_class', 'active_window_name']

        df = pd.read_csv(RAW_DATA_TSV, names=col_names, sep='\t')
        df['application'] = df['wm_class'] + ' | ' + df['active_window_name']
        df['work_time'] = pd.to_timedelta(df['work_time'])
        df = df.groupby('application')['work_time'].sum().reset_index()

        return dict(zip(list(df['application']), list(df['work_time'])))

    def save_app_work_time(self, now: datetime, reset_start_time=False) -> None:
        activity_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time
        activity_work_time = now - activity_start_time

        self.save_activity_time(activity_work_time)
        self.save_activity_line_to_file(activity_start_time, now, activity_work_time)

        if reset_start_time:
            self.active_tab_start_time = now
            self.active_window_start_time = now

    def handle_sigterm(self, signal_number: int, frame: FrameType) -> None:
        self.stop()

    # TODO: add Timer class
    def start_save_timer(self) -> None:
        interval_ms = 10 * 60 * 1000

        self.save_timer_id = GLib.timeout_add(interval_ms, self.save_timer_handler)

    def save_timer_handler(self) -> bool:
        now = datetime.now()
        self.save_app_work_time(now, True)

        return True

    def stop_save_timer(self) -> None:
        GObject.source_remove(self.save_timer_id)
        self.save_timer_id = None
