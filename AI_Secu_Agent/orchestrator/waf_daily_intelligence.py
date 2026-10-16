from datetime import datetime
from datetime import timedelta


class WAFDailyIntelligence:

    @classmethod
    def run(
        cls,
        customer
    ):

        print(
            f"WAF_WEEKLY_START={customer}"
        )

        date_range = cls.get_weekly_range()

        print(date_range)

    @classmethod
    def get_weekly_range(
        cls
    ):

        today = datetime.now()

        current_end = today

        current_start = today - timedelta(days=7)

        previous_end = current_start

        previous_start = previous_end - timedelta(days=7)

        return {
            "current_start":
                current_start.strftime("%Y-%m-%d"),
            "current_end":
                current_end.strftime("%Y-%m-%d"),
            "previous_start":
                previous_start.strftime("%Y-%m-%d"),
            "previous_end":
                previous_end.strftime("%Y-%m-%d")
        }
