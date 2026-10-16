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

    SELECT
        httprequest.clientip

    FROM {table_name}

    WHERE DATE(
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

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{previous_start}'
    AND DATE '{previous_end}'

),

new_ips AS (

    SELECT DISTINCT
        clientip

    FROM current_week

    EXCEPT

    SELECT DISTINCT
        clientip

    FROM previous_week

)

SELECT

    httprequest.clientip
        AS source_ip,

    count(*)
        AS hit_count,

    max(
        terminatingruleid
    )
        AS matched_rule,

    count_if(
        action = 'BLOCK'
    )
        AS block_count,

    count_if(
        action = 'COUNT'
    )
        AS count_count

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{current_start}'
AND DATE '{current_end}'

AND httprequest.clientip IN (

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
WITH current_rules AS (

    SELECT DISTINCT
        terminatingruleid

    FROM {table_name}

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{current_start}'
    AND DATE '{current_end}'

),

previous_rules AS (

    SELECT DISTINCT
        terminatingruleid

    FROM {table_name}

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{previous_start}'
    AND DATE '{previous_end}'

),

new_rules AS (

    SELECT *
    FROM current_rules

    EXCEPT

    SELECT *
    FROM previous_rules

)

SELECT

    terminatingruleid,

    count(*)
        AS hit_count,

    count_if(
        action = 'BLOCK'
    )
        AS block_count,

    count_if(
        action = 'COUNT'
    )
        AS count_count

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{current_start}'
AND DATE '{current_end}'

AND terminatingruleid IN (

    SELECT terminatingruleid
    FROM new_rules

)

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
WITH base AS (

    SELECT

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

        *

    FROM {table_name}

),

current_domains AS (

    SELECT DISTINCT
        host_domain

    FROM base

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{current_start}'
    AND DATE '{current_end}'

),

previous_domains AS (

    SELECT DISTINCT
        host_domain

    FROM base

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{previous_start}'
    AND DATE '{previous_end}'

),

new_domains AS (

    SELECT *
    FROM current_domains

    EXCEPT

    SELECT *
    FROM previous_domains

)

SELECT

    host_domain,

    count(*)
        AS hit_count,

    max(
        terminatingruleid
    )
        AS top_rule

FROM base

WHERE host_domain IN (

    SELECT host_domain
    FROM new_domains

)

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
WITH base AS (

    SELECT

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
        AS user_agent,

        *

    FROM {table_name}

),

current_ua AS (

    SELECT DISTINCT
        user_agent

    FROM base

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{current_start}'
    AND DATE '{current_end}'

),

previous_ua AS (

    SELECT DISTINCT
        user_agent

    FROM base

    WHERE DATE(
        from_unixtime(
            timestamp / 1000
        )
    )
    BETWEEN DATE '{previous_start}'
    AND DATE '{previous_end}'

),

new_ua AS (

    SELECT *
    FROM current_ua

    EXCEPT

    SELECT *
    FROM previous_ua

)

SELECT

    user_agent,

    count(*)
        AS request_count,

    count(
        DISTINCT httprequest.clientip
    )
        AS ip_count

FROM base

WHERE user_agent IN (

    SELECT user_agent
    FROM new_ua

)

GROUP BY 1

ORDER BY request_count DESC

LIMIT 10
"""
