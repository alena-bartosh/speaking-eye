import logging
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from activity import Activity
from activity_reader import ActivityReader
from application_info import ApplicationInfo
from application_info_matcher import ApplicationInfoMatcher


class ActivityReaderTestCase(unittest.TestCase):
    read_data = [
        '2021-07-04 20:30:00.000001\t2021-07-04 21:30:00.000002\t1:00:00.000001\twm_name1\ttab1\tTrue\n',
        '2021-07-04 21:30:00.000003\t2021-07-04 21:35:00.000004\t0:05:00.000001\twm_name2\ttab2\tFalse\n',
    ]

    def setUp(self) -> None:
        detailed_app_infos = [ApplicationInfo('title', 'wm_name2', 'tab2', False)]
        distracting_app_infos = []
        self.reader = ActivityReader(logger=logging.Logger('ActivityReaderTestCase'),
                                     matcher=ApplicationInfoMatcher(detailed_app_infos, distracting_app_infos))

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_when_read_successfully(self, mock_exists_res, mock_open_res) -> None:
        raw_data_file = Path('/root_dir/raw_data_file.tsv')

        # print(f'DEBUG: [python={sys.version}]')
        # print('DEBUG: START test_when_read_successfully')

        # NOTE: mock_open does not properly handle iterating over the open file with "for line in file",
        #       so need to set the return value like this
        # mock_open_res.return_value.__iter__.return_value = self.read_data
        #
        # print(f'DEBUG: [mock_open_res={mock_open_res}]')
        # print(f'DEBUG: [mock_open_res.return_value.__iter__.return_value='
        #       f'{mock_open_res.return_value.__iter__.return_value}]')
        # print(f'DEBUG: [mock_open_res.return_value='
        #       f'{mock_open_res.return_value}]')

        result_activities = self.reader.read(raw_data_file)

        print(f'DEBUG: [result_activities={result_activities}]')

        self.assertEqual(mock_exists_res.call_count, 1)
        mock_open_res.assert_called_once_with(str(raw_data_file))

        expected_activities = [
            Activity('wm_name1', 'tab1', datetime(2021, 7, 4, 20, 30, 0, 1), True)
            .set_end_time(datetime(2021, 7, 4, 21, 30, 0, 2)),

            Activity('wm_name2', 'tab2', datetime(2021, 7, 4, 21, 30, 0, 3), False)
            .set_end_time(datetime(2021, 7, 4, 21, 35, 0, 4))
            .set_application_info(self.reader.matcher.detailed_app_infos[0]),
        ]

        self.assertListEqual(result_activities, expected_activities)

    def test_when_raw_data_file_does_not_exist(self) -> None:
        raw_data_file = Path('/non_existent_output_dir/non_existent_file.tsv')
        result_activities = self.reader.read(raw_data_file)
        self.assertListEqual(result_activities, [])
