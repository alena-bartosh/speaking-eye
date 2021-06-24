from enum import Enum


class Theme(Enum):
    """"Themes that are used for tray icon interface"""
    DARK = 'dark'
    LIGHT = 'light'

    # TODO: implement class SpeakingEyeEnum(Enum) which has parse()
    @staticmethod
    def parse(value: str, default: 'Theme') -> 'Theme':
        for theme in Theme:
            if value == theme.value:
                return theme

        return default
