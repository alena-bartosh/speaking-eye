import argparse
import fcntl
import logging
import os
import sys
import tempfile
import threading
from pathlib import Path
from shutil import copy
from typing import List, Optional

import coloredlogs
import gi
import yaml

from .activity_reader import ActivityReader
from .application_info import ApplicationInfo
from .application_info_matcher import ApplicationInfoMatcher
from .application_info_reader import ApplicationInfoReader
from .config_reader import ConfigReader
from .dash_report_server import DashReportServer
from .files_provider import FilesProvider
from .localizator import Localizator
from .special_application_info_title import SpecialApplicationInfoTitle
from .special_wm_class import SpecialWmClass

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from .speaking_eye_app import SpeakingEyeApp  # noqa: E402

APP_ID = 'speaking-eye'


def app_exit_with_failure(logger: logging.Logger, msg: str) -> None:
    logger.error(msg)
    sys.exit(1)


def dash_report_server_main(logger: logging.Logger,
                            config_reader: ConfigReader,
                            activity_reader: ActivityReader,
                            files_provider: FilesProvider,
                            localizator: Localizator) -> None:
    try:
        server = DashReportServer(logger, config_reader, activity_reader, files_provider, localizator)
        server.run()
    except Exception:
        logger.exception('Could not start Report Server!')


def make_autostartable_if_needed(config_reader: ConfigReader,
                                 files_provider: FilesProvider,
                                 logger: logging.Logger) -> None:
    autostart_file_path = files_provider.autostart_file_path

    if not config_reader.get_autostart():
        if autostart_file_path.exists():
            logger.debug(f'Remove [{autostart_file_path}] since [autostart=False] '
                         f'and file exists...')
            autostart_file_path.unlink()

        return

    if not autostart_file_path.exists():
        logger.debug(f'Copy [{files_provider.desktop_file_path}] into [{autostart_file_path}] '
                     f'since [autostart=True] and file does not exist...')
        copy(files_provider.desktop_file_path, autostart_file_path)


def main() -> None:
    current_file_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    files_provider = FilesProvider(current_file_dir, APP_ID)
    default_config_path = str(files_provider.default_config_path)

    parser = argparse.ArgumentParser(description=f'[{APP_ID}] Track & analyze your computer activity')
    parser.add_argument('--log-level', type=str, choices=['debug', 'info', 'warning', 'error'],
                        default='debug', metavar='', help='debug/info/warning/error')
    parser.add_argument('-c', '--config', type=str, default=default_config_path, metavar='', help='config path')
    args = parser.parse_args()

    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    coloredlogs.install(log_level_map[args.log_level])
    logger = logging.getLogger(APP_ID)

    # TODO: Support Wayland (new display server protocol)
    if os.getenv('XDG_SESSION_TYPE') != 'x11':
        error_xdg_session_msg = 'Sorry, Speaking eye supports only x11 windows manager for now!'
        app_exit_with_failure(logger, error_xdg_session_msg)

    # TODO: It can be extracted into separate package with name like "run_once" -->
    pid_file = f'{tempfile.gettempdir()}/{APP_ID}.pid'
    fp = open(pid_file, 'w')

    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        app_exit_with_failure(logger, msg='Another instance is already running!')
    # <--

    error_config_msg = 'Speaking Eye does not work without config. Bye baby!'

    try:
        files_provider.config_path = args.config
    except Exception:
        logger.exception(f'Error during config path [{args.config}] initialization!')
        app_exit_with_failure(logger, error_config_msg)

    logger.debug(f'Use config_path [{files_provider.config_path}]')

    config: Optional[ConfigReader.ConfigType] = None

    try:
        with open(str(files_provider.config_path)) as config_file:
            config = yaml.safe_load(config_file)
    except Exception:
        logger.exception(f'Config [{args.config}] is not correct')
        app_exit_with_failure(logger, error_config_msg)

    if not config:
        logger.error(f'Config [{args.config}] is empty')
        app_exit_with_failure(logger, error_config_msg)
        # NOTE: return is needed for correct mypy checks (config type)
        return

    application_info_reader = ApplicationInfoReader()
    config_reader = ConfigReader(application_info_reader, config)

    make_autostartable_if_needed(config_reader, files_provider, logger)

    detailed_app_infos: Optional[List[ApplicationInfo]] = None
    distracting_app_infos: Optional[List[ApplicationInfo]] = None

    try:
        detailed_app_infos = config_reader.try_read_application_info_list(ConfigReader.ConfigKey.DETAILED_NODE)
        distracting_app_infos = config_reader.try_read_application_info_list(
            ConfigReader.ConfigKey.DISTRACTING_NODE)
    except Exception:
        logger.exception('Error while reading config!')
        app_exit_with_failure(logger, error_config_msg)
        # NOTE: return is needed for correct mypy checks (detailed_app_infos & distracting_app_infos types)
        return

    # NOTE: Implicitly add LockScreen to monitor Break Time activity
    #       to not to add this info at user detailed apps config
    break_time_activity_info = ApplicationInfo(SpecialApplicationInfoTitle.BREAK_TIME.value,
                                               SpecialWmClass.LOCK_SCREEN.value,
                                               tab_re='',
                                               is_distracting=False)
    detailed_app_infos.append(break_time_activity_info)

    application_info_matcher = ApplicationInfoMatcher(detailed_app_infos, distracting_app_infos)
    activity_reader = ActivityReader(logger, application_info_matcher)

    language = config_reader.get_language()
    localizator = Localizator(files_provider.i18n_dir, language)
    logger.debug(f'Set user language to [{language.value}]')

    dash_server_thread = threading.Thread(target=dash_report_server_main,
                                          kwargs={
                                              'config_reader': config_reader,
                                              'logger': logger,
                                              'activity_reader': activity_reader,
                                              'files_provider': files_provider,
                                              'localizator': localizator,
                                          },
                                          daemon=True)
    dash_server_thread.start()

    app = SpeakingEyeApp(app_id=APP_ID,
                         config_reader=config_reader,
                         logger=logger,
                         application_info_matcher=application_info_matcher,
                         activity_reader=activity_reader,
                         files_provider=files_provider,
                         localizator=localizator)
    app.run()
    app.start_main_loop()


if __name__ == '__main__':
    main()
