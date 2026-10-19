class WAFWeeklyQueries:

    @classmethod
    def get_weekly_summary_query(
        cls,
        table_name,
        previous_start,
        previous_end,
        current_start,
        current_end
    ):

        return f"""
SELECT

    CASE
    
        WHEN DATE(
            from_unixtime(
                timestamp / 1000
            )
        )
        BETWEEN DATE '{previous_start}'
            AND DATE '{previous_end}'
        THEN 'PREVIOUS'
    
        WHEN DATE(
            from_unixtime(
                timestamp / 1000
            )
        )
        BETWEEN DATE '{current_start}'
            AND DATE '{current_end}'
        THEN 'CURRENT'
    
    END AS period,

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
BETWEEN DATE '{previous_start}'
AND DATE '{current_end}'
"""
