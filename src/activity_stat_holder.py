from datetime import timedelta
from typing import List, ItemsView, cast

from activity import Activity
from activity_helper import ActivityHelper
from activity_stat import ActivityStat
from application_info import ApplicationInfo

KeyType = str
ItemType = ActivityStat
ActivityStatHolderItemsType = ItemsView[KeyType, ItemType]


class ActivityStatHolder(dict):  # type: ignore[type-arg]
    """Store ActivityStat objects and compute total time spent in all activities"""

    def __init__(self, activities: List[Activity]) -> None:
        super().__init__()

        self.total_work_time = timedelta()
        self.total_off_time = timedelta()

        for activity in activities:
            self.update_stat(activity)

    def initialize_stats(self, application_infos: List[ApplicationInfo]) -> None:
        for application_info in application_infos:
            if application_info.title in self:
                continue

            self[application_info.title] = ActivityStat()

    def update_stat(self, activity: Activity) -> None:
        if activity.is_work_time:
            self.total_work_time += ActivityHelper.get_activity_time(activity)
        else:
            self.total_off_time += ActivityHelper.get_activity_time(activity)

        title_from_config = activity.application_info.title if activity.application_info is not None else 'Others'

        if title_from_config not in self:
            self[title_from_config] = ActivityStat.from_activity(activity)

            return

        activity_stat = self[title_from_config]
        activity_stat.update(activity)

    def get_group_work_time(self, titles: List[str]) -> timedelta:
        """Compute total work time for the specific group of ActivityStat titles"""
        result = timedelta()

        for title in titles:
            if title not in self:
                raise RuntimeError(f'ActivityStatHolder does not contain stat for [ActivityStat.title={title}]!')

            result += self[title].work_time

        return result

    # NOTE: override the default implementations just to use our typing

    def __setitem__(self, app_name: KeyType, item: ItemType) -> None:
        super().__setitem__(app_name, item)

    def __getitem__(self, app_name: KeyType) -> ItemType:
        return cast(ItemType, super().__getitem__(app_name))

    def __contains__(self, app_name: KeyType) -> bool:  # type: ignore[override]
        return super().__contains__(app_name)

    def items(self) -> ActivityStatHolderItemsType:
        return super().items()
