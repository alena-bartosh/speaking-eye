from activity import Activity
from activity_converter import ActivityConverter


class ActivityHelper:
    """Extra methods for working with Activity objects"""

    @staticmethod
    def raise_if_not_finished(activity: Activity) -> None:
        if not activity.has_finished():
            raise ValueError(f'Activity [{ActivityConverter.to_string(activity)}] should be finished!')
