from activity import Activity


class ActivityConverter:
    @staticmethod
    def to_string(activity: Activity) -> str:
        return f'{activity.start_time}\t' \
               f'{activity.end_time}\t' \
               f'{activity.activity_time}\t' \
               f'{activity.wm_class}\t' \
               f'{activity.window_name}\t' \
               f'{activity.is_work_time}\n'

    @staticmethod
    def from_string(value: str) -> Activity:
        raise NotImplementedError()
