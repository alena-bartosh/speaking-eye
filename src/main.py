import gi

gi.require_version('Wnck', '3.0')
gi.require_version('Gtk', '3.0')

import sys

from speaking_eye_app import SpeakingEyeApp

if __name__ == '__main__':
    app = SpeakingEyeApp()
    app.run(sys.argv)
    app.start_main_loop()
