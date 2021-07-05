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

    def test_when_initialize_stats(self) -> None:
        additional_activity = Activity('wm_name3', 'tab3', datetime(2021, 7, 4, 23, 35), True)
        additional_activity.set_end_time(datetime(2021, 7, 4, 23, 40))
        additional_activity.set_application_info(ApplicationInfo('title3', 'wm_name3', 'tab3', False))

        holder = ActivityStatHolder([additional_activity])
        empty_activity_stat = ActivityStat(timedelta(), timedelta())

        detailed_app_infos = [
            self.activities['ordinary_activity'].application_info,
            additional_activity.application_info
        ]
        holder.initialize_stats(detailed_app_infos)
        self.assertEqual(len(holder), 2)
        self.assertEqual(holder['title1'], empty_activity_stat)
        self.assertEqual(holder['title3'], ActivityStat(timedelta(minutes=5), timedelta()))

        youtube_app_info = ApplicationInfo('youtube', 'firefox', 'youtube', True)
        distracting_app_infos = [
            self.activities['distracting_activity'].application_info,
            youtube_app_info
        ]
        holder.initialize_stats(distracting_app_infos)
        self.assertEqual(len(holder), 4)
        self.assertEqual(holder['title2'], empty_activity_stat)
        self.assertEqual(holder['youtube'], empty_activity_stat)

    def test_when_get_correct_group_work_time(self) -> None:
        holder = ActivityStatHolder([activity for activity in self.activities.values()])

        correct_group_titles = ['title1', 'title2']
        self.assertEqual(holder.get_group_work_time(correct_group_titles), timedelta(hours=1, minutes=5))

    def test_when_get_incorrect_group_work_time(self) -> None:
        holder = ActivityStatHolder([activity for activity in self.activities.values()])

        incorrect_group_titles = ['I am bad title that is missing in holder!']
        with self.assertRaisesRegex(
                RuntimeError,
                expected_regex='ActivityStatHolder does not contain stat for '
                               '\\[ActivityStat.title=I am bad title that is missing in holder!\\]!'):
            holder.get_group_work_time(incorrect_group_titles)

    def test_when_update_stat(self) -> None:
        holder = ActivityStatHolder([self.activities['ordinary_activity']])
        self.assertEqual(holder['title1'], ActivityStat(timedelta(hours=1), timedelta()))

        next_ordinary_activity = Activity('wm_name1', 'tab1', datetime(2021, 7, 4, 22, 0), True)
        next_ordinary_activity.set_end_time(datetime(2021, 7, 4, 22, 20))
        next_ordinary_activity.set_application_info(ApplicationInfo('title1', 'wm_name1', 'tab1', False))

        holder.update_stat(next_ordinary_activity)
        self.assertEqual(holder['title1'], ActivityStat(timedelta(hours=1, minutes=20), timedelta()))
