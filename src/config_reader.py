from enum import Enum
from typing import Any, List, Dict, Optional, cast

from pydash import get

from application_info import ApplicationInfo
from application_info_reader import ApplicationInfoReader
from language import Language
from theme import Theme


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

        app_list = get(self.config, apps_list_node)

        is_distracting = config_key == self.ConfigKey.DISTRACTING_NODE

        if app_list is not None:
            return self.application_info_reader.try_read(app_list, is_distracting)

        if is_distracting:
            return []

        raise RuntimeError(f'Path [{apps_list_node}] should be set in config!')

    # TODO: for all get_* funcs need to validate value type (e.g. work_time_hours must be int)
    def get_work_time_limit(self) -> int:
        return get(self.config, 'time_limits.work_time_hours') or 9

    def get_breaks_interval_hours(self) -> int:
        return get(self.config, 'time_limits.breaks_interval_hours') or 3

    def get_distracting_apps_mins(self) -> int:
        return get(self.config, 'time_limits.distracting_apps_mins') or 15

    def get_report_server_host(self) -> str:
        return get(self.config, 'report_server.host') or 'localhost'

    def get_report_server_port(self) -> int:
        return get(self.config, 'report_server.port') or 3838

    def get_report_server_browser(self) -> Optional[str]:
        return cast(Optional[str], get(self.config, 'report_server.browser', default=None))

    def get_report_server_ignore_weekends(self) -> bool:
        return cast(bool, get(self.config, 'report_server.ignore_weekends', default=True))

    def get_language(self) -> Language:
        return Language.parse(get(self.config, 'language'), Language.ENGLISH)

    def get_theme(self) -> Theme:
        return Theme.parse(get(self.config, 'theme'), Theme.DARK)
