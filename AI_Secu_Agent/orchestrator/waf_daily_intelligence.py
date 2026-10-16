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

        print(
            f"CURRENT={date_range['current_start']} ~ "
            f"{date_range['current_end']}"
        )

        print(
            f"PREVIOUS={date_range['previous_start']} ~ "
            f"{date_range['previous_end']}"
        )

        return date_range

    @classmethod
    def get_weekly_range(
        cls
    ):

        today = datetime.now()

        # 이번 주 월요일
        this_monday = (
            today -
            timedelta(days=today.weekday())
        )

        # 분석 대상 주간 (지난주 월~일)
        current_start = (
            this_monday -
            timedelta(days=7)
        )

        current_end = (
            this_monday -
            timedelta(days=1)
        )

        # 비교 대상 주간 (그 이전 주 월~일)
        previous_start = (
            current_start -
            timedelta(days=7)
        )

        previous_end = (
            current_start -
            timedelta(days=1)
        )

        return {
            "current_start":
                current_start.strftime(
                    "%Y-%m-%d"
                ),

            "current_end":
                current_end.strftime(
                    "%Y-%m-%d"
                ),

            "previous_start":
                previous_start.strftime(
                    "%Y-%m-%d"
                ),

            "previous_end":
                previous_end.strftime(
                    "%Y-%m-%d"
                )
        }


if __name__ == "__main__":

    WAFDailyIntelligence.run(
        "CJ"
    )
