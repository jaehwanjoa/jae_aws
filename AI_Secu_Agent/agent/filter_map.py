FILTER_MAP = {

    "ONS-Malware": {
        "filters": [
            {
                "field": "issue_domain",
                "operator": "in",
                "value": ["Security"]
            },
            {
                "field": "status.progress",
                "operator": "in",
                "value": ["New"]
            },
            {
                "field": "category",
                "operator": "in",
                "value": ["Malware"]
            }
        ]
    },

    "ONS_Vul_Monitoring": {
        "filters": [
            {
                "field": "severity",
                "operator": "in",
                "value": ["CRITICAL"]
            }
        ]
    },

    "ONS_CSPM_Monitoring": {
        "filters": [
            {
                "field": "issue_domain",
                "operator": "in",
                "value": ["Posture"]
            }
        ]
    }

}
