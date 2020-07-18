import unittest

from bool_parser import BoolParser


class BoolParserTestCase(unittest.TestCase):

    def test_when_correct_value_passed(self):
        for (value, expected) in [
            ('False', False),
            ('True', True),
        ]:
            self.assertEqual(expected, BoolParser.parse(value))

    def test_when_incorrect_value_passed(self):
        for value in [
            False,
            True,
            0,
            1,
            'false',
            'true',
            'no',
            'yes',
            '0',
            '1',
        ]:
            with self.assertRaisesRegex(ValueError,
                                        expected_regex=fr'Unexpected value \[{value}\]'):
                BoolParser.parse(value)


if __name__ == '__main__':
    unittest.main()
