INTENT_MAPPING = {

    "uri_analysis": {
        "mcp": "athena",
        "template": "uri_analysis.sql",
        "description": "특정 URI 분석"
    },

    "ip_analysis": {
        "mcp": "athena",
        "template": "ip_analysis.sql",
        "description": "특정 Source IP 분석"
    },

    "host_analysis": {
        "mcp": "athena",
        "template": "host_analysis.sql",
        "description": "특정 Host 분석"
    },

    "rule_analysis": {
        "mcp": "athena",
        "template": "rule_analysis.sql",
        "description": "WAF Rule 분석",

        "supported_filters": [
            "rule_name",
            "rule_pattern",
            "action",
            "source_country",
            "start_time",
            "end_time"
        ]
    },

    "top_uri": {
        "mcp": "athena",
        "template": "top_uri.sql"
    },

    "top_ip": {
        "mcp": "athena",
        "template": "top_ip.sql"
    },

    "attack_trend": {
        "mcp": "athena",
        "template": "attack_trend.sql"
    },

    "generic_analysis": {
        "mcp": "athena",
        "template": "generic_analysis.sql"
    }
}


def get_mapping(intent):

    mapping = INTENT_MAPPING.get(intent)

    if not mapping:
        raise ValueError(
            f"Unsupported intent: {intent}"
        )

    return mapping
