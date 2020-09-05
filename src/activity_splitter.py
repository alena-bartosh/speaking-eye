from datetime import date
from typing import List, Tuple

from activity import Activity
from activity_builder import ActivityBuilder
from datetime_helper import DatetimeHelper


class ActivitySplitter:
    """Split activity lasting several days into several activities"""

    @staticmethod
    def split_by_day(activity: Activity) -> List[Tuple[date, Activity]]:
        days = activity.get_days()
        first_day, last_day = days[0], days[-1]

        if first_day == last_day:
            return [(first_day, activity)]

        result = []

        for day in days:
            start_time, end_time = DatetimeHelper.get_date_range(day)

            new_activity = ActivityBuilder(activity)\
                .with_start_time(activity.start_time if day == first_day else start_time)\
                .with_end_time(activity.end_time if day == last_day else end_time)\
                .build()

            result.append((day, new_activity))

        return result
