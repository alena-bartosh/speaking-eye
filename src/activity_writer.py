from pathlib import Path
from typing import Optional, TextIO

from activity import Activity
from activity_converter import ActivityConverter
from time_provider import TimeProvider


class ActivityWriter:
    FILE_MODE = 'a'

    def __init__(self, time_provider: TimeProvider, output_dir: Path, file_mask: str) -> None:
        if not output_dir.is_dir():
            raise ValueError(f'Path [{output_dir}] does not exist or it is not a dir!')

        self.__time_provider = time_provider
        self.__output_dir = output_dir
        # TODO: check mask for date argument
        self.__file_mask = file_mask
        self.__current_file: Optional[TextIO] = None

    def __get_file(self) -> Path:
        return self.__output_dir / self.__file_mask.format(date=self.__time_provider.today())

    def __write_and_flush(self, activity: Activity) -> None:
        if self.__current_file is None:
            raise Exception('current_file should be opened!')

        self.__current_file.write(ActivityConverter.to_string(activity))
        self.__current_file.flush()

    def write(self, activity: Activity) -> None:
        # TODO: activity should be finished
        file = self.__get_file()

        if self.__current_file is None:
            self.__current_file = open(str(file), self.FILE_MODE)
            self.__write_and_flush(activity)
            return

        if self.__current_file == str(file):
            self.__write_and_flush(activity)
            return

        self.__current_file.close()

        # TODO: if app work time from 23:00 to 01:00
        #  then split between old and new file: [23:00; 00:00] U [00:00; 01:00]
        self.__current_file = open(str(file), self.FILE_MODE)
        self.__write_and_flush(activity)

        # TODO: emit on_new_file_open
