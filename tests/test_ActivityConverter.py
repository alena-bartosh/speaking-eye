import unittest
from datetime import datetime, timedelta

from activity import Activity
from activity_converter import ActivityConverter


class ActivityConverterTestCase(unittest.TestCase):

    def test_convert_to_string(self):
        sub_tests_data = {
            'When is_work_time is [True]': (
                Activity('wm_class1',
                         'window_name1',
                         datetime(2020, 7, 12, 20, 30, 0),
                         is_work_time=True).set_end_time(datetime(2020, 7, 12, 21, 30, 0)),
                '2020-07-12 20:30:00\t2020-07-12 21:30:00\t1:00:00\twm_class1\twindow_name1\tTrue\n'
            ),
            'When is_work_time is [False]': (
                Activity('wm_class2',
                         'window_name2',
                         datetime(2020, 7, 13, 20, 30, 0),
                         is_work_time=False).set_end_time(datetime(2020, 7, 13, 21, 35, 0)),
                '2020-07-13 20:30:00\t2020-07-13 21:35:00\t1:05:00\twm_class2\twindow_name2\tFalse\n'
            )
        }

        for sub_test, (activity, expected) in sub_tests_data.items():
            with self.subTest(name=sub_test):
                self.assertEqual(expected, ActivityConverter.to_string(activity))

    def test_convert_from_string(self):
        with self.assertRaises(NotImplementedError):
            ActivityConverter.from_string('In progress ;)')


if __name__ == '__main__':
    unittest.main()
