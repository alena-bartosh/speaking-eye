from datetime import date, datetime, timedelta
from functools import reduce
from types import FrameType
from typing import Any, Dict
import coloredlogs
import json
import logging
import operator
import os
import signal

from gi.repository import GObject, Gtk, Notify, Wnck
import pandas as pd

from gtk_extras import get_window_name
from timer import Timer
from tray_icon import TrayIcon
from x_helpers import get_wm_class

APP_ID = 'speaking-eye'
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_ICON = os.path.join(SRC_DIR, '../icon/dark/active.png')
DISABLED_ICON = os.path.join(SRC_DIR, '../icon/dark/disabled.png')
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
        self.save_timer = Timer('save_timer', handler=self.save_timer_handler, interval_ms=10*60*1000, repeat=True)
        self.reminder_timer = \
            Timer('reminder_timer', handler=self.show_overtime_notification, interval_ms=15*60*1000, repeat=False)
        self.overtime_timer = \
            Timer('overtime_timer', handler=self.overtime_timer_handler, interval_ms=1*60*1000, repeat=True)
        self.is_work_time = False
        self.last_overtime_notification = None
        self.user_work_time_hour_limit = 8
        self.logger = self.init_logger()

        Notify.init(APP_ID)

        start_msg = f'Start time: [{self.start_time.strftime("%H:%M:%S")}]'
        self.logger.debug(start_msg)
        self.show_notification(msg=start_msg)

    def init_logger(self) -> logging.Logger:
        coloredlogs.install(level='DEBUG')
        logger = logging.getLogger(APP_ID)

        return logger

    def do_activate(self) -> None:
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()
        self.save_timer.start()
        self.overtime_timer.start()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        now = datetime.now()

        if self.wm_class:
            self.on_close_window(now)
            self.save_app_work_time(now)
        else:
            # self.wm_class is None only for Speaking Eye start (only for the first check)
            self.active_window_start_time = now

        # to prevent double handler connections
        if previously_active_window and self.name_changed_handler_id:
            previously_active_window.disconnect(self.name_changed_handler_id)

        active_window = screen.get_active_window()

        if active_window:
            self.name_changed_handler_id = active_window.connect('name-changed', self.on_name_changed)
            self.wm_class = get_wm_class(active_window.get_xid())
            self.active_window_name = get_window_name(active_window)
        else:
            self.wm_class = 'Desktop'
            self.active_window_name = 'Desktop'

        self.logger.debug(f'OPEN {self.wm_class}')

    def on_close_window(self, now: datetime) -> None:
        active_window_work_time = now - self.active_window_start_time

        self.logger.debug(f'CLOSE {self.wm_class} [{active_window_work_time}]')

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

    def on_close_tab(self, now: datetime) -> None:
        active_tab_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time

        active_tab_work_time = now - active_tab_start_time
        self.logger.debug(f'\t[{active_tab_work_time}]\t{self.active_window_name}')

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.save_timer.stop()

        now = datetime.now()

        self.on_close_tab(now)
        self.on_close_window(now)
        self.save_app_work_time(now)

        finish_time = now
        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)

        finish_msg = f'Finish time: [{finish_time.strftime("%H:%M:%S")}]'
        work_time_msg = f'Work time: [{work_time}]'

        self.logger.debug(f'{finish_msg}\n{work_time_msg}')
        self.logger.debug(f'Apps time: {json.dumps(self.work_apps_time, indent=2, default=str)}')

        self.show_notification(msg=f'{finish_msg}; {work_time_msg}')
        Notify.uninit()

        self.raw_data_tsv_file.close()
        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def set_work_time_state(self, value: bool) -> None:
        if value == self.is_work_time:
            self.logger.debug('### Trying to change is_work_time to the same value')
            return

        now = datetime.now()
        self.save_app_work_time(now)

        self.is_work_time = value

        self.logger.debug(f'### Set Work Time to [{self.is_work_time}]')

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
            self.logger.debug('### Do not run timer because of end of the work')
            return

        self.reminder_timer.start()

    def on_finish_work_action_clicked(self, notification: Notify.Notification, action_id: str, arg: Any) -> None:
        self.reminder_timer.stop()
        self.set_work_time_state(False)

    def show_notification(self, msg: str) -> None:
        Notify.Notification.new('Speaking Eye', msg, ACTIVE_ICON).show()

    def show_overtime_notification(self) -> None:
        msg = f'You have already worked {self.user_work_time_hour_limit} hours.\n' \
              f'It\'s time to finish working and start living.'

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

    def get_user_work_time(self) -> timedelta:
        return reduce(operator.add, self.work_apps_time.values(), timedelta())

    def save_app_work_time(self, now: datetime) -> None:
        activity_start_time = \
            self.active_tab_start_time if self.active_tab_start_time else self.active_window_start_time
        activity_work_time = now - activity_start_time

        self.save_activity_time_if_needed(activity_work_time)
        self.save_activity_line_to_file(activity_start_time, now, activity_work_time)

        self.active_tab_start_time = now
        self.active_window_start_time = now

    def handle_sigterm(self, signal_number: int, frame: FrameType) -> None:
        self.stop()

    def save_timer_handler(self) -> None:
        now = datetime.now()
        self.save_app_work_time(now)

    def overtime_timer_handler(self):
        if self.get_user_work_time().total_seconds() >= self.user_work_time_hour_limit * 60 * 60:
            self.show_overtime_notification()
            self.overtime_timer.stop()
