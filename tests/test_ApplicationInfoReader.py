import unittest

from application_info import ApplicationInfo
from application_info_reader import ApplicationInfoReader


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

    def test_when_all_special_application_info_used_with_others(self):
        reader = ApplicationInfoReader()
        sub_tests_data = {
            'all in the beginning': ['all', {'App name': {'wm_name': 'wm1'}}],
            'all in the middle': [{'App name 1': {'wm_name': 'wm1'}}, 'all', {'App name 2': {'wm_name': 'wm2'}}],
            'all in the end': [{'App name': {'wm_name': 'wm1'}}, 'all']
        }

        for sub_test, incorrect_data in sub_tests_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaisesRegex(ValueError,
                                            expected_regex=r'Special case \[all\] must be the only one in a list!'):
                    reader.try_read(incorrect_data)

    def test_when_none_special_application_info_used_with_others(self):
        reader = ApplicationInfoReader()
        sub_tests_data = {
            'none in the beginning': ['none', {'App name': {'wm_name': 'wm1'}}],
            'none in the middle': [{'App name 1': {'wm_name': 'wm1'}}, 'none', {'App name 2': {'wm_name': 'wm2'}}],
            'none in the end': [{'App name': {'wm_name': 'wm1'}}, 'none']
        }

        for sub_test, incorrect_data in sub_tests_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaisesRegex(ValueError,
                                            expected_regex=r'Special case \[none\] must be the only one in a list!'):
                    reader.try_read(incorrect_data)

    def test_when_only_special_application_info_used(self):
        reader = ApplicationInfoReader()
        sub_tests_data = {
            'only all': (['all'], [ApplicationInfo(name='all', wm_name='', tab='')]),
            'only none': (['none'], [ApplicationInfo(name='none', wm_name='', tab='')])
        }

        for sub_test, sub_test_data in sub_tests_data.items():
            with self.subTest(name=sub_test):
                data, expected = sub_test_data

                result = reader.try_read(data)

                self.assertListEqual(result, expected)

    def test_when_app_name_is_not_object(self):
        reader = ApplicationInfoReader()
        incorrect_data = ['I am not an object because I have not ":" in the .yaml']

        with self.assertRaisesRegex(ValueError,
                                    expected_regex=r"Only special cases \[\['all', 'none'\]\] can be here or "
                                                   r"list of apps with wm_name and tab!"):
            reader.try_read(incorrect_data)

    def test_when_special_application_info_not_lowercase(self):
        reader = ApplicationInfoReader()
        sub_tests_incorrect_data = {
            'all uppercase': ['ALL'],
            'none uppercase': ['NONE'],
            'all mixed case': ['aLl'],
            'none mixed case': ['nONe']
        }

        for sub_test, incorrect_data in sub_tests_incorrect_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaisesRegex(ValueError,
                                            expected_regex=r"Only special cases \[\['all', 'none'\]\] can be here or "
                                                           r"list of apps with wm_name and tab!"):
                    reader.try_read(incorrect_data)

    def test_when_special_application_info_is_object(self):
        reader = ApplicationInfoReader()
        sub_tests_incorrect_data = {
            'all': [{'all': {}}],
            'none': [{'none': {}}]
        }

        for sub_test, incorrect_data in sub_tests_incorrect_data.items():
            with self.subTest(name=sub_test):
                with self.assertRaisesRegex(ValueError,
                                            expected_regex=r"Special cases \[\['all', 'none'\]\] "
                                                           r"with \":\" are not supported!"):
                    reader.try_read(incorrect_data)
