from datetime import timedelta

from activity import Activity
from activity_converter import ActivityConverter


class ActivityHelper:
    """Extra methods for working with Activity objects"""

    @staticmethod
    def raise_if_not_finished(activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished!')

    @staticmethod
    def get_activity_time(activity: Activity) -> timedelta:
        ActivityHelper.raise_if_not_finished(activity)

        if activity.activity_time is None:
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] activity_time is None!')

        return activity.activity_time
