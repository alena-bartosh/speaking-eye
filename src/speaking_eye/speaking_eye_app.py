import logging
import re
import signal
import subprocess
import webbrowser
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from random import choice
from types import FrameType
from typing import Any, cast, List, Optional

from gi.repository import Gio, GLib, GObject, Gtk, Notify, Wnck
from pyee import BaseEventEmitter

from .activity import Activity
from .activity_reader import ActivityReader
from .activity_stat_holder import ActivityStatHolder
from .activity_writer import ActivityWriter
from .application_info_matcher import ApplicationInfoMatcher
from .config_reader import ConfigReader
from .files_provider import FilesProvider
from .gtk_extras import get_window_name
from .icon_state import IconState
from .localizator import Localizator
from .notification import Notification, NotificationEvent
from .notification_emojis import BREAK_TIME_EMOJIS, DISTRACTING_NOTIFICATION_EMOJIS
from .special_wm_class import SpecialWmClass
from .timer import Timer
from .tray_icon import TrayIcon
from .value import Value
from .x_helpers import get_wm_class


class ApplicationEvent(Enum):
    DISTRACTING_APP_OVERTIME = 'distracting_app_overtime'


class SpeakingEyeApp(Gtk.Application):  # type: ignore[misc]

    def __init__(self,
                 app_id: str,
                 config_reader: ConfigReader,
                 logger: logging.Logger,
                 application_info_matcher: ApplicationInfoMatcher,
                 activity_reader: ActivityReader,
                 files_provider: FilesProvider,
                 localizator: Localizator) -> None:
        super().__init__()
        self.logger = logger
        self.config_reader = config_reader

        self.connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.screen_saver_bus_names = self.__dbus_get_screen_saver_bus_names()

        self.files_provider = files_provider
        self.localizator = localizator

        self.theme = self.config_reader.get_theme()
        self.active_icon = self.get_icon(IconState.ACTIVE)
        self.disabled_icon = self.get_icon(IconState.DISABLED)

        self.work_state_checkbox_item = self.__create_work_state_checkbox_item()
        self.tray_icon = TrayIcon(app_id, self.disabled_icon, self.create_tray_menu(self.work_state_checkbox_item))

        self.screen: Optional[Wnck.Screen] = None
        self.main_loop: Optional[GObject.MainLoop] = None
        self.name_changed_handler_id = None

        self.previous_active_window_name: Optional[str] = None
        self.previous_wm_class: Optional[str] = None

        self.overtime_timer = \
            Timer('overtime_timer', handler=self.overtime_timer_handler,
                  interval_ms=1 * 60 * 1000, repeat=True, logger=self.logger)
        self.break_timer = \
            Timer('break_timer', handler=self.break_timer_handler,
                  interval_ms=1 * 60 * 1000, repeat=True, logger=self.logger)
        self.distracting_app_timer = \
            Timer('distracting_app_timer', handler=self.distracting_app_timer_handler,
                  interval_ms=1 * 60 * 1000, repeat=True, logger=self.logger)

        self.event = BaseEventEmitter()

        self.event.on(ApplicationEvent.DISTRACTING_APP_OVERTIME.value, self.show_distracting_app_overtime_notification)

        self.start_time = datetime.now()
        self.is_work_time = False
        self.is_work_time_update_time = self.start_time
        self.last_overtime_notification: Optional[Notification] = None
        self.last_break_notification: Optional[Notification] = None
        self.last_lock_screen_time: Optional[datetime] = None
        self.is_lock_screen_activated = False
        self.has_distracting_app_overtime_notification_shown = False
        self.is_overtime_notification_allowed_to_show = True
        self.is_break_notification_allowed_to_show = True

        self.user_work_time_hour_limit = config_reader.get_work_time_limit()
        self.user_breaks_interval_hours = config_reader.get_breaks_interval_hours()
        self.user_distracting_apps_mins = config_reader.get_distracting_apps_mins()

        self.writer = ActivityWriter(self.files_provider)

        self.app_info_matcher = application_info_matcher

        today_raw_data_file_path = self.files_provider.get_raw_data_file_path(date.today())
        self.holder = ActivityStatHolder(activity_reader.read(today_raw_data_file_path))

        self.holder.initialize_stats(self.app_info_matcher.detailed_app_infos)
        self.holder.initialize_stats(self.app_info_matcher.distracting_app_infos)

        self.current_activity: Optional[Activity] = None

        self.writer.event.on(ActivityWriter.NEW_DAY_EVENT, self.__on_new_day_started)

        self.logger.debug(f'Set user work time limit to [{self.user_work_time_hour_limit}] hours')
        self.logger.debug(f'Set user user breaks interval to [{self.user_breaks_interval_hours}] hours')

        Notify.init(app_id)
        self.__dbus_subscribe_to_screen_saver_signals()

        start_msg = self.localizator.get('notification.start', start_time=self.start_time.strftime("%H:%M:%S"))
        self.logger.debug(start_msg)
        self.new_notification(msg=start_msg).show()

    def __dbus_method_call(self, bus_name: str, object_path: str, interface_name: str, method_name: str) -> Any:
        """
        D-Bus is a middleware mechanism that allows communication between
        multiple processes running concurrently on the same machine
        """
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
        return cast(
            List[str],
            self.__dbus_method_call('org.freedesktop.DBus', '/org/freedesktop/DBus',
                                    'org.freedesktop.DBus', 'ListNames')
        )

    def __dbus_lock_screen(self) -> None:
        """Try to lock screen with a dbus call"""
        for bus in self.screen_saver_bus_names:
            if bus == 'org.freedesktop.ScreenSaver':
                # NOTE: that server is just interface without implementation
                continue

            interface_name = f'/{bus.replace(".", "/")}'

            try:
                self.__dbus_method_call(bus, interface_name, bus, 'Lock')
            except Exception as e:
                self.logger.warning(f'Please ignore it if lock screen works well. Lock screen error: [{e}]')

    def __on_screen_saver_active_changed(self, connection: Gio.DBusConnection, sender_name: str, object_path: str,
                                         interface_name: str, signal_name: str, parameters: GLib.Variant) -> None:
        is_activated, = parameters
        self.is_lock_screen_activated = is_activated

        now = datetime.now()

        if self.is_lock_screen_activated:
            current_activity = Value.get_or_raise(self.current_activity, 'current_activity')

            self.previous_wm_class = current_activity.wm_class
            self.previous_active_window_name = current_activity.window_name

            wm_class = SpecialWmClass.LOCK_SCREEN.value
            window_name = ''
        else:
            # the screen has just been unlocked
            if self.is_work_time:
                self.last_lock_screen_time = now

            wm_class = Value.get_or_raise(self.previous_wm_class, 'previous_wm_class')
            window_name = Value.get_or_raise(self.previous_active_window_name, 'previous_active_window_name')

        self.__on_open_window(wm_class, window_name, now)

    def __dbus_get_screen_saver_bus_names(self) -> List[str]:
        bus_names = self.__dbus_get_all_bus_names()
        screen_saver_re = re.compile(r'^org\..*\.ScreenSaver$')

        return list(filter(screen_saver_re.match, bus_names))

    def __dbus_subscribe_to_screen_saver_signals(self) -> None:
        if not self.screen_saver_bus_names:
            raise Exception('self.screen_saver_bus_names should be set!')

        for bus_name in self.screen_saver_bus_names:
            self.connection.signal_subscribe(None, bus_name, 'ActiveChanged', None, None,
                                             Gio.DBusSignalFlags.NONE, self.__on_screen_saver_active_changed)

    def do_activate(self) -> None:
        """Gtk.Application must call this method to get the application up and running"""
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        self.screen = Wnck.Screen.get_default()
        self.screen.connect('active-window-changed', self.__on_active_window_changed)
        self.main_loop = GObject.MainLoop()
        self.overtime_timer.start()
        self.break_timer.start()
        self.distracting_app_timer.start()

    def __on_active_window_changed(self, screen: Wnck.Screen, previously_active_window: Gtk.Window) -> None:
        now = datetime.now()

        # to prevent double handler connections
        if previously_active_window and self.name_changed_handler_id:
            previously_active_window.disconnect(self.name_changed_handler_id)

        active_window = screen.get_active_window()

        if active_window:
            self.name_changed_handler_id = active_window.connect('name-changed', self.__on_name_changed)
            wm_class = get_wm_class(active_window.get_xid())
            window_name = get_window_name(active_window)
        else:
            wm_class = SpecialWmClass.DESKTOP.value
            window_name = ''

        self.__on_open_window(wm_class, window_name, now)

    def __on_open_window(self, wm_class: str, window_name: str, now: datetime) -> None:
        new_activity = Activity(wm_class, window_name, now, self.is_work_time)

        self.__on_activity_changed(self.current_activity, new_activity)

    def __on_name_changed(self, window: Wnck.Window) -> None:
        now = datetime.now()

        current_activity = Value.get_or_raise(self.current_activity, 'current_activity')
        window_name = get_window_name(window)

        new_activity = Activity(current_activity.wm_class, window_name, now, current_activity.is_work_time)

        self.__on_activity_changed(current_activity, new_activity)

    def __on_activity_changed(self, previous_activity: Optional[Activity], next_activity: Activity) -> None:
        now = datetime.now()

        if previous_activity is not None:
            previous_activity.set_end_time(now)
            self.writer.write(previous_activity)
            self.holder.update_stat(previous_activity)

        # NOTE: previous_activity is None when it is the first activity after starting
        previous_activity_app_name = \
            '' if previous_activity is None else f'{previous_activity.wm_class}|{previous_activity.window_name}'
        self.logger.debug(f'{now}: {previous_activity_app_name} -> '
                          f'{next_activity.wm_class}|{next_activity.window_name}')

        self.app_info_matcher.set_if_matched(next_activity)

        self.current_activity = next_activity
        # NOTE: for reshowing notification when open distracting app once more time
        self.has_distracting_app_overtime_notification_shown = False

    def start_main_loop(self) -> None:
        try:
            self.main_loop.run()  # type: ignore[union-attr]
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop application work and quit main loop"""
        now = datetime.now()

        finish_time = now
        work_time = finish_time - self.start_time
        work_time -= timedelta(microseconds=work_time.microseconds)

        finish_msg = self.localizator.get('notification.finish', finish_time=finish_time.strftime("%H:%M:%S"))
        work_time_msg = self.localizator.get('notification.work_time', work_time=work_time)

        self.logger.debug(f'{finish_msg}\n{work_time_msg}')

        self.logger.info('              title |          work_time |            off_time')
        self.logger.info('--------------------------------------------------------------')

        for holder_item in self.holder.items():
            title, stat = holder_item

            padded_title = title.rjust(19, ' ')
            padded_work_time = f'{stat.work_time}'.rjust(19, ' ')
            padded_off_time = f'{stat.off_time}'.rjust(20, ' ')
            self.logger.info(f'{padded_title} |{padded_work_time} |{padded_off_time}')

        self.new_notification(msg=f'{finish_msg}; {work_time_msg}').show()
        Notify.uninit()

        self.main_loop.quit()  # type: ignore[union-attr]

    def __on_close_item_click(self, menu_item: Gtk.MenuItem) -> None:
        self.stop()

    def __on_open_report_item_click(self, menu_item: Gtk.MenuItem) -> None:
        """Open page with report in browser"""
        browser = webbrowser.get(self.config_reader.get_report_server_browser())
        host = self.config_reader.get_report_server_host()
        port = self.config_reader.get_report_server_port()
        url = f'http://{host}:{port}'

        browser.open_new_tab(url)

    def __on_edit_config_item_click(self, menu_item: Gtk.MenuItem) -> None:
        subprocess.run(['xdg-open', f'{self.files_provider.config_path}'])

    def __on_open_data_dir_item_click(self, menu_item: Gtk.MenuItem) -> None:
        subprocess.run(['xdg-open', f'{self.files_provider.raw_data_dir}'])

    def set_work_time_state(self, value: bool) -> None:
        """
        Try to change work time state. It can be True (working time) or False (not working time).
        If changed successfully, tray icon & work state checkbox in menu should also change
        """
        if value == self.is_work_time:
            self.logger.debug('Trying to change is_work_time to the same value')
            return

        self.is_work_time = value
        self.work_state_checkbox_item.set_active(self.is_work_time)

        current_activity = Value.get_or_raise(self.current_activity, 'current_activity')
        now = datetime.now()
        new_activity = Activity(current_activity.wm_class,
                                current_activity.window_name,
                                now,
                                self.is_work_time)

        self.__on_activity_changed(current_activity, new_activity)

        self.is_work_time_update_time = now

        self.logger.debug(f'Set Work Time to [{self.is_work_time}]')

        icon = self.active_icon if self.is_work_time else self.disabled_icon
        self.tray_icon.set_icon_if_exist(icon)

        if self.is_work_time:
            self.last_lock_screen_time = now
            self.last_break_notification = None
            self.last_overtime_notification = None

    def on_work_state_checkbox_item_click(self, menu_item: Gtk.CheckMenuItem) -> None:
        """Reverse work time state"""
        self.set_work_time_state(not self.is_work_time)

    def __create_work_state_checkbox_item(self) -> Gtk.CheckMenuItem:
        work_state_checkbox_item = Gtk.CheckMenuItem(self.localizator.get('tray.work_time'))
        work_state_checkbox_item.connect('activate', self.on_work_state_checkbox_item_click)

        return work_state_checkbox_item

    def create_tray_menu(self, work_state_checkbox_item: Gtk.CheckMenuItem) -> Gtk.Menu:
        menu = Gtk.Menu()

        menu.append(work_state_checkbox_item)

        open_report_item = Gtk.MenuItem(self.localizator.get('tray.open_report'))
        open_report_item.connect('activate', self.__on_open_report_item_click)
        menu.append(open_report_item)

        menu.append(Gtk.SeparatorMenuItem())

        edit_config_item = Gtk.MenuItem(self.localizator.get('tray.edit_config'))
        edit_config_item.connect('activate', self.__on_edit_config_item_click)
        menu.append(edit_config_item)

        open_data_dir_item = Gtk.MenuItem(self.localizator.get('tray.open_data_dir'))
        open_data_dir_item.connect('activate', self.__on_open_data_dir_item_click)
        menu.append(open_data_dir_item)

        menu.append(Gtk.SeparatorMenuItem())

        close_item = Gtk.MenuItem(self.localizator.get('tray.close'))
        close_item.connect('activate', self.__on_close_item_click)
        menu.append(close_item)

        menu.show_all()

        return menu

    def __on_overtime_notification_closed(self) -> None:
        self.is_overtime_notification_allowed_to_show = True

    def __on_finish_work_action_clicked(self) -> None:
        self.set_work_time_state(False)

    def __on_take_break_clicked(self) -> None:
        self.__dbus_lock_screen()

    def new_notification(self,
                         msg: str,
                         urgency: Optional[Notify.Urgency] = None,
                         listen_closed_event: bool = False) -> Notification:
        # TODO: replace with NotificationFactory (Factory Pattern)
        return Notification('Speaking Eye', msg, self.active_icon, urgency, listen_closed_event)

    def show_overtime_notification(self) -> None:
        msg = self.localizator.get('notification.overtime.text', hours=self.user_work_time_hour_limit)

        notification = self.new_notification(msg, Notify.Urgency.CRITICAL, listen_closed_event=True)

        notification.add_buttons((
            self.localizator.get('notification.overtime.left_button'),  # finish_work
            self.localizator.get('notification.overtime.right_button')  # remind_later
        ))

        notification.event.on(NotificationEvent.CLOSED.value, self.__on_overtime_notification_closed)
        notification.event.on(NotificationEvent.LEFT_BUTTON_CLICKED.value, self.__on_finish_work_action_clicked)

        notification.show()

        self.last_overtime_notification = notification
        self.is_overtime_notification_allowed_to_show = False

    def show_distracting_app_overtime_notification(self, title: str, total_time: timedelta) -> None:
        distracting_minutes = total_time.total_seconds() // 60
        text = self.localizator.get_random('notification.distracting_texts', 10)
        emoji = choice(DISTRACTING_NOTIFICATION_EMOJIS)
        msg = self.localizator.get('notification.distracting', app_title=title,
                                   distracting_minutes=int(distracting_minutes),
                                   text=text, emoji=emoji)

        self.new_notification(msg).show()

    def __on_break_notification_closed(self) -> None:
        self.is_break_notification_allowed_to_show = True

    def show_break_notification(self) -> None:
        emoji = choice(BREAK_TIME_EMOJIS)
        msg = self.localizator.get('notification.break.text', emoji=emoji)

        notification = self.new_notification(msg, Notify.Urgency.CRITICAL, listen_closed_event=True)

        notification.add_buttons((
            self.localizator.get('notification.break.left_button'),  # take_break
            self.localizator.get('notification.break.right_button')  # remind_later
        ))

        notification.event.on(NotificationEvent.CLOSED.value, self.__on_break_notification_closed)
        notification.event.on(NotificationEvent.LEFT_BUTTON_CLICKED.value, self.__on_take_break_clicked)

        notification.show()

        self.last_break_notification = notification
        self.is_break_notification_allowed_to_show = False

    def __on_new_day_started(self) -> None:
        """Reset work time state"""
        open_new_file_msg = self.localizator.get('notification.new_day')

        self.logger.debug(open_new_file_msg)
        self.new_notification(msg=open_new_file_msg).show()

        self.set_work_time_state(False)

    def handle_sigterm(self, signal_number: int, frame: FrameType) -> None:
        self.stop()

    def __need_to_show_overtime_notification(self) -> bool:
        if not self.is_work_time:
            return False

        if self.is_lock_screen_activated:
            return False

        now = datetime.now()
        current_activity = Value.get_or_raise(self.current_activity, 'current_activity')
        seconds_in_current_activity = (now - current_activity.start_time).total_seconds()
        total_work_time_seconds = seconds_in_current_activity + self.holder.total_work_time.total_seconds()
        is_overtime_started = total_work_time_seconds >= self.user_work_time_hour_limit * 60 * 60

        if not is_overtime_started:
            return False

        if self.last_overtime_notification is None:
            return True

        if self.last_overtime_notification.last_shown is None:
            return True

        if not self.is_overtime_notification_allowed_to_show:
            return False

        seconds_from_last_notification = (now - self.last_overtime_notification.last_shown).total_seconds()
        interval_seconds = 15 * 60

        return seconds_from_last_notification >= interval_seconds

    def overtime_timer_handler(self) -> None:
        if not self.__need_to_show_overtime_notification():
            return

        self.show_overtime_notification()

    def __need_to_show_break_notification(self) -> bool:
        if not self.is_work_time:
            return False

        if self.is_lock_screen_activated:
            return False

        if not self.is_break_notification_allowed_to_show:
            return False

        now = datetime.now()
        start_work_time = self.is_work_time_update_time
        last_break_time = self.last_lock_screen_time if self.last_lock_screen_time else start_work_time

        if (now - last_break_time).total_seconds() < self.user_breaks_interval_hours * 60 * 60:
            return False

        last_break_reminder_time = Value.get_by_getter_or_default(
            lambda: self.last_break_notification.last_shown,  # type: ignore[union-attr]
            start_work_time
        )

        if (now - last_break_reminder_time).total_seconds() < 15 * 60:
            return False

        return True

    def break_timer_handler(self) -> None:
        if not self.__need_to_show_break_notification():
            return

        self.show_break_notification()

    def distracting_app_timer_handler(self) -> None:
        # TODO: ⚡️ run this timer only if work started
        if not self.is_work_time:
            return

        if self.has_distracting_app_overtime_notification_shown:
            return

        current_activity = Value.get_or_raise(self.current_activity, 'current_activity')
        application_info = current_activity.application_info

        if application_info is None:
            # NOTE: It is None if detailed/distracting lists do not contain such activity
            #       See more in ApplicationInfoMatcher.set_if_matched()
            return

        if not application_info.is_distracting:
            return

        now = datetime.now()
        current_stats = self.holder[application_info.title]
        total_distracting_time = now - current_activity.start_time + current_stats.work_time

        if total_distracting_time.total_seconds() < self.user_distracting_apps_mins * 60:
            return

        self.event.emit(ApplicationEvent.DISTRACTING_APP_OVERTIME.value, application_info.title, total_distracting_time)

        self.has_distracting_app_overtime_notification_shown = True

    def get_icon(self, icon_state: IconState) -> Path:
        if not self.theme:
            raise Exception('self.theme should be set!')

        path = self.files_provider.get_icon_file_path(self.theme, icon_state)

        if not path.exists():
            self.logger.warning(f'Icon [{path}] not found')

        return path
