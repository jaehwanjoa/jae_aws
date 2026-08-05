INTENT_MAPPING = {

    "uri_analysis": {
        "mcp": "athena",
        "query_type": "uri_analysis",
        "description": "특정 URI 분석"
    },

    "ip_analysis": {
        "mcp": "athena",
        "query_type": "ip_analysis",
        "description": "특정 Source IP 분석"
    },

    "host_analysis": {
        "mcp": "athena",
        "query_type": "host_analysis",
        "description": "특정 Host 분석"
    },

    "rule_analysis": {
        "mcp": "athena",
        "query_type": "rule_analysis",
        "description": "WAF Rule 분석",

        "supported_filters": [
            "rule_group",
            "rule_name",
            "rule_pattern",
            "action",
            "source_country",
            "host_domain",
            "uri",
            "start_time",
            "end_time"
        ]
    },

    "top_uri": {
        "mcp": "athena",
        "query_type": "top_uri",
        "description": "상위 URI 분석"
    },

    "top_ip": {
        "mcp": "athena",
        "query_type": "top_ip",
        "description": "상위 Source IP 분석"
    },

    "attack_trend": {
        "mcp": "athena",
        "query_type": "attack_trend",
        "description": "공격 추이 분석"
    },

    "generic_analysis": {
        "mcp": "athena",
        "query_type": "generic_analysis",
        "description": "일반 분석"
    }
}


def get_mapping(intent: str):

    mapping = INTENT_MAPPING.get(intent)

    if mapping is None:

        raise ValueError(
            f"Unsupported intent: {intent}"
        )

    return mapping
