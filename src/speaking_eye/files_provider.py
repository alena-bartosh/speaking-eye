import glob
import os
from datetime import date, datetime
from pathlib import Path
from shutil import copy
from typing import cast, Optional, Union

import parse
from xdg import xdg_config_home, xdg_data_home

from .icon_state import IconState
from .theme import Theme
from .value import Value


class FilesProvider:
    """"
    Provide paths to localization / icon / data files.
    Help to search among files with raw data
    """
    __DATE_FORMAT_LABEL = 'date'
    __RAW_DATA_FILE_MASK = f'{{{__DATE_FORMAT_LABEL}}}_speaking_eye_raw_data.tsv'
    __FS_RAW_DATA_FILE_MASK = __RAW_DATA_FILE_MASK.format_map({__DATE_FORMAT_LABEL: '*'})

    def __init__(self, package_root_dir: Path, app_id: str) -> None:
        self.__package_root_dir = package_root_dir

        self.__i18n_dir = self.__package_root_dir / 'i18n'
        self.__icon_dir = self.__package_root_dir / 'icon'
        self.__initial_config_path = self.__package_root_dir / 'config' / 'config.yaml'

        self.__autostart_file_path = xdg_config_home() / 'autostart' / 'speaking-eye.desktop'
        data_home = xdg_data_home()
        self.__desktop_file_path = data_home / 'applications' / 'speaking-eye.desktop'

        app_data_dir = data_home / app_id
        self.__raw_data_dir = app_data_dir / 'data'
        self.__default_config_path = app_data_dir / 'config' / 'config.yaml'

        self.__raw_data_dir.mkdir(parents=True, exist_ok=True)

        self.__check_dirs()

        self.__config_path: Optional[Path] = None

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

    @property
    def autostart_file_path(self) -> Path:
        return self.__autostart_file_path

    @property
    def desktop_file_path(self) -> Path:
        return self.__desktop_file_path

    @property
    def config_path(self) -> Path:
        return Value.get_or_raise(self.__config_path, '__config_path')

    @config_path.setter
    def config_path(self, raw_value: Union[Path, str]) -> None:
        value = raw_value

        if isinstance(raw_value, str):
            value = Path(raw_value)

        self.__config_path = cast(Path, value)

        if self.__config_path.exists():
            return

        is_custom_config_path = self.default_config_path != self.__config_path

        if is_custom_config_path:
            raise ValueError(f'__config_path [{self.__config_path}] does not exist!')

        self.__config_path.parent.mkdir(parents=True, exist_ok=True)
        copy(self.__initial_config_path, self.__config_path)

    @property
    def default_config_path(self) -> Path:
        return self.__default_config_path

    @property
    def raw_data_dir(self) -> Path:
        return self.__raw_data_dir

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
