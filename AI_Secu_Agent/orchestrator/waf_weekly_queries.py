class WAFWeeklyQueries:

    @classmethod
    def get_count_detail_query(
        cls,
        table_name,
        start_ts,
        end_ts
    ):
        return f"""
SELECT

    terminatingruleid,

    httprequest.clientip AS client_ip,

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name)='host'
            ),
            1
        ).value
    ) AS host_domain,

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name)='user-agent'
            ),
            1
        ).value
    ) AS user_agent

FROM {table_name}

WHERE action='COUNT'

AND terminatingruleid IS NOT NULL

AND terminatingruleid <> 'Default_Action'

AND timestamp BETWEEN
{start_ts}
AND {end_ts}
"""
