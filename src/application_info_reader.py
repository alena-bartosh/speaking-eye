from typing import List

from application_info import ApplicationInfo


class ApplicationInfoReader:

    def try_read(self, data: List) -> List[ApplicationInfo]:
        raise NotImplementedError()
