from enum import Enum
from typing import List

from application_info import ApplicationInfo

WM_NAME_KEY = 'wm_name'
TAB_KEY = 'tab'


class SpecialApplicationInfo(Enum):
    ALL = 'all'
    NONE = 'none'

    @staticmethod
    def list():
        return [special.value for special in SpecialApplicationInfo]


class ApplicationInfoReader:

    def try_read(self, data: List) -> List[ApplicationInfo]:
        if not isinstance(data, list):
            raise ValueError(f'Incorrect data type [{type(data)}]!')

        if len(data) == 0:
            raise ValueError('Empty data!')

        result = []

        for data_item in data:
            if data_item in SpecialApplicationInfo.list():
                special_case = data_item
                has_other_application_infos = len(data) > 1

                if has_other_application_infos:
                    raise ValueError(f'Special case [{special_case}] must be the only one in a list!')

                app_info = ApplicationInfo(special_case, '', '')
                result.append(app_info)

            raw_app_info, = data_item.items()
            app_name, app_info = raw_app_info

            wm_name = app_info[WM_NAME_KEY] if WM_NAME_KEY in app_info else ''
            tab = app_info[TAB_KEY] if TAB_KEY in app_info else ''

            if not wm_name and not tab:
                raise ValueError(f'Application [{app_name}] has empty wm_name and tab!')

            app_info = ApplicationInfo(app_name, wm_name, tab)
            result.append(app_info)

        return result
