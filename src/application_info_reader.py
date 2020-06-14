from typing import List

from application_info import ApplicationInfo

WM_NAME_KEY = 'wm_name'
TAB_KEY = 'tab'


class ApplicationInfoReader:

    def try_read(self, data: List) -> List[ApplicationInfo]:
        if not isinstance(data, list):
            raise ValueError(f'Incorrect data type [{type(data)}]!')

        if len(data) == 0:
            raise ValueError('Empty data!')

        result = []

        for data_item in data:
            raw_app_info, = data_item.items()
            app_name, app_info = raw_app_info

            # TODO: handle 'all' and 'none' cases

            wm_name = app_info[WM_NAME_KEY] if WM_NAME_KEY in app_info else ''
            tab = app_info[TAB_KEY] if TAB_KEY in app_info else ''

            if not wm_name and not tab:
                raise ValueError(f'Application [{app_name}] has empty wm_name and tab!')

            app_info = ApplicationInfo(app_name, wm_name, tab)
            result.append(app_info)

        return result
