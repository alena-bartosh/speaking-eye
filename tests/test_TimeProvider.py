import unittest
from datetime import date

from time_provider import TimeProvider


class TimeProviderTestCase(unittest.TestCase):

    def test_today_is_really_today(self) -> None:
        self.assertEqual(date.today(), TimeProvider().today())
