import unittest
from datetime import datetime, timedelta

from activity import Activity
from activity_stat import ActivityStat


class ActivityStatTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.activity = Activity('wm_class1',
                                'window_name1',
                                datetime(2020, 7, 21, 20, 30, 0, 1),
                                is_work_time=True).set_end_time(datetime(2020, 7, 21, 21, 30, 0, 2))

    def test_when_activity_has_not_finished(self) -> None:
        not_finished_activity = Activity('wm_class1',
                                         'window_name1',
                                         datetime(2020, 7, 21, 20, 30, 0),
                                         is_work_time=True)

        with self.assertRaisesRegex(
                ValueError,
                expected_regex='Activity \\[2020-07-21 20:30:00\tNone\tNone\twm_class1\twindow_name1\tTrue\n\\] '
                               'should be finished before creating ActivityStat!'):
            ActivityStat(not_finished_activity)

        with self.assertRaisesRegex(
                ValueError,
                expected_regex='Activity \\[2020-07-21 20:30:00\tNone\tNone\twm_class1\twindow_name1\tTrue\n\\] '
                               'should be finished before updating ActivityStat!'):
            ActivityStat(self.activity).update(not_finished_activity)

    def test_when_update_time(self) -> None:
        not_working_activity = Activity('wm_class1',
                                        'window_name1',
                                        datetime(2020, 7, 21, 21, 30, 0, 3),
                                        is_work_time=False).set_end_time(datetime(2020, 7, 21, 22, 30, 0, 3))
        working_activity = Activity('wm_class1',
                                    'window_name1',
                                    datetime(2020, 7, 21, 22, 30, 0, 4),
                                    is_work_time=True).set_end_time(datetime(2020, 7, 21, 22, 35, 0, 5))

        sub_tests_data = {
            'Update off time stat when it was empty':
                (self.activity, not_working_activity, timedelta(0, 3600, 1), timedelta(0, 3600)),
            'Update work time stat when it was empty':
                (not_working_activity, working_activity, timedelta(0, 300, 1), timedelta(0, 3600)),
            'Update work time stat when it was not empty':
                (self.activity, working_activity, timedelta(0, 3900, 2), timedelta(0)),
        }

        for sub_test, (activity, same_activity_with_diff_time, work_time, off_time) in sub_tests_data.items():
            with self.subTest(name=sub_test):
                activity_stat = ActivityStat(activity)
                activity_stat.update(same_activity_with_diff_time)

                self.assertEqual(activity_stat.work_time, work_time)
                self.assertEqual(activity_stat.off_time, off_time)
