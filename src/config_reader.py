from enum import Enum
from typing import List, Dict

from pydash import get

from application_info import ApplicationInfo
from application_info_reader import ApplicationInfoReader


class ConfigReader:
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
