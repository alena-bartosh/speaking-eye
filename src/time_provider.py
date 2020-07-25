from datetime import date


class TimeProvider:

    def today(self) -> date:
        return date.today()
