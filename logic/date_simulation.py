from datetime import date, timedelta


class DateSimulation:
    def __init__(self):
        self.today: date = date.today()

    def advance_date(self, days: int = 1) -> None:
        """
        Advances the current date by the specified numbers of days.
        """
        self.today += timedelta(days=days)