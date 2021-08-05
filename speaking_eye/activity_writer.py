from pathlib import Path
from typing import cast, Optional, TextIO

from pyee import BaseEventEmitter

from activity import Activity
from activity_converter import ActivityConverter
from activity_helper import ActivityHelper
from activity_splitter import ActivitySplitter
from files_provider import FilesProvider


class ActivityWriter:
    """
    Open file that contains date in its name and write activity at string format to this file.
    If the activity lasted for several days, then it will be written in several files
    """

    FILE_MODE = 'a'
    NEW_DAY_EVENT = 'new-day-event'

    def __init__(self, files_provider: FilesProvider) -> None:
        self.__files_provider = files_provider
        self.__current_file: Optional[TextIO] = None
        self.__current_file_path: Optional[Path] = None
        self.event = BaseEventEmitter()

    def __open_file(self, file: Path) -> None:
        self.__current_file_path = file
        # cast open() result to TextIO to fix mypy warnings
        self.__current_file = cast(TextIO, open(str(file), self.FILE_MODE))

    def __write_and_flush(self, activity: Activity) -> None:
        if self.__current_file is None:
            raise Exception('current_file should be opened!')

        self.__current_file.write(ActivityConverter.to_string(activity))
        self.__current_file.flush()

    def write(self, original_activity: Activity) -> None:
        ActivityHelper.raise_if_not_finished(original_activity)

        activities_with_days = ActivitySplitter.split_by_day(original_activity)

        for (day, activity) in activities_with_days:
            file = self.__files_provider.get_raw_data_file_path(day)

            if self.__current_file_path == file:
                self.__write_and_flush(activity)
                continue

            if self.__current_file is not None:  # current day != day of opening
                self.__current_file.close()
                self.event.emit(ActivityWriter.NEW_DAY_EVENT)

            self.__open_file(file)
            self.__write_and_flush(activity)
