class WAFWeeklyQueries:

    @classmethod
    def get_ip_query(
        cls,
        table_name,
        start_date,
        end_date
    ):

        return f"""
SELECT

    httprequest.clientip
        AS source_ip,

    count(*) AS hit_count,

    count_if(
        action = 'BLOCK'
    ) AS block_count,

    count_if(
        action = 'COUNT'
    ) AS count_count,

    array_join(
        array_distinct(
            array_agg(
                try(
                    element_at(
                        filter(
                            httprequest.headers,
                            x -> lower(x.name) = 'host'
                        ),
                        1
                    ).value
                )
            )
        ),
        ','
    ) AS domains,

    array_join(
        array_distinct(
            array_agg(
                terminatingruleid
            )
        ),
        ','
    ) AS rules

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{start_date}'
AND DATE '{end_date}'

GROUP BY 1
"""

    @classmethod
    def get_rule_query(
        cls,
        table_name,
        start_date,
        end_date
    ):

        return f"""
SELECT

    terminatingruleid
        AS rule_id,

    count(*) AS hit_count,

    count_if(
        action = 'BLOCK'
    ) AS block_count,

    count_if(
        action = 'COUNT'
    ) AS count_count

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{start_date}'
AND DATE '{end_date}'

GROUP BY 1
"""

    @classmethod
    def get_domain_query(
        cls,
        table_name,
        start_date,
        end_date
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
    )
        AS host_domain,

    count(*) AS hit_count,

    max(
        terminatingruleid
    )
        AS top_rule

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{start_date}'
AND DATE '{end_date}'

GROUP BY 1
"""
        
    @classmethod
    def get_user_agent_query(
        cls,
        table_name,
        start_date,
        end_date
    ):

        return f"""
SELECT

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name) = 'user-agent'
            ),
            1
        ).value
    )
        AS user_agent,

    count(*) AS request_count,

    approx_distinct(
        httprequest.clientip
    ) AS ip_count,

    max(
        httprequest.clientip
    ) AS top_ip

FROM {table_name}

WHERE DATE(
    from_unixtime(
        timestamp / 1000
    )
)
BETWEEN DATE '{start_date}'
AND DATE '{end_date}'

GROUP BY 1
"""
