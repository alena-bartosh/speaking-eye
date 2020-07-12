from datetime import datetime, timedelta
from typing import Optional


class Activity:
    def __init__(self, wm_class: str, window_name: str, start_time: datetime, is_work_time: bool):
        self.wm_class = wm_class
        self.window_name = window_name
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.activity_time: Optional[timedelta] = None
        self.is_work_time = is_work_time

    def set_end_time(self, end_time: datetime) -> 'Activity':
        if end_time < self.start_time:
            raise ValueError(f'end_time [{end_time}] should be greater than start_time [{self.start_time}]!')

        self.end_time = end_time
        self.activity_time = self.end_time - self.start_time

        return self

    def has_finished(self) -> bool:
        return self.end_time is not None
