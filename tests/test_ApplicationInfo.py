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
        raise NotImplementedError()


if __name__ == '__main__':
    unittest.main()
