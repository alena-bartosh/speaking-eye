import unittest

from application_info import ApplicationInfo
from application_info_reader import ApplicationInfoReader


class ApplicationInfoReaderTestCase(unittest.TestCase):

    def test_when_incorrect_data(self):
        sub_tests_incorrect_data = {
            'None': None,
            'Empty list': [],
            'Wrong input type (dict)': {},
            'Wrong input type (number)': 42,
            'Wrong input type (str)': 'I am a string',
            'An application item w/o wm_name & tab': [{'App name': {}}],
        }
        reader = ApplicationInfoReader()

        for sub_test, incorrect_data in sub_tests_incorrect_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaises(ValueError):
                    reader.try_read(incorrect_data)

    def test_when_correct_data(self):
        reader = ApplicationInfoReader()
        correct_data = [
            {'App name 1': {'wm_name': 'wm1|wm2', 'tab': 't1'}},
            {'App name 2': {'wm_name': 'wm3', 'tab': 't2'}},
            {'App name 3': {'wm_name': 'wm4', 'tab': 't3|t4'}},
        ]

        result = reader.try_read(correct_data)
        expected = [
            ApplicationInfo(name='App name 1', wm_name='wm1|wm2', tab='t1'),
            ApplicationInfo(name='App name 2', wm_name='wm3', tab='t2'),
            ApplicationInfo(name='App name 3', wm_name='wm4', tab='t3|t4')
        ]

        self.assertListEqual(result, expected)

    def test_when_correct_data_without_wm_name(self):
        reader = ApplicationInfoReader()
        correct_data_without_wm_name = [{'App name': {'tab': 't1'}}]

        result = reader.try_read(correct_data_without_wm_name)
        expected = [ApplicationInfo(name='App name', wm_name='', tab='t1')]

        self.assertListEqual(result, expected)

    def test_when_correct_data_without_tab(self):
        reader = ApplicationInfoReader()
        correct_data_without_tab = [{'App name': {'wm_name': 'wm1'}}]

        result = reader.try_read(correct_data_without_tab)
        expected = [ApplicationInfo(name='App name', wm_name='wm1', tab='')]

        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
