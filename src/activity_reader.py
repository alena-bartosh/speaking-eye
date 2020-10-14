import logging
from pathlib import Path
from typing import List

from activity import Activity
from activity_converter import ActivityConverter
from application_info_matcher import ApplicationInfoMatcher


class ActivityReader:
    """Read line by line activities from file with raw data"""

    def __init__(self, logger: logging.Logger, matcher: ApplicationInfoMatcher) -> None:
        self.logger = logger
        self.matcher = matcher

    def read(self, raw_data_file: Path) -> List[Activity]:
        activities = []

        if not raw_data_file.exists():
            self.logger.debug(f'File with raw data [{raw_data_file}] does not exist for this day')

            return activities

        with open(str(raw_data_file)) as file:
            for line in file:
                activity = ActivityConverter.from_string(line)
                self.matcher.set_if_matched(activity)

                activities.append(activity)

        return activities
