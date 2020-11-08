from datetime import timedelta

from activity import Activity
from activity_helper import ActivityHelper


class ActivityStat:
    """Store and update the amount of time spent in a certain activity"""

    def __init__(self, work_time: timedelta = timedelta(), off_time: timedelta = timedelta()) -> None:
        """Can be used for the first reading ApplicationInfo
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
            work_time = activity.activity_time
            off_time = timedelta()
        else:
            work_time = timedelta()
            off_time = activity.activity_time

        return ActivityStat(work_time, off_time)

    # TODO: check whether activity the same as in from_activity()
    def update(self, activity: Activity) -> None:
        ActivityHelper.raise_if_not_finished(activity)

        if activity.is_work_time:
            self.work_time += activity.activity_time
        else:
            self.off_time += activity.activity_time
