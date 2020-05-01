from gi.repository import AppIndicator3 as AppIndicator


class TrayIcon:
    def __init__(self, app_id, icon, menu):
        self.menu = menu

        self.ind = AppIndicator.Indicator.new(app_id, '', AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_icon(icon)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_menu(self.menu)
