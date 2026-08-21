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
            },
            {
                "field": "detection.method",
                "operator": "in",
                "value": [
                    "COMPUTE_POLICY",
                    "XDR_AGENT"
                ]
            },
            {
                "field": "status.progress",
                "operator": "in",
                "value": ["New"]
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
    },

    "ONS_CSPM_Monitoring": {
        "filters": [
            {
                "field": "issue_domain",
                "operator": "in",
                "value": ["Posture"]
            },
            {
                "field": "detection.method",
                "operator": "in",
                "value": ["CSPM_SCANNER"]
            },
            {
                "field": "severity",
                "operator": "in",
                "value": [
                    "HIGH",
                    "CRITICAL"
                ]
            },
            {
                "field": "status.progress",
                "operator": "in",
                "value": ["New"]
            }
        ]
    }

}
