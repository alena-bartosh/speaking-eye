from pathlib import Path
from random import randint

import i18n


class Localizator:
    """Wrapper to work with i18n internalization package"""

    # TODO: add language enum for typing
    def __init__(self, localization_dir: Path, language: str) -> None:
        if not localization_dir.is_dir():
            raise ValueError(f'Path [{localization_dir}] does not exist or it is not a dir!')

        i18n.load_path.append(localization_dir)

        i18n.set('locale', language)
        i18n.set('enable_memoization', True)  # cache loaded strings in memory
        i18n.set('filename_format', '{locale}.{format}')

    def get(self, key: str, **kwargs) -> str:
        return i18n.t(key, **kwargs)

    def get_random(self, key: str, max_n: int, **kwargs) -> str:
        variant = randint(1, max_n)
        key_with_variant = key + i18n.get('namespace_delimiter') + str(variant)

        return self.get(key_with_variant, **kwargs)
