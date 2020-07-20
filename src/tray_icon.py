import os
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Gtk

FALLBACK_ICON = 'face-monkey'


class TrayIcon:
    def __init__(self, app_id: str, icon: str, menu: Gtk.Menu) -> None:
        self.menu = menu

        self.indicator = \
            AppIndicator.Indicator.new(app_id, FALLBACK_ICON, AppIndicator.IndicatorCategory.APPLICATION_STATUS)

        self.set_icon_if_exist(icon)

        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

    def set_icon_if_exist(self, icon: str) -> None:
        if os.path.exists(icon):
            self.indicator.set_icon(icon)
