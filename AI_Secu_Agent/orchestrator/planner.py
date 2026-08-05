import re

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")


class Planner:

    COUNTRY_MAP = {
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
        "미국": "US",
        "캐나다": "CA",
        "멕시코": "MX",
        "영국": "GB",
        "독일": "DE",
        "프랑스": "FR",
        "이탈리아": "IT",
        "스페인": "ES",
        "네덜란드": "NL",
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

        intent = cls.detect_intent(
            question,
            filters
        )

        return {
            "intent": intent,
            "filters": filters,
            "original_question": question
        }

    @classmethod
    def detect_intent(
        cls,
        question,
        filters
    ):

        lower_question = question.lower()

        # Top URI
        if (
            (
                "uri" in lower_question
                or "url" in lower_question
            )
            and (
                "top" in lower_question
                or "상위" in question
                or "많이" in question
                or "가장" in question
            )
        ):
            return "top_uri"

        # Top IP
        if (
            "ip" in lower_question
            and (
                "top" in lower_question
                or "상위" in question
                or "많이" in question
                or "가장" in question
            )
        ):
            return "top_ip"

        # Trend
        if (
            "트렌드" in question
            or "추이" in question
        ):
            return "attack_trend"

        # URI
        if filters.get("uri"):
            return "uri_analysis"

        # IP
        if filters.get("source_ip"):
            return "ip_analysis"

        # Host
        if filters.get("host_domain"):
            return "host_analysis"

        # Rule
        if (
            filters.get("rule_group")
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

        lower_question = question.lower()

        # URI
        uri_match = re.search(
            r"(/[^\s]+)",
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

            if not re.fullmatch(
                r"(?:\d{1,3}\.){3}\d{1,3}",
                value
            ):
                result["host_domain"] = value

        # Query String
        query_match = re.search(
            r"([a-zA-Z0-9_-]+=[^\s]+)",
            question
        )

        if query_match:
            result["query_string"] = (
                query_match.group(1)
            )

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
            or "block" in lower_question
        ):
            result["action"] = "BLOCK"

        elif (
            "허용" in question
            or "allow" in lower_question
        ):
            result["action"] = "ALLOW"

        elif "count" in lower_question:
            result["action"] = "COUNT"

        elif "captcha" in lower_question:
            result["action"] = "CAPTCHA"

        elif "challenge" in lower_question:
            result["action"] = "CHALLENGE"

        # Rule Group
        rule_group_match = re.search(
            r"(AWSManagedRules[\w\-]+)",
            question
        )

        if rule_group_match:

            result["rule_group"] = (
                rule_group_match.group(1)
            )

        # Rule Pattern
        for keyword, value in cls.RULE_KEYWORDS.items():

            if keyword in lower_question:

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

        hour_match = re.search(
            r"최근\s*(\d+)\s*시간",
            question
        )

        if hour_match:

            start_time = now - timedelta(
                hours=int(hour_match.group(1))
            )

        day_match = re.search(
            r"최근\s*(\d+)\s*일",
            question
        )

        if day_match:

            start_time = now - timedelta(
                days=int(day_match.group(1))
            )

        if "오늘" in question:

            start_time = now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            end_time = now

        elif "어제" in question:

            yesterday = now - timedelta(days=1)

            start_time = yesterday.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            end_time = yesterday.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )

        elif "이번주" in question:

            start_time = (
                now - timedelta(days=now.weekday())
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        elif "지난주" in question:

            this_week_start = (
                now - timedelta(days=now.weekday())
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            start_time = (
                this_week_start
                - timedelta(days=7)
            )

            end_time = (
                this_week_start
                - timedelta(seconds=1)
            )

        elif "이번달" in question:

            start_time = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        elif "지난달" in question:

            first_day_this_month = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            end_time = (
                first_day_this_month
                - timedelta(seconds=1)
            )

            start_time = end_time.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        return {
            "start_time": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "end_time": end_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "timezone": "Asia/Seoul"
        }
