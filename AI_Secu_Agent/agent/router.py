INTENT_MAP = {

    # Cortex

    "취약점": {
        "source": "cortex",
        "intent": "ONS_Vul_Monitoring"
    },

    "취약성": {
        "source": "cortex",
        "intent": "ONS_Vul_Monitoring"
    },

    "vulnerability": {
        "source": "cortex",
        "intent": "ONS_Vul_Monitoring"
    },

    "규정준수": {
        "source": "cortex",
        "intent": "ONS_CSPM_Monitoring"
    },

    "cspm": {
        "source": "cortex",
        "intent": "ONS_CSPM_Monitoring"
    },

    "멀웨어": {
        "source": "cortex",
        "intent": "ONS-Malware"
    },

    "악성코드": {
        "source": "cortex",
        "intent": "ONS-Malware"
    },

    "malware": {
        "source": "cortex",
        "intent": "ONS-Malware"
    },

    "cwp": {
        "source": "cortex",
        "intent": "ONS_Cwp_Monitoring"
    },

    # Athena

    "top uri": {
        "source": "athena",
        "intent": "TOP_URI"
    },

    "uri": {
        "source": "athena",
        "intent": "TOP_URI"
    },

    "top ip": {
        "source": "athena",
        "intent": "TOP_IP"
    }
}


def select_route(question: str):

    q = question.lower()

    for keyword, route in INTENT_MAP.items():

        if keyword.lower() in q:
            return route

    return None
