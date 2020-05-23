import gi

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

import os
import sys
import yaml

from speaking_eye_app import SpeakingEyeApp


def main():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    config_full_path = os.path.join(src_dir, '../config/config.yaml')

    if not os.path.exists(config_full_path):
        raise Exception(f'Config [{config_full_path}] not found')

    config = None

    with open(config_full_path) as config_file:
        config = yaml.safe_load(config_file)

    app = SpeakingEyeApp(config)
    app.run(sys.argv)
    app.start_main_loop()


if __name__ == '__main__':
    main()
