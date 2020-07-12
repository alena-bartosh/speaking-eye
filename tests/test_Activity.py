import unittest
from datetime import datetime, timedelta

from activity import Activity


class ActivityTestCase(unittest.TestCase):

    def test_when_end_time_is_greater_than_start_time(self):
        start_time = datetime(2020, 7, 12, 20, 30, 0)
        end_time = datetime(2020, 7, 12, 21, 30, 0)
        expected_activity_time = timedelta(hours=1)

        self.assertGreater(end_time, start_time)

        activity = Activity('wm_class', 'window_name', start_time, is_work_time=True)

        activity.set_end_time(end_time)

        self.assertTrue(activity.has_finished())
        self.assertEqual(end_time, activity.end_time)
        self.assertEqual(expected_activity_time, activity.activity_time)

    def test_when_end_time_is_not_greater_than_start_time(self):
        start_time = datetime(2020, 7, 12, 20, 30, 0)
        end_time = datetime(2020, 7, 12, 19, 30, 0)

        self.assertLess(end_time, start_time)

        activity = Activity('wm_class', 'window_name', start_time, is_work_time=True)

        with self.assertRaisesRegex(ValueError,
                                    expected_regex=r'end_time \[2020-07-12 19:30:00\] should be greater '
                                                   r'than start_time \[2020-07-12 20:30:00\]!'):
            activity.set_end_time(end_time)

        self.assertFalse(activity.has_finished())
        self.assertIsNone(activity.end_time)
        self.assertIsNone(activity.activity_time)


if __name__ == '__main__':
    unittest.main()
