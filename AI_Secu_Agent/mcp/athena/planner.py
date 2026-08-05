import re

def parse_question(question: str):

    result = {
        "intent": None,
        "filters": {}
    }

    # URI 추출
    uri_match = re.search(
        r'(/\S+)',
        question
    )

    if uri_match:
        result["intent"] = "uri_analysis"
        result["filters"]["uri"] = uri_match.group(1)

    # IP 추출
    ip_match = re.search(
        r'(\d+\.\d+\.\d+\.\d+)',
        question
    )

    if ip_match:
        result["intent"] = "ip_analysis"
        result["filters"]["source_ip"] = ip_match.group(1)

    # 기간
    if "24시간" in question:
        result["filters"]["hours"] = 24

    elif "7일" in question:
        result["filters"]["hours"] = 24 * 7

    else:
        result["filters"]["hours"] = 24

    return result
