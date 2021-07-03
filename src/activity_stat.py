from datetime import timedelta

from activity import Activity
from activity_helper import ActivityHelper


class ActivityStat:
    """Store and update the amount of time spent in a certain activity"""

    def __init__(self, work_time: timedelta = timedelta(),
                 off_time: timedelta = timedelta()) -> None:
        """
        Can be used for the first reading ApplicationInfo
        from detailed/distracting lists when no activity has started yet
        """
        self.work_time = work_time
        self.off_time = off_time

    @staticmethod
    def from_activity(activity: Activity) -> 'ActivityStat':
        """For creating ActivityStat when Activity has already started"""

        ActivityHelper.raise_if_not_finished(activity)

        # NOTE: for distracting activity work_time is distracting time

        if activity.is_work_time:
            work_time = ActivityHelper.get_activity_time(activity)
            off_time = timedelta()
        else:
            work_time = timedelta()
            off_time = ActivityHelper.get_activity_time(activity)

        return ActivityStat(work_time, off_time)

    def update(self, activity: Activity) -> None:
        ActivityHelper.raise_if_not_finished(activity)

        if activity.is_work_time:
            self.work_time += ActivityHelper.get_activity_time(activity)
        else:
            self.off_time += ActivityHelper.get_activity_time(activity)
