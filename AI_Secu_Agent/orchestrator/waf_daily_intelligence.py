from datetime import datetime
from datetime import timedelta

from orchestrator.table_catalog import (
    TABLE_CATALOG
)

from mcp_tools.athena_client import (
    AthenaClient
)

##추가할 WAF테이블은 too_mapping에서 참고
class WAFDailyIntelligence:

    @classmethod
    def run(
        cls
    ):

        customers = [
            "cjl_an2",
            "cjl_ue1"
        ]

        table_infos = [
            TABLE_CATALOG[customer]
            for customer in customers
        ]

        databases = list(
            set(
                [
                    table_info["database"]
                    for table_info in table_infos
                ]
            )
        )

        if len(databases) != 1:

            raise ValueError(
                f"MULTIPLE DATABASES FOUND: {databases}"
            )

        database = databases[0]

        table_names = [
            table_info["table_name"]
            for table_info in table_infos
        ]

        date_range = cls.get_weekly_range()

        current_start = (
            date_range["current_start"]
        )

        current_end = (
            date_range["current_end"]
        )

        previous_start = (
            date_range["previous_start"]
        )

        previous_end = (
            date_range["previous_end"]
        )

        print(
            f"DATABASE={database}"
        )

        print(
            f"TABLES={table_names}"
        )

        print(
            f"CURRENT={current_start} ~ "
            f"{current_end}"
        )

        print(
            f"PREVIOUS={previous_start} ~ "
            f"{previous_end}"
        )

        union_sql = cls.build_union_query(
            table_names
        )

        test_query = f"""
{union_sql}

SELECT
    count(*) AS total_count
FROM waf_logs
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
    def build_union_query(
        cls,
        table_names
    ):

        union_queries = []

        for table_name in table_names:

            union_queries.append(
                f'SELECT * FROM "{table_name}"'
            )

        union_sql = (
            "\nUNION ALL\n"
        ).join(
            union_queries
        )

        return f"""
WITH waf_logs AS (

{union_sql}

)
"""

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

    WAFDailyIntelligence.run()
