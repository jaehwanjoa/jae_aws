import json
import re


def summarize_result(result_text):

    try:

        if "structuredContent={'result':" in result_text:

            m = re.search(
                r"structuredContent=\{'result': '(.*?)'\} isError",
                result_text,
                re.DOTALL
            )

            if not m:
                return {
                    "summary": "결과 파싱 실패"
                }

            raw_json = m.group(1)

            raw_json = raw_json.encode(
                "utf-8"
            ).decode(
                "unicode_escape"
            )

            data = json.loads(raw_json)

        else:

            start = result_text.find("{")
            end = result_text.rfind("}")

            if start < 0 or end < 0:
                return {
                    "summary": "JSON 영역을 찾을 수 없습니다."
                }

            data = json.loads(
                result_text[start:end + 1]
            )

        reply = data.get("reply", {})

        issues = reply.get(
            "DATA",
            []
        )

        filter_count = reply.get(
            "FILTER_COUNT",
            len(issues)
        )

        summary_items = []

        for issue in issues[:10]:

            summary_items.append(
                {
                    "id": issue.get("id"),
                    "severity": issue.get("severity"),
                    "asset": (
                        issue.get("asset_names", [""])
                    )[0],
                    "name": issue.get("name")
                }
            )

        return {
            "count": filter_count,
            "top_issues": summary_items
        }

    except Exception as e:

        return {
            "summary": f"파싱 오류: {str(e)}"
        }
