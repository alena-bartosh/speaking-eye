from datetime import datetime, timedelta
from typing import Optional

from application_info import ApplicationInfo


class Activity:
    def __init__(self, wm_class: str, window_name: str, start_time: datetime, is_work_time: bool) -> None:
        self.wm_class = wm_class
        self.window_name = window_name
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.activity_time: Optional[timedelta] = None
        self.is_work_time = is_work_time
        self.application_info: Optional[ApplicationInfo] = None

    def set_end_time(self, end_time: datetime) -> 'Activity':
        if end_time < self.start_time:
            raise ValueError(f'end_time [{end_time}] should be greater than start_time [{self.start_time}]!')

        self.end_time = end_time
        self.activity_time = self.end_time - self.start_time

        return self

    def has_finished(self) -> bool:
        return self.end_time is not None

    def __eq__(self, other: object) -> bool:
        """
        Overrides the default implementation
        to use the object values instead of identifiers for comparison
        """
        if not isinstance(other, Activity):
            return False

        if self.wm_class != other.wm_class:
            return False

        if self.window_name != other.window_name:
            return False

        if self.start_time != other.start_time:
            return False

        if self.end_time != other.end_time:
            return False

        if self.activity_time != other.activity_time:  # pragma: no cover
            return False

        if self.is_work_time != other.is_work_time:
            return False

        return self.application_info == other.application_info

    def set_application_info(self, value: ApplicationInfo) -> None:
        self.application_info = value
