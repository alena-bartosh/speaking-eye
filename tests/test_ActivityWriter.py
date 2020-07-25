import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from activity import Activity
from activity_writer import ActivityWriter
from time_provider import TimeProvider


class ActivityWriterTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.activity = Activity('wm_class1',
                                 'window_name1',
                                 datetime(2020, 7, 21, 20, 30, 0, 1),
                                 is_work_time=True).set_end_time(datetime(2020, 7, 21, 21, 30, 0, 2))

    @patch('builtins.open', new_callable=mock_open)
    @patch('time_provider.TimeProvider.today', return_value=date(2020, 7, 21))
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_when_record_first_activity(self, mock_is_dir_res, mock_today_res, mock_open_res):
        writer = ActivityWriter(TimeProvider(), Path('/output_dir/'), '{date}.tsv')
        writer.write(self.activity)

        mock_is_dir_res.assert_called_once()
        mock_today_res.assert_called_once()
        mock_open_res.assert_called_once_with('/output_dir/2020-07-21.tsv', 'a')
        mock_open_res().write.assert_called_once_with(
            '2020-07-21 20:30:00.000001\t2020-07-21 21:30:00.000002\t1:00:00.000001\twm_class1\twindow_name1\tTrue\n')
        mock_open_res().flush.assert_called_once()
