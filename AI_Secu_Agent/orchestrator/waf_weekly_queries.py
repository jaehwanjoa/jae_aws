class WAFWeeklyQueries:

    @classmethod
    def get_weekly_summary_query(
        cls,
        table_name,
        start_date,
        end_date
    ):

        return f"""
SELECT

    httprequest.clientip
        AS source_ip,

    terminatingruleid
        AS rule_id,

    action,

    element_at(
        map_from_entries(
            transform(
                httprequest.headers,
                x -> (
                    lower(x.name),
                    x.value
                )
            )
        ),
        'host'
    )
        AS host_domain,

    element_at(
        map_from_entries(
            transform(
                httprequest.headers,
                x -> (
                    lower(x.name),
                    x.value
                )
            )
        ),
        'user-agent'
    )
        AS user_agent

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{start_date}'
AND DATE '{end_date}'
"""
