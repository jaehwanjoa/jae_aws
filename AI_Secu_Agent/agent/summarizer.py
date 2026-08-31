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

            raw_json = (
                raw_json
                .encode("utf-8")
                .decode("unicode_escape")
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

        reply = data.get(
            "reply",
            {}
        )

        issues = reply.get(
            "DATA",
            []
        )

        filter_count = reply.get(
            "FILTER_COUNT",
            len(issues)
        )

        if filter_count == 0:

            return {
                "count": 0,
                "message": "현재 조회 조건에 해당하는 이벤트가 없습니다.",
                "top_issues": []
            }

        summary_items = []

        for idx, issue in enumerate(
            issues[:10],
            start=1
        ):

            findings = issue.get(
                "findings",
                []
            )

            incident_detail = issue.get(
                "incident_detail",
                {}
            )

            category = issue.get(
                "category"
            )

            item = {

                "index": idx,

                "id":
                    issue.get("id"),

                "name":
                    issue.get("name"),

                "severity":
                    issue.get("severity"),

                "status":
                    issue.get(
                        "status.progress"
                    ),

                "category":
                    category
            }

            if category == "Malware":

                item.update({

                    "hostname":
                        incident_detail.get(
                            "hostname"
                        ),

                    "container_name":
                        incident_detail.get(
                            "container_name"
                        ),

                    "image_name":
                        incident_detail.get(
                            "image_name"
                        ),

                    "account_id":
                        incident_detail.get(
                            "account_id"
                        ),

                    "asset_name":
                        incident_detail.get(
                            "asset_name"
                        ),

                    "file_name":
                        incident_detail.get(
                            "file_name"
                        ),

                    "file_path":
                        incident_detail.get(
                            "file_path"
                        ),

                    "sha256":
                        incident_detail.get(
                            "sha256"
                        ),

                    "user":
                        incident_detail.get(
                            "user"
                        ),

                    "initiator":
                        incident_detail.get(
                            "initiator"
                        )
                })

            else:

                item.update({

                    "finding_id":
                        findings[0]
                        if findings
                        else None,

                    "asset_names":
                        issue.get(
                            "asset_names",
                            []
                        ),

                    "cve_id":
                        incident_detail.get(
                            "cve_id"
                        ),

                    "cvss_score":
                        incident_detail.get(
                            "cvss_score"
                        ),

                    "file_path":
                        incident_detail.get(
                            "file_path"
                        ),

                    "fix_versions":
                        incident_detail.get(
                            "fix_versions"
                        )
                })

            summary_items.append(item)

        return {
            "count":
                filter_count,

            "top_issues":
                summary_items
        }

    except Exception as e:

        return {
            "summary":
                f"파싱 오류: {str(e)}"
        }
