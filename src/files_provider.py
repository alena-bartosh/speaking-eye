from datetime import date
from pathlib import Path

from icon_state import IconState


class FilesProvider:
    """"
    Provide paths to localization / icon / dest files.
    Help to search among files with raw data
    """
    __RAW_DATA_FILE_MASK = '{date}_speaking_eye_raw_data.tsv'

    def __init__(self, app_root_dir: Path) -> None:
        self.__app_root_dir = app_root_dir

        self.__i18n_dir = self.__app_root_dir / 'i18n'
        self.__icon_dir = self.__app_root_dir / 'icon'
        self.__raw_data_dir = self.__app_root_dir / 'dest'

        self.__check_dirs()

    def __check_dirs(self) -> None:
        dir_paths = [
            self.__app_root_dir,
            self.__i18n_dir,
            self.__icon_dir,
            self.__raw_data_dir,
        ]

        for dir_path in dir_paths:
            if dir_path.is_dir():
                continue

            raise ValueError(f'Path [{dir_path}] does not exist or it is not a dir!')

    @property
    def i18n_dir(self) -> Path:
        return self.__i18n_dir

    # TODO: add enum for theme
    def get_icon_file_path(self, theme: str, icon_state: IconState) -> Path:
        return self.__icon_dir / theme / f'{icon_state.value}.png'

    def get_raw_data_file_path(self, file_date: date) -> Path:
        return self.__raw_data_dir / self.__RAW_DATA_FILE_MASK.format(date=file_date)
