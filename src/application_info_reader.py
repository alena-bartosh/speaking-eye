from enum import Enum
from typing import Dict, List

from application_info import ApplicationInfo

WM_NAME_KEY = 'wm_name'
TAB_KEY = 'tab'


class SpecialApplicationInfo(Enum):
    NONE = 'none'

    @staticmethod
    def list():
        return [special.value for special in SpecialApplicationInfo]


class ApplicationInfoReader:

    def __handle_special_case(self, special_case: SpecialApplicationInfo, is_distracting: bool) -> ApplicationInfo:
        return ApplicationInfo(special_case.value, '', '', is_distracting)

    def __handle_regular_case(self, data_item: Dict[str, Dict], is_distracting: bool) -> ApplicationInfo:
        raw_app_info, = data_item.items()
        app_name, app_info = raw_app_info

        is_special_case_used_as_app_name = app_name in SpecialApplicationInfo.list()

        if is_special_case_used_as_app_name:
            raise ValueError(f'Special cases [{SpecialApplicationInfo.list()}] with ":" are not supported!')

        wm_name = app_info[WM_NAME_KEY] if WM_NAME_KEY in app_info else ''
        tab = app_info[TAB_KEY] if TAB_KEY in app_info else ''

        if not wm_name and not tab:
            raise ValueError(f'Application [{app_name}] has empty wm_name and tab!')

        return ApplicationInfo(app_name, wm_name, tab, is_distracting)

    def try_read(self, data: List, is_distracting: bool) -> List[ApplicationInfo]:
        if not isinstance(data, list):
            raise ValueError(f'Incorrect data type [{type(data)}]!')

        if len(data) == 0:
            raise ValueError('Empty data!')

        result = []

        for data_item in data:
            is_special_case = data_item in SpecialApplicationInfo.list()

            if not is_special_case and isinstance(data_item, str):
                raise ValueError(f'Only special cases [{SpecialApplicationInfo.list()}] can be here '
                                 f'or list of apps with wm_name and tab!')

            if is_special_case:
                has_other_application_infos = len(data) > 1
                special_case = SpecialApplicationInfo(data_item)

                if has_other_application_infos:
                    raise ValueError(f'Special case [{special_case.value}] must be the only one in a list!')

                result.append(self.__handle_special_case(special_case, is_distracting))
            else:
                result.append(self.__handle_regular_case(data_item, is_distracting))

        return result
