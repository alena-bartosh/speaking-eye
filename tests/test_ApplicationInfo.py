import unittest

from application_info import ApplicationInfo


class ApplicationInfoTestCase(unittest.TestCase):

    def test_when_application_infos_are_equal(self):
        name = 'name'
        wm_name = 'wm_name'
        tab = 'tab'

        left = ApplicationInfo(name, wm_name, tab)
        right = ApplicationInfo(name, wm_name, tab)

        self.assertEqual(left, right)

    def test_when_application_infos_are_not_equal(self):
        name = 'name'
        wm_name = 'wm_name'
        tab = 'tab'

        app_info = ApplicationInfo(name, wm_name, tab)

        another_name = 'another_name'
        another_wm_name = 'another_wm_name'
        another_tab = 'another_tab'

        sub_tests_data = {
            'Different names': ApplicationInfo(another_name, wm_name, tab),
            'Different wm names': ApplicationInfo(name, another_wm_name, tab),
            'Different tabs': ApplicationInfo(name, wm_name, another_tab),
        }

        for sub_test, another_app_info in sub_tests_data.items():
            with self.subTest(name=sub_test):
                self.assertNotEqual(app_info, another_app_info)
