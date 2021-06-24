from enum import Enum

from typing import Type, TypeVar

# declare type variable
DerivedEnumClass = TypeVar('DerivedEnumClass', bound=Enum)


# TODO: This class can be published into github as a pip package
#       because class is cool and it is a good idea for learning
class ExtendedEnum(Enum):
    """Used as a base class for enums with strict typing"""

    @classmethod
    def parse(cls: Type[DerivedEnumClass], value: str, default: DerivedEnumClass) -> DerivedEnumClass:
        for enum_item in cls:
            if value == enum_item.value:
                return enum_item

        return default
