from datetime import date, datetime, timedelta
from typing import Any, Dict
import json
import os
import signal
from types import FrameType

from gi.repository import GLib, GObject, Gtk, Notify, Wnck
import pandas as pd

from gtk_extras import get_window_name
from tray_icon import TrayIcon
from x_helpers import get_wm_class

APP_ID = 'speaking-eye'
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_ICON = os.path.join(SRC_DIR, '../icon/active.png')
DISABLED_ICON = os.path.join(SRC_DIR, '../icon/disabled.png')
RAW_DATA_TSV = os.path.join(SRC_DIR, f'../dist/{date.today()}_speaking_eye_raw_data.tsv')


class SpeakingEyeApp(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.tray_icon = TrayIcon(APP_ID, DISABLED_ICON, self.create_tray_menu())
        self.screen = None
        self.main_loop = None
        self.name_changed_handler_id = None
        self.start_time = datetime.now()
        self.active_window_start_time = datetime.now()
        self.active_tab_start_time = None
        self.active_window_name = None
        self.wm_class = None
        self.work_apps_time = self.try_load_work_apps_time()
        self.raw_data_tsv_file = open(RAW_DATA_TSV, 'a')
        self.save_timer_id = None
        self.reminder_timer_id = None
        self.is_work_time = False
        self.last_overtime_notification = None

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

    def save_activity_time_if_needed(self, work_time: timedelta) -> None:
        if not self.is_work_time:
            return

        app = f'{self.wm_class} | {self.active_window_name}'

        if app in self.work_apps_time:
            self.work_apps_time[app] += work_time
        else:
            self.work_apps_time[app] = work_time

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
        self.stop_save_timer()

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
        print(f'Apps time: {json.dumps(self.work_apps_time, indent=2, default=str)}')

        self.show_notification(msg=f'{finish_msg}; {work_time_msg}')
        Notify.uninit()

        self.raw_data_tsv_file.close()
        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def set_work_time_state(self, value: bool) -> None:
        if value == self.is_work_time:
            print('### Trying to change is_work_time to the same value')
            return

        now = datetime.now()
        self.save_app_work_time(now, reset_start_time=True)

        self.is_work_time = value

        print(f'### Set Work Time to [{self.is_work_time}]')

        icon = ACTIVE_ICON if self.is_work_time else DISABLED_ICON
        self.tray_icon.set_icon_if_exist(icon)

    def on_work_state_checkbox_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.set_work_time_state(not self.is_work_time)

    def create_tray_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        work_state_checkbox_item = Gtk.CheckMenuItem('Work Time')
        work_state_checkbox_item.connect('activate', self.on_work_state_checkbox_item_click)
        menu.append(work_state_checkbox_item)

        close_item = Gtk.MenuItem('Close')
        close_item.connect('activate', self.on_close_item_click)
        menu.append(close_item)

        menu.show_all()

        return menu

    def on_overtime_notification_closed(self, notification: Notify.Notification) -> None:
        if not self.is_work_time:
            print('### Do not run timer because of end of the work')
            return

        self.start_reminder_timer(mins=15)

    def on_finish_work_action_clicked(self, notification: Notify.Notification, action_id: str, arg: Any) -> None:
        self.stop_reminder_timer_if_exists()
        self.set_work_time_state(False)

    def show_notification(self, msg: str) -> None:
        Notify.Notification.new('Speaking Eye', msg, ACTIVE_ICON).show()

    def show_overtime_notification(self) -> None:
        msg = f'You have already worked {8} hours.\nIt\'s time to finish working and start living.'

        notification = Notify.Notification.new('Speaking Eye', msg, ACTIVE_ICON)
        notification.connect('closed', self.on_overtime_notification_closed)

        notification.add_action(
            'finish_work',
            'Finish work',
            self.on_finish_work_action_clicked,
            None
        )
        notification.add_action(
            'remind_later',
            'Remind me after 15 mins',
            lambda *args: None,
            None
        )

        notification.set_urgency(Notify.Urgency.CRITICAL)
        notification.show()

        self.last_overtime_notification = notification

    def save_activity_line_to_file(self, start_time: datetime, end_time: datetime, work_time: timedelta) -> None:
        line = \
            f'{start_time}\t{end_time}\t{work_time}\t{self.wm_class}\t{self.active_window_name}\t{self.is_work_time}\n'
        self.raw_data_tsv_file.write(line)
        self.raw_data_tsv_file.flush()

    def try_load_work_apps_time(self) -> Dict[str, timedelta]:
        if not os.path.exists(RAW_DATA_TSV):
            return {}

        col_names = ['start_time', 'end_time', 'work_time', 'wm_class', 'active_window_name', 'is_work_time']

        df = pd.read_csv(RAW_DATA_TSV, names=col_names, sep='\t')
        df = df.loc[df['is_work_time'].astype(bool).eq(True)]
        df['application'] = df['wm_class'] + ' | ' + df['active_window_name']
        df['work_time'] = pd.to_timedelta(df['work_time'])
        df = df.groupby('application')['work_time'].sum().reset_index()

        return dict(zip(list(df['application']), list(df['work_time'])))

    def save_app_work_time(self, now: datetime, reset_start_time=False) -> None:
        activity_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time
        activity_work_time = now - activity_start_time

        self.save_activity_time_if_needed(activity_work_time)
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
        self.save_app_work_time(now, reset_start_time=True)

        return True

    def stop_save_timer(self) -> None:
        GObject.source_remove(self.save_timer_id)
        self.save_timer_id = None

    def start_reminder_timer(self, mins: int) -> None:
        interval_ms = mins * 60 * 1000

        self.reminder_timer_id = GLib.timeout_add(interval_ms, self.reminder_timer_handler)

    def reminder_timer_handler(self) -> bool:
        self.show_overtime_notification()
        self.reminder_timer_id = None

        return False

    def stop_reminder_timer_if_exists(self) -> None:
        if self.reminder_timer_id:
            GObject.source_remove(self.reminder_timer_id)
            self.reminder_timer_id = None
