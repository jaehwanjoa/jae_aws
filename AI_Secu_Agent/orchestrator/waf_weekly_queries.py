class WAFWeeklyQueries:

    @classmethod
    def get_rule_summary_query(
        cls,
        table_name,
        start_ts,
        end_ts
    ):

        return f"""
SELECT

    terminatingruleid AS rule_id,

    count(*) AS hit_count,

    count_if(
        action = 'BLOCK'
    ) AS block_count,

    count_if(
        action = 'COUNT'
    ) AS count_count

FROM {table_name}

WHERE terminatingruleid IS NOT NULL

AND timestamp BETWEEN {start_ts}
AND {end_ts}

GROUP BY 1

ORDER BY block_count DESC

LIMIT 5
"""

    @classmethod
    def get_ip_summary_query(
        cls,
        table_name,
        start_ts,
        end_ts
    ):

        return f"""
SELECT

    httprequest.clientip AS source_ip,

    count(*) AS block_count

FROM {table_name}

WHERE action = 'BLOCK'

AND timestamp BETWEEN {start_ts}
AND {end_ts}

GROUP BY 1

ORDER BY block_count DESC

LIMIT 5
"""

    @classmethod
    def get_domain_summary_query(
        cls,
        table_name,
        start_ts,
        end_ts
    ):

        return f"""
SELECT

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name) = 'host'
            ),
            1
        ).value
    ) AS host_domain,

    count(*) AS block_count

FROM {table_name}

WHERE action = 'BLOCK'

AND timestamp BETWEEN {start_ts}
AND {end_ts}

AND try(
    element_at(
        filter(
            httprequest.headers,
            x -> lower(x.name) = 'host'
        ),
        1
    ).value
) IS NOT NULL

GROUP BY 1

ORDER BY block_count DESC

LIMIT 5
"""
