import unittest
from typing import Callable, List, Optional, Tuple, TypeVar

from speaking_eye.value import Value

# declare type variable
T = TypeVar('T')


class ValueTestCase(unittest.TestCase):

    def test_get_by_getter_or_default(self):
        # TODO: TestCaseType must be a generic type like a TestCaseType[T] = Tuple[..., T, T]
        TestCaseType = Tuple[
            Callable[[], Optional[str]],  # value_getter func
            str,  # default
            str,  # expected
        ]

        class Bar:
            def __init__(self, value: Optional[int]) -> None:
                self.value: Optional[int] = value

        class Foo:
            def __init__(self, bar: Optional[Bar]) -> None:
                self.bar: Optional[Bar] = bar

        bar1 = Bar(42)
        foo1 = Foo(bar1)

        foo2 = Foo(None)

        bar3 = Bar(None)
        foo3 = Foo(bar3)

        test_cases: List[TestCaseType] = [
            (lambda: None, 'default str', 'default str'),
            (lambda: None, 1, 1),
            (lambda: foo1.bar.value, 1, 42),
            (lambda: foo2.bar.value, 2, 2),
            (lambda: foo3.bar.value, 3, 3),
        ]

        for (value_getter, default, expected) in test_cases:
            self.assertEqual(expected, Value.get_by_getter_or_default(value_getter, default))

    def test_get_or_raise_correct_value(self):
        result = Value.get_or_raise(1, 'correct value')
        self.assertEqual(result, 1)

    def test_get_or_raise_none_value(self):
        with self.assertRaisesRegex(ValueError, expected_regex='Value \\[none_value\\] is None!'):
            Value.get_or_raise(None, 'none_value')
