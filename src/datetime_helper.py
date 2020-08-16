from datetime import date, timedelta, datetime
from typing import List, Tuple


DateRange = Tuple[
    datetime,  # start
    datetime,  # end
]


class DatetimeHelper:
    @staticmethod
    def get_dates_between(start: date, end: date) -> List[date]:
        if end < start:
            raise ValueError(f'End date [{end}] should be greater than start date [{start}]!')

        if start == end:
            return [start]

        delta = end - start

        return [start + timedelta(days=i) for i in range(delta.days + 1)]

    @staticmethod
    def get_date_range(date_: date) -> DateRange:
        start = datetime(date_.year, date_.month, date_.day)
        end = start + timedelta(days=1) - timedelta(microseconds=1)

        return start, end
