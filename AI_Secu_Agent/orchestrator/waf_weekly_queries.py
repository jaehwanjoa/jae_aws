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

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name) = 'host'
            ),
            1
        ).value
    )
        AS host_domain,

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name) = 'user-agent'
            ),
            1
        ).value
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
