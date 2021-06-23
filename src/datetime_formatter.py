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

    @staticmethod
    def parse_string_with_optional_milliseconds(value: str) -> datetime:
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # NOTE: Datetime object such as datetime.now() that is saved as string
            #       when a new second just started, does not contain zero milliseconds after point
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
