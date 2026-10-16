class WAFWeeklyQueries:

    @classmethod
    def get_new_ip_query(
        cls,
        table_name,
        current_start,
        current_end,
        previous_start,
        previous_end
    ):

        return f"""
WITH current_week AS (

    SELECT DISTINCT
        httprequest.clientip

    FROM {table_name}

    WHERE date(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{current_start}'
    AND DATE '{current_end}'
),

previous_week AS (

    SELECT DISTINCT
        httprequest.clientip

    FROM {table_name}

    WHERE date(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{previous_start}'
    AND DATE '{previous_end}'
),

new_ips AS (

    SELECT *
    FROM current_week

    EXCEPT

    SELECT *
    FROM previous_week
)

SELECT
    httprequest.clientip,
    count(*) AS hit_count,
    count_if(
        action = 'BLOCK'
    ) AS block_count,
    count_if(
        action = 'COUNT'
    ) AS count_count
FROM {table_name}
WHERE httprequest.clientip IN (
    SELECT clientip
    FROM new_ips
)
GROUP BY 1
ORDER BY hit_count DESC
LIMIT 10
"""

    @classmethod
    def get_new_rule_query(
        cls,
        table_name,
        current_start,
        current_end,
        previous_start,
        previous_end
    ):

        return f"""
SELECT
    terminatingruleid,
    count(*) AS hit_count,
    count_if(
        action = 'BLOCK'
    ) AS block_count,
    count_if(
        action = 'COUNT'
    ) AS count_count
FROM {table_name}
WHERE date(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{current_start}'
AND DATE '{current_end}'
GROUP BY 1
ORDER BY hit_count DESC
LIMIT 10
"""

    @classmethod
    def get_new_domain_query(
        cls,
        table_name,
        current_start,
        current_end,
        previous_start,
        previous_end
    ):

        return f"""
SELECT
    element_at(
        multimap_from_entries(
            transform(
                httprequest.headers,
                x -> (
                    lower(x.name),
                    x.value
                )
            )
        ),
        'host'
    )[1] AS host_domain,
    count(*) AS hit_count
FROM {table_name}
WHERE date(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{current_start}'
AND DATE '{current_end}'
GROUP BY 1
ORDER BY hit_count DESC
LIMIT 10
"""

    @classmethod
    def get_new_user_agent_query(
        cls,
        table_name,
        current_start,
        current_end,
        previous_start,
        previous_end
    ):

        return f"""
SELECT
    element_at(
        multimap_from_entries(
            transform(
                httprequest.headers,
                x -> (
                    lower(x.name),
                    x.value
                )
            )
        ),
        'user-agent'
    )[1] AS user_agent,
    count(*) AS request_count,
    count(
        DISTINCT httprequest.clientip
    ) AS ip_count
FROM {table_name}
WHERE date(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{current_start}'
AND DATE '{current_end}'
GROUP BY 1
ORDER BY request_count DESC
LIMIT 10
"""
