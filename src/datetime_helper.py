from datetime import date, timedelta
from typing import List


class DatetimeHelper:
    @staticmethod
    def get_dates_between(start: date, end: date) -> List[date]:
        if end < start:
            raise ValueError(f'End date [{end}] should be greater than start date [{start}]!')

        if start == end:
            return [start]

        delta = end - start

        return [start + timedelta(days=i) for i in range(delta.days + 1)]
