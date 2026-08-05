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

    @classmethod
    def parse(cls, question:str):

        filters = {}

        filters.update(
            cls.extract_time(question)
        )

        filters.update(
            cls.extract_entities(question)
        )

        return {
            "intent": cls.detect_intent(filters),
            "filters": filters
        }

    @classmethod
    def detect_intent(cls, filters):

        if filters.get("uri"):
            return "uri_analysis"

        if filters.get("source_ip"):
            return "ip_analysis"

        if filters.get("rule_pattern"):
            return "rule_analysis"

        return "generic_analysis"

    @classmethod
    def extract_entities(cls, question):

        result = {}

        # URI
        uri_match = re.search(
            r"(/\S+)",
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

        # Country Name
        for country_name, code in cls.COUNTRY_MAP.items():

            if country_name in question:
                result["source_country"] = code
                break

        # Country Code
        country_match = re.search(
            r"\b(KR|CN|JP|US|RU|TW|HK|SG|IN|VN|TH|MY|ID|CA|GB|DE|FR|IT|ES|NL|BR|AU)\b",
            question.upper()
        )

        if country_match:
            result["source_country"] = (
                country_match.group(1)
            )

        # Action
        if "차단" in question or "block" in question.lower():
            result["action"] = "BLOCK"

        elif "허용" in question or "allow" in question.lower():
            result["action"] = "ALLOW"

        # Rule Pattern
        rule_keywords = [
            "SQL Injection",
            "SQLi",
            "XSS",
            "Path Traversal",
            "Command Injection",
            "Bad Bot"
        ]

        for keyword in rule_keywords:

            if keyword.lower() in question.lower():

                result["rule_pattern"] = keyword
                break

        return result

    @classmethod
    def extract_time(cls, question):

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

        # 어제
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

        return {
            "start_time": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "end_time": end_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
