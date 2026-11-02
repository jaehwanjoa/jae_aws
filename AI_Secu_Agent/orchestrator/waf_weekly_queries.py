import pandas as pd


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
                x -> lower(x.name) = 'host'
            ),
            1
        ).value
    ) AS host_domain,

    try(
        element_at(
            filter(
                httprequest.headers,
                x -> lower(x.name) = 'user-agent'
            ),
            1
        ).value
    ) AS user_agent

FROM {table_name}

WHERE action = 'COUNT'

AND terminatingruleid IS NOT NULL

AND terminatingruleid <> 'Default_Action'

AND timestamp BETWEEN
{start_ts}
AND {end_ts}
"""


class WAFWeeklyAnalyzer:

    @staticmethod
    def analyze(rows):

        df = pd.DataFrame(rows)

        if df.empty:
            return {
                "top_rule": [],
                "top_domain": [],
                "top_user_agent": [],
                "top_ip": [],
                "rule_domain": [],
                "rule_user_agent": []
            }

        df = df.fillna("UNKNOWN")

        # Top Rule
        top_rule = (
            df.groupby(
                "terminatingruleid",
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(10)
            .to_dict("records")
        )

        # Top Domain
        top_domain = (
            df.groupby(
                "host_domain",
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(10)
            .to_dict("records")
        )

        # Top User-Agent
        top_user_agent = (
            df.groupby(
                "user_agent",
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(10)
            .to_dict("records")
        )

        # Top IP
        top_ip = (
            df.groupby(
                "client_ip",
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(10)
            .to_dict("records")
        )

        # Rule + Domain
        rule_domain = (
            df.groupby(
                [
                    "terminatingruleid",
                    "host_domain"
                ],
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(20)
            .to_dict("records")
        )

        # Rule + UserAgent
        rule_user_agent = (
            df.groupby(
                [
                    "terminatingruleid",
                    "user_agent"
                ],
                as_index=False
            )
            .size()
            .rename(
                columns={"size": "count"}
            )
            .sort_values(
                "count",
                ascending=False
            )
            .head(20)
            .to_dict("records")
        )

        return {
            "top_rule": top_rule,
            "top_domain": top_domain,
            "top_user_agent": top_user_agent,
            "top_ip": top_ip,
            "rule_domain": rule_domain,
            "rule_user_agent": rule_user_agent
        }
