from typing import Generic, TypeVar, Optional, Callable

# declare type variable
T = TypeVar('T')


class Value(Generic[T]):

    @staticmethod
    # NOTE: type T will be inherited based on the function call
    def get_or_raise(value: Optional[T], name: str) -> T:
        """
        Return value if it is not None.
        Raise exception otherwise
        """
        if value is None:
            raise ValueError(f'Value [{name}] is None!')

        return value

    @staticmethod
    def get_by_getter_or_default(value_getter: Callable[[], Optional[T]], default: T) -> T:
        """
        Return value from value_getter if all attributes exist and set.
        Return default value otherwise
        """
        try:
            value = value_getter()

            return value if value is not None else default

        except (AttributeError, NameError):
            return default
