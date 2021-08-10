from enum import Enum
from typing import Any, List, Dict, Optional

from pydash import get

from .application_info import ApplicationInfo
from .application_info_reader import ApplicationInfoReader
from .language import Language
from .theme import Theme
from .typed_value import TypedValue


class ConfigReader:
    """
    Parse config and get values from it.
    Allows to create application info lists based on config nodes
    """
    ConfigType = Dict[str, Any]

    class ConfigKey(Enum):
        DETAILED_NODE = 'detailed'
        DISTRACTING_NODE = 'distracting'

    def __init__(self,
                 application_info_reader: ApplicationInfoReader,
                 config: ConfigType) -> None:
        self.application_info_reader = application_info_reader
        self.config = config

    def try_read_application_info_list(self, config_key: ConfigKey) -> List[ApplicationInfo]:
        """Try to read detailed/distracting ApplicationInfos from app config"""
        apps_list_node = f'apps.{config_key.value}'

        # TODO: get with TypedValue.get() to check types
        app_list = get(self.config, apps_list_node)

        is_distracting = config_key == self.ConfigKey.DISTRACTING_NODE

        if app_list is not None:
            return self.application_info_reader.try_read(app_list, is_distracting)

        if is_distracting:
            return []

        raise RuntimeError(f'Path [{apps_list_node}] should be set in config!')

    def get_work_time_limit(self) -> int:
        return TypedValue.get(self.config, 'time_limits.work_time_hours', int, 9)

    def get_breaks_interval_hours(self) -> int:
        return TypedValue.get(self.config, 'time_limits.breaks_interval_hours', int, 3)

    def get_distracting_apps_mins(self) -> int:
        return TypedValue.get(self.config, 'time_limits.distracting_apps_mins', int, 15)

    def get_report_server_host(self) -> str:
        return TypedValue.get(self.config, 'report_server.host', str, 'localhost')

    def get_report_server_port(self) -> int:
        return TypedValue.get(self.config, 'report_server.port', int, 3838)

    def get_report_server_browser(self) -> Optional[str]:
        return TypedValue.get(self.config, 'report_server.browser', Optional[str], None)  # type: ignore[arg-type]

    def get_report_server_ignore_weekends(self) -> bool:
        return TypedValue.get(self.config, 'report_server.ignore_weekends', bool, True)

    def get_language(self) -> Language:
        return Language.parse(get(self.config, 'language'), Language.ENGLISH)

    def get_theme(self) -> Theme:
        return Theme.parse(get(self.config, 'theme'), Theme.DARK)
