import unittest

from speaking_eye.application_info import ApplicationInfo


class ApplicationInfoTestCase(unittest.TestCase):

    def test_when_application_infos_are_equal(self):
        name = 'name'
        wm_name = 'wm_name'
        tab = 'tab'
        is_distracting = True

        left = ApplicationInfo(name, wm_name, tab, is_distracting)
        right = ApplicationInfo(name, wm_name, tab, is_distracting)

        self.assertEqual(left, right)

    def test_when_application_infos_are_not_equal(self):
        name = 'name'
        wm_name = 'wm_name'
        tab = 'tab'
        is_distracting = True

        app_info = ApplicationInfo(name, wm_name, tab, is_distracting)

        another_name = 'another_name'
        another_wm_name = 'another_wm_name'
        another_tab = 'another_tab'
        another_is_distracting = False

        sub_tests_data = {
            'Different names': ApplicationInfo(another_name, wm_name, tab, is_distracting),
            'Different wm names': ApplicationInfo(name, another_wm_name, tab, is_distracting),
            'Different tabs': ApplicationInfo(name, wm_name, another_tab, is_distracting),
            'Different distracting states': ApplicationInfo(name, wm_name, tab, another_is_distracting),
            'Different types': 'I am not an ApplicationInfo',
        }

        for sub_test, another_app_info in sub_tests_data.items():
            with self.subTest(name=sub_test):
                self.assertNotEqual(app_info, another_app_info)
