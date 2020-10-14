from datetime import timedelta
from typing import List

from activity import Activity
from activity_stat import ActivityStat

KeyType = str
ItemType = ActivityStat


class ActivityStatHolder(dict):
    """Store ActivityStat objects and compute total time spent in all activities"""

    def __init__(self, activities: List[Activity]) -> None:
        super().__init__()

        self.total_work_time = timedelta()
        self.total_off_time = timedelta()

        for activity in activities:
            self.update_stat(activity)

    def update_stat(self, activity: Activity) -> None:
        if activity.is_work_time:
            self.total_work_time += activity.activity_time
        else:
            self.total_off_time += activity.activity_time

        if activity.application_info is None:
            return

        title_from_config = activity.application_info.name

        if title_from_config not in self:
            self[title_from_config] = ActivityStat(activity)

            return

        activity_stat = self[title_from_config]
        activity_stat.update(activity)

    # NOTE: override the default implementations just to use our typing

    def __setitem__(self, app_name: KeyType, item: ItemType) -> None:
        super().__setitem__(app_name, item)

    def __getitem__(self, app_name: KeyType) -> ItemType:
        return super().__getitem__(app_name)

    def __contains__(self, app_name: KeyType) -> bool:
        return super().__contains__(app_name)
