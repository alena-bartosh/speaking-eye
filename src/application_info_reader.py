from typing import Dict, List

from application_info import ApplicationInfo

WM_NAME_KEY = 'wm_name'
TAB_KEY = 'tab'

DataItemType = Dict[
    str,  # app_name
    Dict[
        str,  # wm_name or tab
        str  # value
    ]
]


class ApplicationInfoReader:
    """
    Try to read data items that consist of app name (title), wm_name, tab
    and create collection of ApplicationInfo
    """

    def __handle_regular_case(self, data_item: DataItemType, is_distracting: bool) -> ApplicationInfo:
        raw_app_info, = data_item.items()
        app_name, app_info = raw_app_info

        wm_name = app_info[WM_NAME_KEY] if WM_NAME_KEY in app_info else ''
        tab = app_info[TAB_KEY] if TAB_KEY in app_info else ''

        if not wm_name and not tab:
            raise ValueError(f'Application [{app_name}] has empty wm_name and tab!')

        return ApplicationInfo(app_name, wm_name, tab, is_distracting)

    def try_read(self, data: List[DataItemType], is_distracting: bool) -> List[ApplicationInfo]:
        if not isinstance(data, list):
            raise ValueError(f'Incorrect data type [{type(data)}]!')

        if len(data) == 0:
            raise ValueError('Empty data!')

        result = []

        for data_item in data:
            if not isinstance(data_item, dict):
                raise ValueError(f'Application info [{data_item}] in detailed/distracting list should be an object!')

            result.append(self.__handle_regular_case(data_item, is_distracting))

        return result
