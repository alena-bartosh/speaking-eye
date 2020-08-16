import unittest
from datetime import date, datetime

from activity import Activity
from activity_splitter import ActivitySplitter


class ActivitySplitterTestCase(unittest.TestCase):

    def test_split_by_day(self) -> None:
        one_day_activity = Activity('wm_class1',
                                    'window_name1',
                                    datetime(2020, 7, 21, 12, 5),
                                    is_work_time=True).set_end_time(datetime(2020, 7, 21, 21, 30))
        three_days_activity = Activity('wm_class2',
                                       'window_name2',
                                       datetime(2020, 7, 31, 12, 5),
                                       is_work_time=True).set_end_time(datetime(2020, 8, 2, 11, 30))
        expected_for_three_days_activity = [
            (date(2020, 7, 31), Activity('wm_class2',
                                         'window_name2',
                                         datetime(2020, 7, 31, 12, 5),
                                         is_work_time=True).set_end_time(datetime(2020, 7, 31, 23, 59, 59, 999_999))),
            (date(2020, 8, 1), Activity('wm_class2',
                                        'window_name2',
                                        datetime(2020, 8, 1),
                                        is_work_time=True).set_end_time(datetime(2020, 8, 1, 23, 59, 59, 999_999))),
            (date(2020, 8, 2), Activity('wm_class2',
                                        'window_name2',
                                        datetime(2020, 8, 2),
                                        is_work_time=True).set_end_time(datetime(2020, 8, 2, 11, 30))),
        ]

        for (activity, expected) in [
            (one_day_activity, [(date(2020, 7, 21), one_day_activity)]),
            (three_days_activity, expected_for_three_days_activity),
        ]:
            self.assertEqual(expected, ActivitySplitter.split_by_day(activity))
