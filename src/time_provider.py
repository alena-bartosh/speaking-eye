from datetime import date


class TimeProvider:
    """Can be used in unit tests for mocking"""

    def today(self) -> date:
        return date.today()
