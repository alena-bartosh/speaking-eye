__author__ = 'alena-bartosh'

import argparse
import fcntl
import logging
import os
import sys
import tempfile
import threading
from pathlib import Path
from typing import Dict

import coloredlogs
import gi
import yaml

from activity_reader import ActivityReader
from application_info import ApplicationInfo
from application_info_matcher import ApplicationInfoMatcher
from application_info_reader import ApplicationInfoReader
from config_reader import ConfigReader
from dash_report_server import DashReportServer
from files_provider import FilesProvider
from special_application_info_title import SpecialApplicationInfoTitle
from special_wm_class import SpecialWmClass

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from speaking_eye_app import SpeakingEyeApp  # noqa: E402

APP_ID = 'speaking-eye'


def app_exit(logger: logging.Logger, msg: str) -> None:
    logger.error(msg)
    sys.exit(1)


def dash_report_server_main(logger: logging.Logger,
                            config: Dict,
                            config_reader: ConfigReader,
                            activity_reader: ActivityReader,
                            files_provider: FilesProvider) -> None:
    try:
        server = DashReportServer(logger, config, config_reader, activity_reader, files_provider)
        server.run()
    except Exception:
        logger.exception('Could not start Report Server!')


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    config_full_path = os.path.join(src_dir, '../config/config_example.yaml')

    parser = argparse.ArgumentParser(description=f'[{APP_ID}] Track & analyze your computer activity')
    parser.add_argument('--log-level', type=str, choices=['debug', 'info', 'warning', 'error'],
                        default='debug', metavar='', help='debug/info/warning/error')
    parser.add_argument('-c', '--config', type=str, default=config_full_path, metavar='', help='config path')
    args = parser.parse_args()

    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    coloredlogs.install(log_level_map[args.log_level])
    logger = logging.getLogger(APP_ID)

    pid_file = f'{tempfile.gettempdir()}/{APP_ID}.pid'
    fp = open(pid_file, 'w')

    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        app_exit(logger, msg='Another instance is already running!')

    config = None
    error_config_msg = 'Speaking Eye does not work without config. Bye baby!'

    try:
        with open(args.config) as config_file:
            config = yaml.safe_load(config_file)
    except Exception:
        logger.exception(f'Config [{args.config}] is not correct')
        app_exit(logger, error_config_msg)

    if not config:
        logger.error(f'Config [{args.config}] is empty')
        app_exit(logger, error_config_msg)

    application_info_reader = ApplicationInfoReader()
    config_reader = ConfigReader(application_info_reader, config)
    detailed_app_infos = config_reader.try_read_application_info_list(ConfigReader.ConfigKey.DETAILED_NODE)

    # NOTE: Implicitly add LockScreen to monitor Break Time activity
    #       to not to add this info at user detailed apps config
    break_time_activity_info = ApplicationInfo(SpecialApplicationInfoTitle.BREAK_TIME.value,
                                               SpecialWmClass.LOCK_SCREEN.value,
                                               tab_re='',
                                               is_distracting=False)
    detailed_app_infos.append(break_time_activity_info)

    distracting_app_infos = config_reader.try_read_application_info_list(
        ConfigReader.ConfigKey.DISTRACTING_NODE)
    application_info_matcher = ApplicationInfoMatcher(detailed_app_infos, distracting_app_infos)
    activity_reader = ActivityReader(logger, application_info_matcher)

    current_file_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    app_root_dir = current_file_dir / '..'
    files_provider = FilesProvider(app_root_dir)

    dash_server_thread = threading.Thread(target=dash_report_server_main,
                                          kwargs={
                                              'config': config,
                                              'config_reader': config_reader,
                                              'logger': logger,
                                              'activity_reader': activity_reader,
                                              'files_provider': files_provider,
                                          },
                                          daemon=True)
    dash_server_thread.start()

    app = SpeakingEyeApp(APP_ID,
                         config,
                         config_reader,
                         logger,
                         application_info_matcher,
                         activity_reader,
                         files_provider)
    app.run()
    app.start_main_loop()


if __name__ == '__main__':
    main()
