from typing import Any, Dict, List, Mapping, Sequence, Type, TypeVar, Union, cast

from pydash import get
from typeguard import check_type

# declare type variable
T = TypeVar('T')


class TypedValue:
    @staticmethod
    def check_type(name: str, value: Any, value_type: Type[T]) -> T:
        check_type(name, value, value_type)

        return cast(T, value)

    # TODO: Optional or Union as value_type does not work
    @staticmethod
    def get(obj: Union[List[Any], Dict[Any, Any], Sequence[Any], Mapping[Any, Any]],
            path: str, value_type: Type[T], default_value: T) -> T:
        """
        Get a value from an object by path if the value has requested type.
        Raise exception otherwise
        """
        result = get(obj, path)

        if result is None:
            name = f'default_value [{default_value}] for path [{path}]'

            # TODO: remove default value runtime checking when mypy will handle such cases correctly
            #       For example, TypedValue.get(dict_with_abc, 'a.b.c', int, '6') should produce mypy type error:
            #       '6' (T) is not int (Type[T])

            return TypedValue.check_type(name, default_value, value_type)

        name = f'value [{result}] from path [{path}]'

        return TypedValue.check_type(name, result, value_type)
