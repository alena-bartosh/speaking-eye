from activity import Activity
from bool_parser import BoolParser
from datetime_formatter import DatetimeFormatter


class ActivityConverter:
    """Сonvert activity from/to string format"""

    EXPECTED_COLUMNS_NUMBER = 6

    @staticmethod
    def to_string(activity: Activity) -> str:
        return f'{activity.start_time}\t' \
               f'{activity.end_time}\t' \
               f'{activity.activity_time}\t' \
               f'{activity.wm_class}\t' \
               f'{activity.window_name}\t' \
               f'{activity.is_work_time}\n'

    @staticmethod
    def from_string(value: str) -> Activity:
        if value[-1] != '\n':
            raise ValueError(f'String [{value}] should be ended with a new line!')

        columns = value.split(sep='\t')

        if len(columns) != ActivityConverter.EXPECTED_COLUMNS_NUMBER:
            raise ValueError(f'Unexpected columns number: [{len(columns)}] '
                             f'!= {ActivityConverter.EXPECTED_COLUMNS_NUMBER} in string [{value}]!')

        try:
            start_time_str, end_time_str, activity_time, wm_class, window_name, is_work_time_str = columns
            start_time = DatetimeFormatter.parse_string_with_optional_milliseconds(start_time_str)
            end_time = DatetimeFormatter.parse_string_with_optional_milliseconds(end_time_str)
            is_work_time = BoolParser.parse(is_work_time_str.replace('\n', ''))
        except Exception as e:
            raise ValueError(f'Incorrect string [{value}]! {e}')

        return Activity(wm_class, window_name, start_time, is_work_time).set_end_time(end_time)
