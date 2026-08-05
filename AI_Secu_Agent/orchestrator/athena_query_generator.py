class AthenaQueryGenerator:

    @classmethod
    def build(
        cls,
        plan,
        mapping,
        table_name
    ):

        query_type = mapping["query_type"]
        filters = plan["filters"]

        if query_type == "uri_analysis":
            return cls.build_uri_analysis(
                filters,
                table_name
            )

        elif query_type == "ip_analysis":
            return cls.build_ip_analysis(
                filters,
                table_name
            )

        elif query_type == "host_analysis":
            return cls.build_host_analysis(
                filters,
                table_name
            )

        elif query_type == "rule_analysis":
            return cls.build_rule_analysis(
                filters,
                table_name
            )

        elif query_type == "top_uri":
            return cls.build_top_uri(
                filters,
                table_name
            )

        elif query_type == "top_ip":
            return cls.build_top_ip(
                filters,
                table_name
            )

        elif query_type == "attack_trend":
            return cls.build_attack_trend(
                filters,
                table_name
            )

        return cls.build_generic_analysis(
            filters,
            table_name
        )

    @classmethod
    def base_query(
        cls,
        table_name
    ):

        return f"""
WITH base AS (

    SELECT
        t.*,

        date_format(
            from_unixtime(
                t.timestamp / 1000,
                'Asia/Seoul'
            ),
            '%Y-%m-%d %H:%i:%s'
        ) AS kst_time,

        element_at(
            multimap_from_entries(
                transform(
                    t.httprequest.headers,
                    x -> (
                        lower(x.name),
                        x.value
                    )
                )
            ),
            'host'
        )[1] AS host_domain,

        element_at(
            multimap_from_entries(
                transform(
                    t.httprequest.headers,
                    x -> (
                        lower(x.name),
                        x.value
                    )
                )
            ),
            'user-agent'
        )[1] AS user_agent,

        json_format(
            CAST(
                t.httprequest.headers
                AS JSON
            )
        ) AS all_headers

    FROM {table_name} t

)
"""

    @classmethod
    def build_where_clause(
        cls,
        filters
    ):

        conditions = []

        conditions.append(
            f"""
kst_time BETWEEN
'{filters["start_time"]}'
AND
'{filters["end_time"]}'
"""
        )

        if filters.get("source_ip"):

            conditions.append(
                f"""
httprequest.clientip =
'{filters["source_ip"]}'
"""
            )

        if filters.get("source_country"):

            conditions.append(
                f"""
httprequest.country =
'{filters["source_country"]}'
"""
            )

        if filters.get("host_domain"):

            conditions.append(
                f"""
host_domain =
'{filters["host_domain"]}'
"""
            )

        if filters.get("uri"):

            conditions.append(
                f"""
httprequest.uri =
'{filters["uri"]}'
"""
            )

        if filters.get("query_string"):

            conditions.append(
                f"""
lower(httprequest.args)
LIKE lower(
'%{filters["query_string"]}%'
)
"""
            )

        if filters.get("action"):

            conditions.append(
                f"""
action =
'{filters["action"]}'
"""
            )

        if filters.get("rule_group"):

            conditions.append(
                f"""
lower(rulegrouplist)
LIKE lower(
'%{filters["rule_group"]}%'
)
"""
            )

        if filters.get("rule_pattern"):

            conditions.append(
                f"""
lower(cast(rulegrouplist as varchar))
LIKE lower(
'%{filters["rule_pattern"]}%'
)
"""
            )

        return (
            "WHERE\n"
            + "\nAND ".join(conditions)
        )

    @classmethod
    def build_uri_analysis(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT *

FROM base

{cls.build_where_clause(filters)}

ORDER BY kst_time DESC

LIMIT 100
"""

    @classmethod
    def build_ip_analysis(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT *

FROM base

{cls.build_where_clause(filters)}

ORDER BY kst_time DESC

LIMIT 100
"""

    @classmethod
    def build_host_analysis(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT *

FROM base

{cls.build_where_clause(filters)}

ORDER BY kst_time DESC

LIMIT 100
"""

    @classmethod
    def build_top_uri(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT

    httprequest.uri,
    count(*) AS hit_count

FROM base

{cls.build_where_clause(filters)}

GROUP BY 1

ORDER BY hit_count DESC

LIMIT 10
"""

    @classmethod
    def build_top_ip(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT

    httprequest.clientip,
    count(*) AS hit_count

FROM base

{cls.build_where_clause(filters)}

GROUP BY 1

ORDER BY hit_count DESC

LIMIT 10
"""

    @classmethod
    def build_attack_trend(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT

    date_trunc(
        'hour',
        from_unixtime(
            timestamp / 1000
        )
    ) AS attack_hour,

    count(*) AS hit_count

FROM base

{cls.build_where_clause(filters)}

GROUP BY 1

ORDER BY 1
"""

    @classmethod
    def build_rule_analysis(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT

    b.kst_time,

    b.action,

    concat(
        b.httprequest.clientip,
        ' (',
        b.httprequest.country,
        ')'
    ) AS client_ip,

    b.host_domain,
    b.httprequest.uri,
    b.httprequest.args,

    coalesce(
        nmr_item.ruleid,
        'N/A'
    ) AS matched_rule

FROM base b

LEFT JOIN UNNEST(
    b.rulegrouplist
) AS rg(rg_item)
ON TRUE

LEFT JOIN UNNEST(
    rg_item.nonterminatingmatchingrules
) AS nmr(nmr_item)
ON TRUE

{cls.build_where_clause(filters)}

ORDER BY b.kst_time DESC

LIMIT 100
"""

    @classmethod
    def build_generic_analysis(
        cls,
        filters,
        table_name
    ):

        return f"""
{cls.base_query(table_name)}

SELECT *

FROM base

{cls.build_where_clause(filters)}

LIMIT 100
"""
