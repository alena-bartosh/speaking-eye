from datetime import timedelta

from activity import Activity
from activity_converter import ActivityConverter


# TODO: replace app_name with title


class ActivityStat:
    def __init__(self, activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished '
                             f'before creating ActivityStat!')

        self.app_name = activity.app_name

        if activity.is_work_time:
            self.work_time = activity.activity_time
            self.off_time = timedelta()
        else:
            self.work_time = timedelta()
            self.off_time = activity.activity_time

    def update(self, activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished '
                             f'before updating ActivityStat!')

        if activity.is_work_time:
            self.work_time += activity.activity_time
        else:
            self.off_time += activity.activity_time