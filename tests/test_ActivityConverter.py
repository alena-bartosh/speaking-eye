import unittest
from datetime import datetime

from activity import Activity
from activity_converter import ActivityConverter


class ActivityConverterTestCase(unittest.TestCase):

    def test_convert_to_string(self):
        sub_tests_data = {
            'When is_work_time is [True]': (
                Activity('wm_class1',
                         'window_name1',
                         datetime(2020, 7, 12, 20, 30, 0, 1),
                         is_work_time=True).set_end_time(datetime(2020, 7, 12, 21, 30, 0, 2)),
                '2020-07-12 20:30:00.000001\t2020-07-12 21:30:00.000002\t'
                '1:00:00.000001\twm_class1\twindow_name1\tTrue\n'
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

    def test_convert_from_string_when_correct_activity_line(self):
        sub_tests_data = [(
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\tFalse\n',
            Activity('wm_class1',
                     'window_name1',
                     datetime(2020, 7, 18, 20, 0, 0, 1),
                     is_work_time=False).set_end_time(datetime(2020, 7, 18, 20, 30, 0, 1))
        )]

        for i, (line, expected) in enumerate(sub_tests_data, 1):
            with self.subTest(name=f'Subtest №{i}'):
                self.assertEqual(expected, ActivityConverter.from_string(line))

    def test_convert_from_string_when_incorrect_activity_line(self):
        sub_tests_data = [(
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\tFALSEE\n',
            'Incorrect string \\['
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\tFALSEE\n'
            '\\]! Unexpected value \\[FALSEE\\]'
        ), (
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\tFalse',
            'String \\['
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\tFalse'
            '\\] should be ended with a new line!'
        ), (
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\n',
            'Unexpected columns number: \\[5\\] != 6 in string \\['
            '2020-07-18 20:00:00.000001\t2020-07-18 20:30:00.000001\t0:30:00.000000\twm_class1\twindow_name1\n\\]!'
        )]

        for i, (line, expected_msg) in enumerate(sub_tests_data, 1):
            with self.subTest(name=f'Subtest №{i}'):
                with self.assertRaisesRegex(ValueError,
                                            expected_regex=expected_msg):
                    ActivityConverter.from_string(line)


if __name__ == '__main__':
    unittest.main()
