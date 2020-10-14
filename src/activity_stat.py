from datetime import timedelta

from activity import Activity
from activity_converter import ActivityConverter


class ActivityStat:
    """Store and update the amount of time spent in a certain activity"""

    def __init__(self, activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished '
                             f'before creating ActivityStat!')

        # NOTE: for distracting activity work_time is distracting time

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
