import unittest

from speaking_eye.application_info import ApplicationInfo
from speaking_eye.application_info_reader import ApplicationInfoReader


class ApplicationInfoReaderTestCase(unittest.TestCase):

    def test_when_incorrect_data(self):
        sub_tests_incorrect_data = {
            'None': (None, r"Incorrect data type \[<class 'NoneType'>\]!"),
            'Empty list': ([], r'Empty data!'),
            'Wrong input type (dict)': ({}, r"Incorrect data type \[<class 'dict'>\]!"),
            'Wrong input type (number)': (42, r"Incorrect data type \[<class 'int'>\]!"),
            'Wrong input type (str)': ('I am a string', r"Incorrect data type \[<class 'str'>\]!"),
            'An application item w/o wm_name & tab':
                ([{'App name': {}}], r'Application \[App name\] has empty wm_name and tab!'),
        }
        reader = ApplicationInfoReader()

        for sub_test, (incorrect_data, expected_error_msg) in sub_tests_incorrect_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaisesRegex(ValueError, expected_regex=expected_error_msg):
                    reader.try_read(incorrect_data, False)

    def test_when_correct_data(self):
        reader = ApplicationInfoReader()
        correct_data = [
            {'App name 1': {'wm_name': 'wm1|wm2', 'tab': 't1'}},
            {'App name 2': {'wm_name': 'wm3', 'tab': 't2'}},
            {'App name 3': {'wm_name': 'wm4', 'tab': 't3|t4'}},
        ]

        result = reader.try_read(correct_data, False)
        expected = [
            ApplicationInfo(title='App name 1', wm_name_re='wm1|wm2', tab_re='t1', is_distracting=False),
            ApplicationInfo(title='App name 2', wm_name_re='wm3', tab_re='t2', is_distracting=False),
            ApplicationInfo(title='App name 3', wm_name_re='wm4', tab_re='t3|t4', is_distracting=False)
        ]

        self.assertListEqual(result, expected)

    def test_when_correct_data_without_wm_name(self):
        reader = ApplicationInfoReader()
        correct_data_without_wm_name = [{'App name': {'tab': 't1'}}]

        result = reader.try_read(correct_data_without_wm_name, False)
        expected = [ApplicationInfo(title='App name', wm_name_re='', tab_re='t1', is_distracting=False)]

        self.assertListEqual(result, expected)

    def test_when_correct_data_without_tab(self):
        reader = ApplicationInfoReader()
        correct_data_without_tab = [{'App name': {'wm_name': 'wm1'}}]

        result = reader.try_read(correct_data_without_tab, False)
        expected = [ApplicationInfo(title='App name', wm_name_re='wm1', tab_re='', is_distracting=False)]

        self.assertListEqual(result, expected)

    def test_when_app_name_is_not_object(self):
        reader = ApplicationInfoReader()
        incorrect_data = ['I am not an object because I have not ":" in the .yaml']

        with self.assertRaisesRegex(ValueError,
                                    expected_regex=r"Application info \[I am not an object because "
                                                   r"I have not \":\" in the .yaml\] in detailed\/distracting list "
                                                   r"should be an object!"):
            reader.try_read(incorrect_data, False)
