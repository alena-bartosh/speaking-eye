import glob
import os
from datetime import date, datetime
from pathlib import Path
from typing import cast

import parse

from .icon_state import IconState
from .theme import Theme


class FilesProvider:
    """"
    Provide paths to localization / icon / dest files.
    Help to search among files with raw data
    """
    __DATE_FORMAT_LABEL = 'date'
    __RAW_DATA_FILE_MASK = f'{{{__DATE_FORMAT_LABEL}}}_speaking_eye_raw_data.tsv'
    __FS_RAW_DATA_FILE_MASK = __RAW_DATA_FILE_MASK.format_map({__DATE_FORMAT_LABEL: '*'})

    def __init__(self, package_root_dir: Path) -> None:
        self.__package_root_dir = package_root_dir

        self.__i18n_dir = self.__package_root_dir / 'i18n'
        self.__icon_dir = self.__package_root_dir / 'icon'
        self.__raw_data_dir = self.__package_root_dir / 'dest'

        self.__check_dirs()

    def __check_dirs(self) -> None:
        dir_paths = [
            self.__package_root_dir,
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

    def get_icon_file_path(self, theme: Theme, icon_state: IconState) -> Path:
        return self.__icon_dir / cast(str, theme.value) / f'{icon_state.value}.png'

    def get_raw_data_file_path(self, file_date: date) -> Path:
        return self.__raw_data_dir / self.__RAW_DATA_FILE_MASK.format_map({self.__DATE_FORMAT_LABEL: file_date})

    def get_date_of_first_raw_data_file(self, default_date: date = date.today()) -> date:
        """Return min date from raw data file names or default_date if no files"""
        file_paths = glob.glob(str(self.__raw_data_dir / self.__FS_RAW_DATA_FILE_MASK))

        if len(file_paths) == 0:
            return default_date

        file_names = [os.path.basename(file_path) for file_path in file_paths]

        dates = []
        for file_name in file_names:
            date_str = parse.parse(self.__RAW_DATA_FILE_MASK, file_name)[self.__DATE_FORMAT_LABEL]
            file_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            dates.append(file_date)

        return min(dates)
