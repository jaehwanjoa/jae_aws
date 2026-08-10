FILTER_MAP = {

    "ONS-Malware": {
        "filters": [
            {
                "field": "issue_domain",
                "operator": "in",
                "value": ["Security"]
            },
            {
                "field": "category",
                "operator": "in",
                "value": ["MALWARE"]
            }
        ]
    },

    "ONS_Cwp_Monitoring": {
        "filters": [
            {
                "field": "detection.method",
                "operator": "in",
                "value": ["XDR_AGENT"]
            }
        ]
    },

    "ONS_Vul_Monitoring": {
        "filters": [
            {
                "field": "severity",
                "operator": "in",
                "value": ["CRITICAL"]
            },
            {
                "field": "category",
                "operator": "in",
                "value": ["VULNERABILITY"]
            },
            {
                "field": "status.progress",
                "operator": "in",
                "value": ["New"]
            }
        ]
    }
}
