from re import search
from typing import List, Optional

from activity import Activity
from application_info import ApplicationInfo


class ApplicationInfoMatcher:
    """
    Match ApplicationInfo with Activity
    to distinguish between different types of activities/infos (e.g. 'detailed/distracting')
    """

    def __init__(self, detailed_app_infos: List[ApplicationInfo], distracting_app_infos: List[ApplicationInfo]) -> None:
        self.detailed_app_infos = detailed_app_infos
        self.distracting_app_infos = distracting_app_infos

    def __try_find_app_info_in(self, app_infos: List[ApplicationInfo], activity: Activity) -> Optional[ApplicationInfo]:
        """Using Activity wm_class and window_name try to find corresponding ApplicationInfo"""

        for app_info in app_infos:
            # tab can be empty str, it means that we are considering all tabs
            # search('', whatever) always return SRE_Match object
            if search(app_info.wm_name, activity.wm_class) and search(app_info.tab, activity.window_name):
                return app_info

        return None

    def set_if_matched(self, activity: Activity) -> None:
        """Set ApplicationInfo to Activity if matched"""

        application_info = self.__try_find_app_info_in(
            self.distracting_app_infos, activity) or self.__try_find_app_info_in(self.detailed_app_infos, activity)

        if application_info is None:
            return

        activity.set_application_info(application_info)
