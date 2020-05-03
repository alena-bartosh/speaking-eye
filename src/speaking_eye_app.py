from datetime import datetime, timedelta, date
import json
import os

from gi.repository import Wnck, Gtk, GObject, Notify
import pandas as pd

from gtk_extras import get_window_name
from tray_icon import TrayIcon
from x_helpers import get_wm_class

APP_ID = 'speaking-eye'
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_ICON = os.path.join(SRC_DIR, '../icon/active.png')
RESULT_TSV = os.path.join(SRC_DIR, f'../dist/{date.today()}_speaking_eye_results.tsv')
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

        Notify.init(APP_ID)

        start_msg = f'Start time: [{self.start_time.strftime("%H:%M:%S")}]'
        print(start_msg)
        self.show_notification(msg=start_msg)

    def do_activate(self) -> None:
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        now = datetime.now()
        self.on_close_window(now)

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

    def on_close_window(self, now: datetime, save_to_file: bool = True, save_to_dict: bool = True) -> None:
        if not self.wm_class:
            return

        active_window_work_time = now - self.active_window_start_time

        print(f'CLOSE {self.wm_class} [{active_window_work_time}]')

        if save_to_file:
            self.save_activity_line(self.active_window_start_time, now)

        if save_to_dict:
            self.save_work_time(active_window_work_time)

        self.active_tab_start_time = None

    def save_work_time(self, work_time: timedelta) -> None:
        app = f'|{self.wm_class}|{self.active_window_name}'

        if app in self.apps_time:
            print('ERROR_APP_IN_DICT', app, work_time)
            self.apps_time[app] += work_time
        else:
            self.apps_time[app] = work_time

    def on_name_changed(self, window: Wnck.Window) -> None:
        now = datetime.now()
        self.on_close_tab(now)

        self.active_window_name = get_window_name(window)
        self.active_tab_start_time = now

    def on_close_tab(self, now: datetime) -> None:
        active_tab_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time

        active_tab_work_time = now - active_tab_start_time
        print(f'\t[{active_tab_work_time}]\t{self.active_window_name}')

        self.save_work_time(active_tab_work_time)

        self.save_activity_line(active_tab_start_time, now)

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        now = datetime.now()

        self.on_close_tab(now)
        self.on_close_window(now, save_to_file=False, save_to_dict=False)

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

        pd.DataFrame(self.apps_time.items(), columns=['application', 'work_time']).to_csv(RESULT_TSV, sep='\t')

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

    def save_activity_line(self, start_time: datetime, end_time: datetime) -> None:
        work_time = end_time - start_time

        line = f'{start_time}\t{end_time}\t{work_time}\t{self.wm_class}\t{self.active_window_name}\n'
        self.raw_data_tsv_file.write(line)

    def try_load_apps_time(self):
        if not os.path.exists(RESULT_TSV):
            return {}

        df = pd.read_csv(RESULT_TSV, sep='\t', index_col=0)

        return dict(zip(list(df['application']), [pd.to_timedelta(el) for el in df['work_time']]))
