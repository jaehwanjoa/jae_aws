from datetime import datetime
from datetime import timedelta

from orchestrator.table_catalog import TABLE_CATALOG


class WAFDailyIntelligence:

    @classmethod
    def run(
        cls,
        customer
    ):

        table_info = TABLE_CATALOG.get(
            customer
        )

        if not table_info:

            raise ValueError(
                f"UNKNOWN CUSTOMER={customer}"
            )

        print(
            f"DATABASE={table_info['database']}"
        )

        print(
            f"TABLE={table_info['table_name']}"
        )

        date_range = cls.get_weekly_range()

        print(date_range)

    @classmethod
    def get_weekly_range(
        cls
    ):

        today = datetime.now()

        this_monday = (
            today -
            timedelta(days=today.weekday())
        )

        current_start = (
            this_monday -
            timedelta(days=7)
        )

        current_end = (
            this_monday -
            timedelta(days=1)
        )

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
        "ons_cjl_am2"
    )
