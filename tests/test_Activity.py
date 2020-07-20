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

    def test_when_activities_are_equal(self):
        wm_class = 'wm_class'
        window_name = 'window_name'
        start_time = datetime(2020, 7, 12, 20, 30, 0)
        is_work_time = True

        left = Activity(wm_class, window_name, start_time, is_work_time)
        right = Activity(wm_class, window_name, start_time, is_work_time)

        self.assertEqual(left, right)

        end_time = datetime(2020, 7, 12, 21, 30, 0)

        left.set_end_time(end_time)
        right.set_end_time(end_time)

        self.assertEqual(left, right)

    def test_when_activities_are_not_equal(self):
        wm_class = 'wm_class'
        window_name = 'window_name'
        start_time = datetime(2020, 7, 12, 20, 30, 0)
        end_time = datetime(2020, 7, 12, 21, 30, 0)
        is_work_time = True

        activity = Activity(wm_class, window_name, start_time, is_work_time).set_end_time(end_time)

        another_wm_class = 'another_wm_class'
        another_window_name = 'another_window_name'
        another_start_time = datetime(2020, 7, 12, 20, 50, 0)
        another_end_time = datetime(2020, 7, 12, 23, 30, 0)
        another_is_work_time = False

        sub_tests_data = {
            'Different wm classes':
                Activity(another_wm_class, window_name, start_time, is_work_time).set_end_time(end_time),
            'Different window names':
                Activity(wm_class, another_window_name, start_time, is_work_time).set_end_time(end_time),
            'Different start times':
                Activity(wm_class, window_name, another_start_time, is_work_time).set_end_time(end_time),
            'Different end times':
                Activity(wm_class, window_name, start_time, is_work_time).set_end_time(another_end_time),
            'Different "is_work_time" status':
                Activity(wm_class, window_name, start_time, another_is_work_time).set_end_time(end_time),
            'Different types':
                'I am not an Activity',
        }

        for sub_test, another_activity in sub_tests_data.items():
            with self.subTest(name=sub_test):
                self.assertNotEqual(activity, another_activity)
