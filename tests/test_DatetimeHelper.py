import unittest
from datetime import date

from datetime_helper import DatetimeHelper


class DatetimeHelperTestCase(unittest.TestCase):

    def test_when_correct_value_passed(self):
        for (start, end, expected) in [
            (date(2020, 10, 27), date(2020, 10, 27), [date(2020, 10, 27)]),
            (date(2020, 10, 27), date(2020, 10, 28), [date(2020, 10, 27), date(2020, 10, 28)]),
            (date(2020, 10, 30), date(2020, 11, 1), [date(2020, 10, 30), date(2020, 10, 31), date(2020, 11, 1)]),
        ]:
            self.assertEqual(expected, DatetimeHelper.get_dates_between(start, end))

    def test_when_incorrect_value_passed(self):
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='End date \\[2020-07-20\\] should be greater '
                                                   'than start date \\[2020-07-21\\]!'):
            start = date(2020, 7, 21)
            end_less_than_start = date(2020, 7, 20)
            DatetimeHelper.get_dates_between(start, end_less_than_start)
