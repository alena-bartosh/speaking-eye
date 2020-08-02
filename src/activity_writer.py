from pathlib import Path
from typing import Optional, TextIO
from pyee import BaseEventEmitter

from activity import Activity
from activity_converter import ActivityConverter
from time_provider import TimeProvider


class ActivityWriter:
    FILE_MODE = 'a'
    NEW_DAY_EVENT = 'new-day-event'

    def __init__(self, time_provider: TimeProvider, output_dir: Path, file_mask: str) -> None:
        if not output_dir.is_dir():
            raise ValueError(f'Path [{output_dir}] does not exist or it is not a dir!')

        if '{date}' not in file_mask:
            raise ValueError(f'file_mask [{file_mask}] should contain [date] string argument!')

        self.__time_provider = time_provider
        self.__output_dir = output_dir
        self.__file_mask = file_mask
        self.__current_file: Optional[TextIO] = None
        self.__current_file_path: Optional[Path] = None
        self.event = BaseEventEmitter()

    def __get_file(self) -> Path:
        return self.__output_dir / self.__file_mask.format(date=self.__time_provider.today())

    def __open_file(self, file: Path) -> None:
        self.__current_file_path = file
        self.__current_file = open(str(file), self.FILE_MODE)

    def __write_and_flush(self, activity: Activity) -> None:
        if self.__current_file is None:
            raise Exception('current_file should be opened!')

        self.__current_file.write(ActivityConverter.to_string(activity))
        self.__current_file.flush()

    def write(self, activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished '
                             f'before writing into the file!')

        file = self.__get_file()

        if self.__current_file is None:
            self.__open_file(file)
            self.__write_and_flush(activity)
            return

        if self.__current_file_path == file:
            self.__write_and_flush(activity)
            return

        self.__current_file.close()

        # TODO: if app work time from 23:00 to 01:00
        #  then split between old and new file: [23:00; 00:00] U [00:00; 01:00]
        self.__open_file(file)
        self.__write_and_flush(activity)

        self.event.emit(ActivityWriter.NEW_DAY_EVENT)
