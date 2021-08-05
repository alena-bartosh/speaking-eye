from datetime import timedelta
from pathlib import Path
from random import randint
from typing import Union, cast

import i18n

from language import Language


class Localizator:
    """Wrapper to work with i18n internalization package"""

    FormatValueType = Union[str, int, timedelta]

    def __init__(self, localization_dir: Path, language: Language) -> None:
        if not localization_dir.is_dir():
            raise ValueError(f'Path [{localization_dir}] does not exist or it is not a dir!')

        i18n.load_path.append(localization_dir)

        i18n.set('locale', language.value)
        i18n.set('enable_memoization', True)  # cache loaded strings in memory
        i18n.set('filename_format', '{locale}.{format}')

    def get(self, key: str, **kwargs: FormatValueType) -> str:
        return cast(str, i18n.t(key, **kwargs))

    def get_random(self, key: str, max_n: int, **kwargs: FormatValueType) -> str:
        variant = randint(1, max_n)
        key_with_variant = key + i18n.get('namespace_delimiter') + str(variant)

        return self.get(key_with_variant, **kwargs)
