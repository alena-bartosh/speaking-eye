from typing import Generic, TypeVar, Optional

# declare type variable
T = TypeVar('T')


class Value(Generic[T]):
    @staticmethod
    def get_or_raise(value: Optional[T], name: str) -> T:
        # NOTE: type T will be inherited based on the function call
        if value is None:
            raise ValueError(f'Value [{name}] is None!')

        return value
