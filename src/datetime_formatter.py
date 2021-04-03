from datetime import datetime, timedelta


class DatetimeFormatter:
    __TIME_SEPARATOR = ':'

    @staticmethod
    def __timedelta_to_datetime(value: timedelta) -> datetime:
        return datetime.min + value

    @staticmethod
    def __days_to_hours(value: int) -> int:
        return 24 * value

    @staticmethod
    def format_time_without_seconds(value: timedelta) -> str:
        time = DatetimeFormatter.__timedelta_to_datetime(value).time()
        hours = DatetimeFormatter.__days_to_hours(value.days) + time.hour

        return f'{hours}{DatetimeFormatter.__TIME_SEPARATOR}{time.minute:02}'
