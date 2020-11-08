from datetime import timedelta, datetime, date
from typing import List

from activity import Activity
from activity_converter import ActivityConverter
from datetime_helper import DatetimeHelper


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

    @staticmethod
    def get_end_time(activity: Activity) -> datetime:
        ActivityHelper.raise_if_not_finished(activity)

        if activity.end_time is None:
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] end_time is None!')

        return activity.end_time

    @staticmethod
    def get_days(activity: Activity) -> List[date]:
        return DatetimeHelper.get_dates_between(activity.start_time.date(),
                                                ActivityHelper.get_end_time(activity).date())
