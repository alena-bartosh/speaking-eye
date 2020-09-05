from datetime import date
from pathlib import Path
from typing import Optional, TextIO
from pyee import BaseEventEmitter

from activity import Activity
from activity_converter import ActivityConverter
from activity_splitter import ActivitySplitter


class ActivityWriter:
    """
    Open file that contains date in its name and write activity at string format to this file.
    If the activity lasted for several days, then it will be written in several files
    """

    FILE_MODE = 'a'
    NEW_DAY_EVENT = 'new-day-event'

    def __init__(self, output_dir: Path, file_mask: str) -> None:
        if not output_dir.is_dir():
            raise ValueError(f'Path [{output_dir}] does not exist or it is not a dir!')

        if '{date}' not in file_mask:
            raise ValueError(f'file_mask [{file_mask}] should contain [date] string argument!')

        self.__output_dir = output_dir
        self.__file_mask = file_mask
        self.__current_file: Optional[TextIO] = None
        self.__current_file_path: Optional[Path] = None
        self.event = BaseEventEmitter()

    def __get_file(self, day: date) -> Path:
        return self.__output_dir / self.__file_mask.format(date=day)

    def __open_file(self, file: Path) -> None:
        self.__current_file_path = file
        self.__current_file = open(str(file), self.FILE_MODE)

    def __write_and_flush(self, activity: Activity) -> None:
        if self.__current_file is None:
            raise Exception('current_file should be opened!')

        self.__current_file.write(ActivityConverter.to_string(activity))
        self.__current_file.flush()

    def write(self, original_activity: Activity) -> None:
        if not original_activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(original_activity)}] should be finished '
                             f'before writing into the file!')

        activities_with_days = ActivitySplitter.split_by_day(original_activity)

        for (day, activity) in activities_with_days:
            file = self.__get_file(day)

            if self.__current_file_path == file:
                self.__write_and_flush(activity)
                continue

            if self.__current_file is not None:  # current day != day of opening
                self.__current_file.close()
                self.event.emit(ActivityWriter.NEW_DAY_EVENT)

            self.__open_file(file)
            self.__write_and_flush(activity)
