import logging
import os
import re
import signal
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from random import choice
from types import FrameType
from typing import Any, Dict, List, Optional

from gi.repository import Gio, GLib, GObject, Gtk, Notify, Wnck
from pydash import get

from activity import Activity
from activity_reader import ActivityReader
from activity_stat_holder import ActivityStatHolder
from activity_writer import ActivityWriter
from gtk_extras import get_window_name
from timer import Timer
from tray_icon import TrayIcon
from x_helpers import get_wm_class

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_TSV_FILE_DIR = Path(SRC_DIR) / '..' / 'dest'
OUTPUT_TSV_FILE_MASK = '{date}_speaking_eye_raw_data.tsv'

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
        self.active_window_name = None
        self.previous_active_window_name = None
        self.wm_class = None
        self.previous_wm_class = None
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
        self.is_lock_screen_activated = False

        self.writer = ActivityWriter(OUTPUT_TSV_FILE_DIR, OUTPUT_TSV_FILE_MASK)
        self.reader = ActivityReader(logger)
        self.holder = ActivityStatHolder(self.reader.read(self.get_tsv_file_path()))
        self.current_activity: Optional[Activity] = None

        self.writer.event.on(ActivityWriter.NEW_DAY_EVENT, self.on_new_day_started)

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

        self.on_open_window(self.wm_class, self.active_window_name, now)

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
        self.overtime_timer.start()
        self.break_timer.start()

    def on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        now = datetime.now()

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

        self.on_open_window(self.wm_class, self.active_window_name, now)

    def on_open_window(self, wm_class: str, window_name: str, now: datetime) -> None:
        self.logger.debug(f'OPEN {self.wm_class}')

        new_activity = Activity(wm_class, window_name, now, self.is_work_time)

        self.__on_activity_changed(self.current_activity, new_activity)

    def on_name_changed(self, window: Wnck.Window) -> None:
        now = datetime.now()

        self.active_window_name = get_window_name(window)

        new_activity = Activity(self.wm_class, self.active_window_name, now, self.is_work_time)

        self.__on_activity_changed(self.current_activity, new_activity)

    def __on_activity_changed(self, previous_activity: Optional[Activity], next_activity: Activity) -> None:
        is_first_activity_change = previous_activity is None
        now = datetime.now()

        if not is_first_activity_change:
            previous_activity.set_end_time(now)
            self.writer.write(previous_activity)
            self.holder.update_stat(previous_activity)

        previous_activity_app_name = '' if is_first_activity_change else previous_activity.app_name
        self.logger.debug(f'{now}: {previous_activity_app_name} -> {next_activity.app_name}')

        self.current_activity = next_activity

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        now = datetime.now()

        finish_time = now
        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)

        finish_msg = f'Finish time: [{finish_time.strftime("%H:%M:%S")}]'
        work_time_msg = f'Work time: [{work_time}]'

        self.logger.debug(f'{finish_msg}\n{work_time_msg}')
        self.show_notification(msg=f'{finish_msg}; {work_time_msg}')
        Notify.uninit()

        self.main_loop.quit()

    def on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def set_work_time_state(self, value: bool) -> None:
        if value == self.is_work_time:
            self.logger.debug('Trying to change is_work_time to the same value')
            return

        self.is_work_time = value

        now = datetime.now()
        new_activity = Activity(self.current_activity.wm_class,
                                self.current_activity.window_name,
                                now,
                                self.is_work_time)

        self.__on_activity_changed(self.current_activity, new_activity)

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

    def on_new_day_started(self) -> None:
        open_new_file_msg = 'New file was opened and apps work time was reset'

        self.logger.debug(open_new_file_msg)
        self.show_notification(msg=open_new_file_msg)

        self.set_work_time_state(False)

    def get_tsv_file_path(self) -> Path:
        return OUTPUT_TSV_FILE_DIR / OUTPUT_TSV_FILE_MASK.format(date=date.today())

    def handle_sigterm(self, signal_number: int, frame: FrameType) -> None:
        self.stop()

    def overtime_timer_handler(self) -> None:
        if not self.is_work_time:
            return

        is_overtime_started = self.holder.total_work_time.total_seconds() >= self.user_work_time_hour_limit * 60 * 60

        if not is_overtime_started:
            return

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
