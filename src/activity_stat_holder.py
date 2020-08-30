from datetime import timedelta
from typing import List

from activity import Activity
from activity_stat import ActivityStat

KeyType = str
ItemType = ActivityStat


# TODO: replace app_name with title

class ActivityStatHolder(dict):

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

        if activity.app_name not in self:
            self[activity.app_name] = ActivityStat(activity)

            return

        activity_stat = self[activity.app_name]
        activity_stat.update(activity)

    # NOTE: override the default implementations just to use our typing

    def __setitem__(self, app_name: KeyType, item: ItemType) -> None:
        super().__setitem__(app_name, item)

    def __getitem__(self, app_name: KeyType) -> ItemType:
        return super().__getitem__(app_name)

    def __contains__(self, app_name: KeyType) -> bool:
        return super().__contains__(app_name)
