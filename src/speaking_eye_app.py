from datetime import date, datetime, timedelta
from enum import Enum
from functools import reduce
from random import choice
from types import FrameType
from typing import Any, Dict, List
import json
import logging
import operator
import os
import re
import signal

from gi.repository import Gio, GLib, GObject, Gtk, Notify, Wnck
from pydash import get
import pandas as pd

from gtk_extras import get_window_name
from timer import Timer
from tray_icon import TrayIcon
from x_helpers import get_wm_class

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_TSV_FMT = os.path.join(SRC_DIR, '../dest/{date}_speaking_eye_raw_data.tsv')

BREAK_TIME_EMOJIS = ['🐵', '✋', '🙃', '💆', '💣', '😎',
                     '🙇', '🙋', '🚣', '🤸', '🧟', '🐙',
                     '🐧', '☕', '🍌', '🥐', '🆓', '🔮']


class IconState(Enum):
    ACTIVE = 'active'
    DISABLED = 'disabled'


class SpecialWmClass(Enum):
    DESKTOP = 'Desktop'
    LOCK_SCREEN = 'LockScreen'


class SpeakingEyeApp(Gtk.Application):

    def __init__(self, app_id: str, config: Dict, logger: logging.Logger) -> None:
        super().__init__()
        self.config = config
        self.logger = logger
        self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.screen_saver_bus_names = self.__dbus_get_screen_saver_bus_names()
        self.theme = get(self.config, 'theme') or 'dark'
        self.active_icon = self.get_icon(IconState.ACTIVE)
        self.disabled_icon = self.get_icon(IconState.DISABLED)
        self.tray_icon = TrayIcon(app_id, self.disabled_icon, self.create_tray_menu())
        self.screen = None
        self.main_loop = None
        self.name_changed_handler_id = None
        self.start_time = datetime.now()
        self.active_window_start_time = self.start_time
        self.active_tab_start_time = None
        self.active_window_name = None
        self.previous_active_window_name = None
        self.wm_class = None
        self.previous_wm_class = None
        self.work_apps_time = self.try_load_work_apps_time()
        self.save_timer = Timer('save_timer', handler=self.save_timer_handler, interval_ms=10*60*1000, repeat=True)
        self.reminder_timer = \
            Timer('reminder_timer', handler=self.show_overtime_notification, interval_ms=15*60*1000, repeat=False)
        self.overtime_timer = \
            Timer('overtime_timer', handler=self.overtime_timer_handler, interval_ms=1*60*1000, repeat=True)
        self.break_timer = \
            Timer('break_timer', handler=self.break_timer_handler, interval_ms=1*60*1000, repeat=True)
        self.last_break_reminder_time = None
        self.is_work_time = False
        self.is_work_time_update_time = self.start_time
        self.last_overtime_notification = None
        self.last_break_notification = None
        self.user_work_time_hour_limit = get(self.config, 'time_limits.work_time_hours') or 9
        self.user_breaks_interval_hours = get(self.config, 'time_limits.breaks_interval_hours') or 3
        self.last_lock_screen_time = None
        self.tsv_file = None
        self.is_lock_screen_activated = False

        self.logger.debug(f'Set user work time limit to [{self.user_work_time_hour_limit}] hours')
        self.logger.debug(f'Set user user breaks interval to [{self.user_breaks_interval_hours}] hours')

        Notify.init(app_id)
        self.__dbus_subscribe_to_screen_saver_signals()

        start_msg = f'Start time: [{self.start_time.strftime("%H:%M:%S")}]'
        self.logger.debug(start_msg)
        self.show_notification(msg=start_msg)

    def __dbus_method_call(self, bus_name: str, object_path: str, interface_name: str, method_name: str) -> Any:
        if not self.connection:
            raise Exception('self.connection should be set!')

        no_parameters = None
        default_reply_type = None
        default_call_timeout = -1
        not_cancellable = None

        raw_result = self.connection.call_sync(bus_name, object_path, interface_name,
                                               method_name, no_parameters, default_reply_type,
                                               Gio.DBusCallFlags.NONE, default_call_timeout, not_cancellable)

        if raw_result:
            result, = raw_result

            return result

        return None

    def __dbus_get_all_bus_names(self) -> List[str]:
        return self.__dbus_method_call('org.freedesktop.DBus', '/org/freedesktop/DBus',
                                       'org.freedesktop.DBus', 'ListNames')

    def __dbus_lock_screen(self) -> None:
        for bus in self.screen_saver_bus_names:
            # TODO: think about 'try-except' here
            if bus == 'org.freedesktop.ScreenSaver':
                continue

            interface_name = f'/{bus.replace(".", "/")}'

            self.__dbus_method_call(bus, interface_name, bus, 'Lock')

    def on_screen_saver_active_changed(self, connection: Gio.DBusConnection, sender_name: str, object_path: str,
                                       interface_name: str, signal_name: str, parameters: GLib.Variant) -> None:
        is_activated, = parameters
        self.is_lock_screen_activated = is_activated

        now = datetime.now()

        self.on_close_window(now)
        self.save_app_work_time(now)

        if self.is_lock_screen_activated:
            self.previous_wm_class = self.wm_class
            self.previous_active_window_name = self.active_window_name

            self.wm_class = SpecialWmClass.LOCK_SCREEN.value
            self.active_window_name = ''
        else:
            if self.is_work_time:
                self.last_lock_screen_time = now

            self.wm_class = self.previous_wm_class
            self.active_window_name = self.previous_active_window_name

        self.on_open_window()

    def __dbus_get_screen_saver_bus_names(self) -> List[str]:
        bus_names = self.__dbus_get_all_bus_names()
        screen_saver_re = re.compile(r'^org\..*\.ScreenSaver$')

        return list(filter(screen_saver_re.match, bus_names))

    def __dbus_subscribe_to_screen_saver_signals(self) -> None:
        if not self.screen_saver_bus_names:
            raise Exception('self.screen_saver_bus_names should be set!')

        for bus_name in self.screen_saver_bus_names:
            self.connection.signal_subscribe(None, bus_name, 'ActiveChanged', None, None,
                                             Gio.DBusSignalFlags.NONE, self.on_screen_saver_active_changed)

    def do_activate(self) -> None:
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.on_active_window_changed)
        self.main_loop = GObject.MainLoop()
        self.save_timer.start()
        self.overtime_timer.start()
        self.break_timer.start()

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
            self.wm_class = SpecialWmClass.DESKTOP.value
            self.active_window_name = ''

        self.on_open_window()

    def on_open_window(self) -> None:
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

        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def set_work_time_state(self, value: bool) -> None:
        # TODO: correct write to file when change work state while do the same
        if value == self.is_work_time:
            self.logger.debug('Trying to change is_work_time to the same value')
            return

        now = datetime.now()
        self.save_app_work_time(now)

        self.is_work_time = value
        self.is_work_time_update_time = now

        self.logger.debug(f'Set Work Time to [{self.is_work_time}]')

        icon = self.active_icon if self.is_work_time else self.disabled_icon
        self.tray_icon.set_icon_if_exist(icon)

        if self.is_work_time:
            self.last_lock_screen_time = now
            self.last_break_reminder_time = now

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
            self.logger.debug('Do not run timer because of end of the work')
            return

        self.reminder_timer.start()

    def on_finish_work_action_clicked(self, notification: Notify.Notification, action_id: str, arg: Any) -> None:
        self.reminder_timer.stop()
        self.set_work_time_state(False)

    def on_take_break_clicked(self, notification: Notify.Notification, action_id: str, arg: Any) -> None:
        self.__dbus_lock_screen()

    def show_notification(self, msg: str) -> None:
        Notify.Notification.new('Speaking Eye', msg, self.active_icon).show()

    def show_overtime_notification(self) -> None:
        msg = f'You have already worked {self.user_work_time_hour_limit} hours.\n' \
              f'It\'s time to finish working and start living.'

        notification = Notify.Notification.new('Speaking Eye', msg, self.active_icon)
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

    def show_break_notification(self) -> None:
        emoji = choice(BREAK_TIME_EMOJIS)
        msg = f'It\'s time to take a break {emoji}'

        notification = Notify.Notification.new('Speaking Eye', msg, self.active_icon)

        notification.add_action(
            'take_break',
            'Take a break (lock screen)',
            self.on_take_break_clicked,
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

        self.last_break_notification = notification

    def save_activity_line_to_file(self, start_time: datetime, end_time: datetime, work_time: timedelta) -> None:
        self.open_tsv_file_if_needed()

        line = \
            f'{start_time}\t{end_time}\t{work_time}\t{self.wm_class}\t{self.active_window_name}\t{self.is_work_time}\n'
        self.tsv_file.write(line)
        self.tsv_file.flush()

    def open_tsv_file_if_needed(self) -> None:
        tsv_file_path = self.get_tsv_file_path()

        if self.tsv_file is None:
            self.tsv_file = open(tsv_file_path, 'a')
            return

        if self.tsv_file.name == tsv_file_path:
            return

        # TODO: if app work time from 23:00 to 01:00
        #  then split between old and new file: [23:00; 00:00] U [00:00; 01:00]
        self.tsv_file.close()

        self.tsv_file = open(tsv_file_path, 'a')

        self.on_new_day_started()

    def on_new_day_started(self) -> None:
        self.work_apps_time = {}
        open_new_file_msg = 'New file was opened and apps work time was reset'

        self.logger.debug(open_new_file_msg)
        self.show_notification(msg=open_new_file_msg)

        self.set_work_time_state(False)

    def try_load_work_apps_time(self) -> Dict[str, timedelta]:
        tsv_file_path = self.get_tsv_file_path()

        if not os.path.exists(tsv_file_path):
            return {}

        col_names = ['start_time', 'end_time', 'work_time', 'wm_class', 'active_window_name', 'is_work_time']

        df = pd.read_csv(tsv_file_path, names=col_names, sep='\t')
        df = df.loc[df['is_work_time'].astype(bool).eq(True)]
        df['application'] = df['wm_class'] + ' | ' + df['active_window_name']
        df['work_time'] = pd.to_timedelta(df['work_time'])
        df = df.groupby('application')['work_time'].sum().reset_index()

        return dict(zip(list(df['application']), list(df['work_time'])))

    def get_tsv_file_path(self) -> str:
        return RAW_DATA_TSV_FMT.format(date=date.today())

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

    def overtime_timer_handler(self) -> None:
        is_overtime_started = self.get_user_work_time().total_seconds() >= self.user_work_time_hour_limit * 60 * 60
        if is_overtime_started and self.is_work_time:
            self.show_overtime_notification()
            self.overtime_timer.stop()

    def break_timer_handler(self) -> None:
        if not self.is_work_time or self.is_lock_screen_activated:
            return

        now = datetime.now()
        start_work_time = self.is_work_time_update_time
        last_break_time = self.last_lock_screen_time if self.last_lock_screen_time else start_work_time
        last_break_reminder_time = self.last_break_reminder_time if self.last_break_reminder_time else start_work_time

        need_to_show_break_notification = \
            (now - last_break_time).total_seconds() >= self.user_breaks_interval_hours * 60 * 60 \
            and (now - last_break_reminder_time).total_seconds() >= 15 * 60

        if need_to_show_break_notification:
            self.show_break_notification()
            self.last_break_reminder_time = now

    def get_icon(self, icon_state: IconState) -> str:
        if not self.theme:
            raise Exception('self.theme should be set!')

        full_path = os.path.join(SRC_DIR, f'../icon/{self.theme}/{icon_state.value}.png')

        if not os.path.exists(full_path):
            self.logger.warning(f'Icon [{full_path}] not found')

        return full_path
