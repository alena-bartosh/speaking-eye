import unittest
from datetime import datetime

from activity import Activity
from activity_builder import ActivityBuilder


class ActivityBuilderTestCase(unittest.TestCase):

    def test_when_build_with_start_time_with_end_time(self):
        start_time = datetime(2021, 7, 4, 20, 30, 0)
        end_time = datetime(2021, 7, 4, 21, 30, 0)
        self.assertGreater(end_time, start_time)

        origin_activity = Activity('wm_class', 'window_name', start_time, is_work_time=True)
        new_activity = ActivityBuilder(origin_activity).with_start_time(start_time).with_end_time(end_time).build()

        self.assertTrue(new_activity.has_finished())
        self.assertEqual(start_time, new_activity.start_time)
        self.assertEqual(end_time, new_activity.end_time)

    def test_when_build_failed(self):
        start_time = datetime(2021, 7, 4, 20, 30, 0)
        origin_activity = Activity('wm_class', 'window_name', start_time, is_work_time=True)

        with self.assertRaisesRegex(RuntimeError, expected_regex='start_time should be set!'):
            ActivityBuilder(origin_activity).build()

        with self.assertRaisesRegex(RuntimeError, expected_regex='end_time should be set!'):
            ActivityBuilder(origin_activity).with_start_time(start_time).build()
