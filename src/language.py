from enum import Enum


class Language(Enum):
    UKRAINIAN = 'ua'
    RUSSIAN = 'ru'
    ENGLISH = 'en'

    @staticmethod
    def parse(value: str, default: 'Language') -> 'Language':
        for language in Language:
            if value == language.value:
                return language

        return default
