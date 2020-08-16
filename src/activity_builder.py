from datetime import datetime
from typing import Optional

from activity import Activity


class ActivityBuilder:
    """Implementation of the Builder pattern for easy building Activity objects"""

    def __init__(self, origin_activity: Activity) -> None:
        self.origin_activity = origin_activity
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def with_start_time(self, value) -> 'ActivityBuilder':
        self.start_time = value

        return self

    def with_end_time(self, value) -> 'ActivityBuilder':
        self.end_time = value

        return self

    def build(self) -> Activity:
        if self.start_time is None:
            raise RuntimeError('start_time should be set!')

        if self.end_time is None:
            raise RuntimeError('end_time should be set!')

        activity = Activity(
            self.origin_activity.wm_class,
            self.origin_activity.window_name,
            self.start_time,
            self.origin_activity.is_work_time
        )

        activity.set_end_time(self.end_time)

        return activity
