import unittest
from datetime import datetime

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
