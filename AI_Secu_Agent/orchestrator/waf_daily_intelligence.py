from datetime import datetime
from datetime import timedelta

from orchestrator.table_catalog import (
    TABLE_CATALOG
)

from mcp_tools.athena_client import (
    AthenaClient
)


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

        database = table_info[
            "database"
        ]

        table_name = table_info[
            "table_name"
        ]

        date_range = cls.get_weekly_range()

        current_start = date_range[
            "current_start"
        ]

        current_end = date_range[
            "current_end"
        ]

        previous_start = date_range[
            "previous_start"
        ]

        previous_end = date_range[
            "previous_end"
        ]

        print(
            f"DATABASE={database}"
        )

        print(
            f"TABLE={table_name}"
        )

        print(
            f"CURRENT={current_start} ~ {current_end}"
        )

        print(
            f"PREVIOUS={previous_start} ~ {previous_end}"
        )

        test_query = f"""
        SELECT
            count(*) AS total_count
        FROM {table_name}
        """

        print(
            "\n===== TEST QUERY ====="
        )

        print(
            test_query
        )

        result = AthenaClient.query(
            database=database,
            query=test_query
        )

        print(
            "\n===== RESULT ====="
        )

        print(
            result
        )

        return result

    @classmethod
    def get_weekly_range(
        cls
    ):

        today = datetime.now()

        this_monday = (
            today -
            timedelta(
                days=today.weekday()
            )
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
        "cjl_an2"
    )
