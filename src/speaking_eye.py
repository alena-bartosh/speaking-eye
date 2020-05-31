__author__ = 'alena-bartosh'

import gi

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

import argparse
import coloredlogs
import logging
import os
import sys
import yaml

from speaking_eye_app import SpeakingEyeApp

APP_ID = 'speaking-eye'


def app_exit(logger: logging.Logger, msg: str) -> None:
    logger.error(msg)
    sys.exit(1)


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    config_full_path = os.path.join(src_dir, '../config/config.yaml')

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

    app = SpeakingEyeApp(APP_ID, config, logger)
    app.run(sys.argv)
    app.start_main_loop()


if __name__ == '__main__':
    main()
