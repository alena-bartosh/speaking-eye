from pathlib import Path
from typing import List
import logging

from activity import Activity
from activity_converter import ActivityConverter


class ActivityReader:
    """Read line by line activities from file with raw data"""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def read(self, raw_data_file: Path) -> List[Activity]:
        activities = []

        if not raw_data_file.exists():
            self.logger.debug(f'File with raw data [{raw_data_file}] does not exist for this day')

            return activities

        with open(str(raw_data_file)) as file:
            for line in file:
                activity = ActivityConverter.from_string(line)

                activities.append(activity)

        return activities
