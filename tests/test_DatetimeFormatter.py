import unittest
from datetime import datetime, timedelta

from datetime_formatter import DatetimeFormatter


class DatetimeFormatterTestCase(unittest.TestCase):

    def test_when_format_time_without_seconds(self) -> None:
        for (value, expected) in [
            (timedelta(days=3, hours=2, minutes=1, seconds=10), '74:01'),
            (timedelta(hours=23, minutes=59, seconds=59), '23:59'),
            (timedelta(), '0:00'),
        ]:
            self.assertEqual(DatetimeFormatter.format_time_without_seconds(value), expected)

    def test_when_parse_string_with_optional_milliseconds(self) -> None:
        for (value, expected) in [
            ('2021-07-04 20:20:20.000001', datetime(2021, 7, 4, 20, 20, 20, 1)),
            ('2021-07-04 20:20:20', datetime(2021, 7, 4, 20, 20, 20)),
        ]:
            self.assertEqual(DatetimeFormatter.parse_string_with_optional_milliseconds(value), expected)
