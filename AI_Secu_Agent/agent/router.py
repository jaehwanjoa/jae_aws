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

    import re

    q = (question or "").lower()

    match = re.search(
        r'\b[a-z0-9_-]+\.(dll|exe|sys|jar|war|zip|rar|7z|ps1|bat|sh)\b',
        q,
        re.IGNORECASE
    )

    if match:
        return {
            "source": "cortex",
            "intent": "FILENAME_SEARCH",
            "filename": match.group(0)
        }

    simple_file = re.search(
        r'^([a-z0-9._-]+)\s*(알려줘|조회|검색)?$',
        q,
        re.IGNORECASE
    )

    if simple_file:
        return {
            "source": "cortex",
            "intent": "FILENAME_SEARCH",
            "filename": simple_file.group(1)
        }

    generic_filename = re.search(
        r'^([a-zA-Z0-9._-]{2,})\s*(알려줘|조회|검색)?$',
        q.strip(),
        re.IGNORECASE
    )

    if generic_filename:

        reserved = {
            "멀웨어",
            "악성코드",
            "malware",
            "취약점",
            "취약성",
            "vulnerability",
            "규정준수",
            "cspm",
            "cwp"
        }

        filename = generic_filename.group(1)

        if filename.lower() not in reserved:

            return {
                "source": "cortex",
                "intent": "FILENAME_SEARCH",
                "filename": filename
            }

    malware_file = re.search(
        r'^([a-zA-Z0-9._-]+)\s+멀웨어\s+알려줘$',
        q.strip(),
        re.IGNORECASE
    )

    if malware_file:

        return {
            "source": "cortex",
            "intent": "FILENAME_SEARCH",
            "filename": malware_file.group(1)
        }

    sha_match = re.search(
        r'\b[a-f0-9]{64}\b',
        q,
        re.IGNORECASE
    )

    if sha_match:
        return {
            "source": "cortex",
            "intent": "SHA256_SEARCH",
            "sha256": sha_match.group(0)
        }

    for keyword, route in INTENT_MAP.items():

        if keyword.lower() in q:
            return route

    return None
