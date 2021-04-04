from enum import Enum
from typing import List, Dict

from pydash import get

from application_info import ApplicationInfo
from application_info_reader import ApplicationInfoReader


class ConfigReader:
    # TODO: Add enum for all config keys

    class ConfigKey(Enum):
        DETAILED_NODE = 'detailed'
        DISTRACTING_NODE = 'distracting'

    def __init__(self,
                 application_info_reader: ApplicationInfoReader,
                 config: Dict) -> None:
        self.application_info_reader = application_info_reader
        self.config = config

    def try_read_application_info_list(self, config_key: ConfigKey) -> List[ApplicationInfo]:
        """Try to read detailed/distracting ApplicationInfos from app config"""
        apps_list_node = f'apps.{config_key.value}'

        app_list = get(self.config, apps_list_node)

        if app_list is None:
            raise RuntimeError(f'Path [{apps_list_node}] should be set in config!')

        is_distracting = config_key == self.ConfigKey.DISTRACTING_NODE

        return self.application_info_reader.try_read(app_list, is_distracting)

    def get_work_time_limit(self) -> int:
        """Read work time limit from app config or return default value"""
        return get(self.config, 'time_limits.work_time_hours') or 9

    def get_distracting_apps_mins(self) -> int:
        return get(self.config, 'time_limits.distracting_apps_mins') or 15

    def get_report_server_port(self) -> int:
        return get(self.config, 'report_server.port') or 3838
