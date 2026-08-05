import re

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


class Planner:

    COUNTRY_MAP = {
        # Asia
        "한국": "KR",
        "대한민국": "KR",
        "중국": "CN",
        "일본": "JP",
        "대만": "TW",
        "홍콩": "HK",
        "싱가포르": "SG",
        "인도": "IN",
        "베트남": "VN",
        "태국": "TH",
        "말레이시아": "MY",
        "인도네시아": "ID",

        # North America
        "미국": "US",
        "캐나다": "CA",
        "멕시코": "MX",

        # Europe
        "영국": "GB",
        "독일": "DE",
        "프랑스": "FR",
        "이탈리아": "IT",
        "스페인": "ES",
        "네덜란드": "NL",

        # Others
        "러시아": "RU",
        "브라질": "BR",
        "호주": "AU"
    }

    RULE_KEYWORDS = {
        "sql injection": "SQL Injection",
        "sqli": "SQL Injection",
        "xss": "XSS",
        "cross site scripting": "XSS",
        "path traversal": "Path Traversal",
        "directory traversal": "Path Traversal",
        "command injection": "Command Injection",
        "bad bot": "Bad Bot",
        "scanner": "Scanner"
    }

    @classmethod
    def parse(cls, question: str):

        filters = {}

        filters.update(
            cls.extract_time(question)
        )

        filters.update(
            cls.extract_entities(question)
        )

        return {
            "intent": cls.detect_intent(
                question,
                filters
            ),
            "filters": filters
        }

    @classmethod
    def detect_intent(
        cls,
        question,
        filters
    ):

        lower_question = question.lower()

        if "top" in lower_question and "uri" in lower_question:
            return "top_uri"

        if "top" in lower_question and "ip" in lower_question:
            return "top_ip"

        if "트렌드" in question:
            return "attack_trend"

        if filters.get("uri"):
            return "uri_analysis"

        if filters.get("source_ip"):
            return "ip_analysis"

        if filters.get("host_domain"):
            return "host_analysis"

        if (
            filters.get("rule_name")
            or filters.get("rule_pattern")
        ):
            return "rule_analysis"

        return "generic_analysis"

    @classmethod
    def extract_entities(
        cls,
        question
    ):

        result = {}

        # URI
        uri_match = re.search(
            r"(/[A-Za-z0-9_\-./?=&%]+)",
            question
        )

        if uri_match:
            result["uri"] = uri_match.group(1)

        # Source IP
        ip_match = re.search(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            question
        )

        if ip_match:
            result["source_ip"] = ip_match.group(0)

        # Host Domain
        host_match = re.search(
            r"\b([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
            question
        )

        if host_match:

            value = host_match.group(1)

            if not re.match(
                r"^(?:\d{1,3}\.){3}\d{1,3}$",
                value
            ):
                result["host_domain"] = value

        # Country Name
        for country_name, code in cls.COUNTRY_MAP.items():

            if country_name in question:
                result["source_country"] = code
                break

        # Country Code
        country_match = re.search(
            r"\b(KR|CN|JP|US|RU|TW|HK|SG|IN|VN|TH|MY|ID|CA|MX|GB|DE|FR|IT|ES|NL|BR|AU)\b",
            question.upper()
        )

        if country_match:
            result["source_country"] = (
                country_match.group(1)
            )

        # Action
        if (
            "차단" in question
            or "block" in question.lower()
        ):
            result["action"] = "BLOCK"

        elif (
            "허용" in question
            or "allow" in question.lower()
        ):
            result["action"] = "ALLOW"

        # AWS Managed Rule
        rule_name_match = re.search(
            r"(AWSManagedRules[A-Za-z0-9]+)",
            question
        )

        if rule_name_match:
            result["rule_name"] = (
                rule_name_match.group(1)
            )

        # Generic Rule Pattern
        for keyword, value in cls.RULE_KEYWORDS.items():

            if keyword in question.lower():

                result["rule_pattern"] = value
                break

        return result

    @classmethod
    def extract_time(
        cls,
        question
    ):

        now = datetime.now(KST)

        start_time = now - timedelta(days=1)
        end_time = now

        # 최근 N시간
        hour_match = re.search(
            r"최근\s*(\d+)\s*시간",
            question
        )

        if hour_match:

            start_time = now - timedelta(
                hours=int(hour_match.group(1))
            )

        # 최근 N일
        day_match = re.search(
            r"최근\s*(\d+)\s*일",
            question
        )

        if day_match:

            start_time = now - timedelta(
                days=int(day_match.group(1))
            )

        # 오늘
        if "오늘" in question:

            start_time = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            end_time = now

        # 어제
        elif "어제" in question:

            yesterday
