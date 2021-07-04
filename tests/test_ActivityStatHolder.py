import unittest
from datetime import datetime, timedelta

from activity import Activity
from activity_stat import ActivityStat
from activity_stat_holder import ActivityStatHolder
from application_info import ApplicationInfo
from special_application_info_title import SpecialApplicationInfoTitle


class ActivityStatHolderTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        ordinary_activity = Activity('wm_name1', 'tab1', datetime(2021, 7, 4, 20, 30), True)
        ordinary_activity.set_end_time(datetime(2021, 7, 4, 21, 30))
        ordinary_activity.set_application_info(ApplicationInfo('title1', 'wm_name1', 'tab1', False))

        distracting_activity = Activity('wm_name2', 'tab2', datetime(2021, 7, 4, 21, 30), True)
        distracting_activity.set_end_time(datetime(2021, 7, 4, 21, 35))
        distracting_activity.set_application_info(ApplicationInfo('title2', 'wm_name2', 'tab2', True))

        not_working_activity = Activity('wm_name2', 'tab2', datetime(2021, 7, 4, 21, 35), False)
        not_working_activity.set_end_time(datetime(2021, 7, 4, 23, 35))

        cls.activities = {
            'ordinary_activity': ordinary_activity,
            'distracting_activity': distracting_activity,
            'not_working_activity': not_working_activity,
        }

    def test_when_create_holder(self) -> None:
        holder = ActivityStatHolder([activity for activity in self.activities.values()])
        self.assertEqual(holder.total_work_time, timedelta(hours=1, minutes=5))
        self.assertEqual(holder.total_off_time, timedelta(hours=2))

        self.assertEqual(holder['title1'], ActivityStat(timedelta(hours=1), timedelta()))
        self.assertEqual(holder['title2'], ActivityStat(timedelta(minutes=5), timedelta()))
        self.assertEqual(holder[SpecialApplicationInfoTitle.OTHERS.value],
                         ActivityStat(timedelta(), timedelta(hours=2)))
