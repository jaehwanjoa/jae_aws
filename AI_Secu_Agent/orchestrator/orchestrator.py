import json
import boto3
import os
import os
import requests
import re
import uuid
import traceback
import xmltodict

from mcp_tools.cortex_executor import CortexExecutor
from agent.router import select_route
from agent.cortex_query import build_issue_query
from agent.summarizer import summarize_result








WF_CACHE_TTL = 3600


def get_wildfire_report(sha256: str):

    api_key = os.environ["WF_API_KEY"]

    response = requests.post(
        "https://wildfire.paloaltonetworks.com/publicapi/get/report",
        files={
            "apikey": (None, api_key),
            "hash": (None, sha256)
        },
        timeout=30
    )

    response.raise_for_status()

    return xmltodict.parse(
        response.text
    )




def summarize_wildfire(report):

    try:

        wildfire = report.get(
            "wildfire",
            {}
        )

        file_info = (
            wildfire.get(
                "file_info",
                {}
            )
        )

        result = {

            "malware":
                file_info.get(
                    "malware"
                ),

            "sha256":
                file_info.get(
                    "sha256"
                ),

            "filetype":
                file_info.get(
                    "filetype"
                )
        }

        return result

    except Exception as e:

        print(
            f"WF_SUMMARY_ERROR={e}"
        )

        return {}



def extract_wildfire_detail(report):

    try:

        wildfire = report.get(
            "wildfire",
            {}
        )

        file_info = wildfire.get(
            "file_info",
            {}
        )

        task_info = wildfire.get(
            "task_info",
            {}
        )

        reports = task_info.get(
            "report",
            []
        )

        if not isinstance(
            reports,
            list
        ):
            reports = [reports]

        summary = []
        network = []
        registry = []
        process_tree = []

        for r in reports:

            #
            # Summary
            #
            entries = (
                r.get(
                    "summary",
                    {}
                ).get(
                    "entry",
                    []
                )
            )

            if not isinstance(
                entries,
                list
            ):
                entries = [entries]

            for e in entries:

                if isinstance(
                    e,
                    dict
                ):

                    text_val = e.get(
                        "#text"
                    )

                    if text_val:

                        summary.append(
                            text_val
                        )

            #
            # Network
            #
            net = r.get(
                "network",
                {}
            )

            if net:

                network.append(
                    net
                )

            #
            # Registry
            #
            reg = r.get(
                "registry_set",
                {}
            )

            if reg:

                registry.append(
                    reg
                )

            #
            # Process
            #
            proc = r.get(
                "process_tree",
                {}
            )

            if proc:

                process_tree.append(
                    proc
                )

        return {

            "file_info":
                file_info,

            "summary":
                list(
                    dict.fromkeys(
                        summary
                    )
                )[:20],

            "network":
                network[:10],

            "registry":
                registry[:10],

            "process_tree":
                process_tree[:10]

        }

    except Exception as e:

        print(
            f"WF_DETAIL_ERROR={e}"
        )

        return {}


class Orchestrator:

    @classmethod
    def process(
        cls,
        question,
        customer
    ):

        print("### PROCESS START ###")

        request_id = str(
            uuid.uuid4()
        )

        try:

            route = select_route(
                question
            )

            print("ROUTE=")
            print(route)

            if not route:

                return {

                    "request_id":
                        request_id,

                    "status":
                        "error",

                    "message":
                        "지원하지 않는 질문입니다."
                }

            #
            # Malware Detail
            #
            if route.get(
                "intent"
            ) == "ONS_MALWARE_DETAIL":

                print(
                    "MALWARE DETAIL REQUEST"
                )

                return {

                    "request_id":
                        request_id,

                    "status":
                        "success",

                    "route":
                        route,

                    "summary": {

                        "message":
                            "Malware Detail 진입",

                        "selected_no":
                            route.get(
                                "selected_no"
                            )
                    }
                }

            #
            # Filename Search
            #
            if route.get(
                "intent"
            ) == "FILENAME_SEARCH":

                filename = (
                    route.get(
                        "filename",
                        ""
                    ).lower()
                )

                print(
                    f"FILENAME_SEARCH={filename}"
                )

                record = (
                    lookup_filename_index(
                        filename
                    )
                )

                if not record:

                    return {
                        "request_id":
                            request_id,
                        "status":
                            "not_found",
                        "message":
                            f"{filename} not found"
                    }

                sha256 = record[
                    "sha256"
                ]

                print(
                    f"S3_LOOKUP_SHA256={sha256}"
                )

                cached_name = filename

                data = {
                    "incident":
                        record
                }

                if True:

                        print(
                            "CACHE HIT"
                        )

                        print(
                            f"WF_SHA256={sha256}"
                        )

                        print(
                            "WF_REPORT_START"
                        )

                        wf_report = (
                            get_wildfire_report(
                                sha256
                            )
                        )

                        print(
                            "WF_REPORT_FETCH_OK"
                        )

                        wf_summary = (
                            summarize_wildfire(
                                wf_report
                            )
                        )

                        wf_detail = (
                            extract_wildfire_detail(
                                wf_report
                            )
                        )

                        return {
                            "request_id":
                                request_id,
                            "status":
                                "success",
                            "route":
                                route,
                            "summary": {
                                "file_name":
                                    cached_name,
                                "sha256":
                                    sha256,
                                "incident":
                                    data.get(
                                        "incident"
                                    ),
                                "wildfire":
                                    wf_summary,

                                "wildfire_detail":
                                    wf_detail
                            }
                        }

                return {
                    "request_id":
                        request_id,
                    "status":
                        "not_found",
                    "message":
                        f"{filename} not found in cache"
                }

            #
            # Cortex
            #
            if route["source"] == "cortex":

                query = build_issue_query(
                    route
                )

                print("QUERY=")
                print(query)

                result = CortexExecutor.execute(

                    "get_issues",

                    {
                        "filters":
                            query["filters"],

                        "search_from":
                            0,

                        "search_to":
                            10
                    }
                )

                print("RESULT=")
                print(str(result))
                print(type(result))

                try:

                    print(
                        "PARSER BLOCK ENTER"
                    )

                    raw_json = (
                        result.structuredContent[
                            "result"
                        ]
                    )

                    try:

                        data = json.loads(
                            raw_json
                        )

                    except json.JSONDecodeError as e:

                        print(
                            f"JSON Parse Error={e}"
                        )

                        start = max(
                            0,
                            e.pos - 100
                        )

                        end = min(
                            len(raw_json),
                            e.pos + 100
                        )

                        print(
                            "===== ERROR CONTEXT START ====="
                        )

                        print(
                            raw_json[
                                start:end
                            ]
                        )

                        print(
                            "===== ERROR CONTEXT END ====="
                        )

                        sanitized = re.sub(
                            r'\\(?!["\\/bfnrtu])',
                            r'\\\\',
                            raw_json
                        )

                        print(
                            "Invalid escape sequence sanitized"
                        )

                        data = json.loads(
                            sanitized
                        )

                    if route["intent"] == "ONS-Malware":

                        data["reply"]["DATA"] = [
                            x
                            for x
                            in data[
                                "reply"
                            ]["DATA"]
                            if x.get(
                                "status.progress"
                            )
                            != "Resolved"
                        ]

                    elif route["intent"] == "ONS_Vul_Monitoring":

                        data["reply"]["DATA"] = [
                            x
                            for x
                            in data[
                                "reply"
                            ]["DATA"]
                            if (
                                x.get(
                                    "severity"
                                )
                                == "CRITICAL"
                            )
                            and (
                                x.get(
                                    "status.progress"
                                )
                                == "New"
                            )
                        ]

                    print(
                        "FILTERED_COUNT="
                    )

                    print(
                        len(
                            data["reply"][
                                "DATA"
                            ]
                        )
                    )

                    if data["reply"]["DATA"]:

                        print(
                            "FIRST_MALWARE_RECORD="
                        )

                        print(
                            json.dumps(
                                data["reply"][
                                    "DATA"
                                ][0],
                                indent=2,
                                ensure_ascii=False
                            )
                        )

                        first_record = (
                            data["reply"]["DATA"][0]
                        )

                        print(
                            f"ISSUE_ID={first_record.get('id')}"
                        )

                        print(
                            f"CASE_IDS={first_record.get('case_ids')}"
                        )

                        print(
                            f"FINDINGS={first_record.get('findings')}"
                        )

                        print("MARKER_A")

                        issue_id = str(
                            first_record.get("id")
                        )

                        incident_detail = None

                        intent = (
                            route.get("intent")
                            if route
                            else None
                        )

                        print(
                            f"INTENT={intent}"
                        )

                        intent = (
                            route.get("intent")
                            if route
                            else None
                        )

                        if False:
                            print(
                                "SKIP_INCIDENT_DETAIL_FOR_ONS_MALWARE"
                            )

                            incident_detail = None

                            result = json.dumps(
                                data,
                                ensure_ascii=False
                            )

                        else:

                            print("MARKER_B")

                            print(
                                "STEP1"
                            )

                            incident_detail = (
                                CortexExecutor.execute(
                                    "get_incident_detail",
                                    {
                                        "incident_id": issue_id
                                    }
                                )
                            )

                        print(
                            "STEP2"
                        )

                        print(
                            "INCIDENT_DETAIL="
                        )

                        print(
                            incident_detail
                        )

                        if (
                            incident_detail
                            and incident_detail.structuredContent
                            and "result"
                            in incident_detail.structuredContent
                        ):
                            try:
                                incident_detail_json = (
                                    json.loads(
                                        incident_detail
                                        .structuredContent[
                                            "result"
                                        ]
                                    )
                                )

                                data["reply"]["DATA"][0][
                                    "incident_detail"
                                ] = incident_detail_json

                                sha256 = (
                                    incident_detail_json.get(
                                        "sha256"
                                    )
                                )

                                print(
                                    "INCIDENT_DETAIL_JSON="
                                )

                                print(
                                    json.dumps(
                                        incident_detail_json,
                                        indent=2,
                                        ensure_ascii=False
                                    )
                                )

                                print(
                                    f"SHA256_DEBUG={sha256}"
                                )

                                if sha256:

                                    save_filename_index(
                                        incident_detail_json.get(
                                            "file_name"
                                        ),
                                        sha256,
                                        incident_detail_json.get(
                                            "incident_id"
                                        )
                                    )

                                    print(
                                        "S3_INDEX_SAVE="
                                        + str(
                                            incident_detail_json.get(
                                                "file_name"
                                            )
                                        )
                                    )

                                intent = (
                                    route.get(
                                        "intent"
                                    )
                                    if route
                                    else None
                                )

                                WF_DETAIL_INTENTS = {

                                    "SHA256_SEARCH",
                                    "FILENAME_SEARCH"

                                }

                                print(
                                    f"INTENT={intent}"
                                )

                                if (
                                    sha256
                                    and intent != "ONS-Malware"
                                ):

                                    print("WF_REPORT_START")

                                    try:

                                        wildfire_report = (
                                            get_wildfire_report(
                                                sha256
                                            )
                                        )

                                    except Exception as e:

                                        print(
                                            f"WF_REPORT_ERROR={e}"
                                        )

                                        wildfire_report = {}

                                    if not wildfire_report:

                                        print(
                                            "WF_REPORT_EMPTY"
                                        )

                                    elif intent == "ONS-Malware":

                                        data["reply"]["DATA"][0][
                                            "wildfire"
                                        ] = summarize_wildfire(
                                            wildfire_report
                                        )

                                    elif (
                                        intent
                                        in
                                        WF_DETAIL_INTENTS
                                    ):

                                        data["reply"]["DATA"][0][
                                            "issue_summary"
                                        ] = {

                                            "file_name":
                                                data["reply"]["DATA"][0].get(
                                                    "file_name"
                                                ),

                                            "severity":
                                                data["reply"]["DATA"][0].get(
                                                    "severity"
                                                ),

                                            "sha256":
                                                sha256
                                        }

                                        data["reply"]["DATA"][0][
                                            "wildfire"
                                        ] = extract_wildfire_detail(
                                            wildfire_report
                                        )

                                    print("WF_REPORT_END")

                                print("INCIDENT_DETAIL_MERGED")

                                print(
                                    json.dumps(
                                        data["reply"]["DATA"][0],
                                        indent=2,
                                        ensure_ascii=False
                                    )
                                )

                            except Exception as e:
                                print(
                                    f"INCIDENT_DETAIL_PARSE_ERROR={e}"
                                )

                    result = json.dumps(
                        data,
                        ensure_ascii=False
                    )

                except Exception as e:

                    print(
                        f"FILTER ERROR={e}"
                    )

                print(
                    "FILTERED_RESULT="
                )

                print(result)
                print(type(result))

                summary = summarize_result(
                    str(result)
                )

                return {

                    "request_id":
                        request_id,

                    "status":
                        "success",

                    "route":
                        route,

                    "summary":
                        summary
                }

            #
            # Athena
            #
            if route["source"] == "athena":

                return {

                    "request_id":
                        request_id,

                    "status":
                        "success",

                    "route":
                        route,

                    "message":
                        "Athena 분기 예정"
                }

            return {

                "request_id":
                    request_id,

                "status":
                    "error",

                "message":
                    "지원하지 않는 source"
            }

        except Exception as e:

            print("EXCEPTION=")
            print(repr(e))

            print(
                traceback.format_exc()
            )

            return {

                "request_id":
                    request_id,

                "status":
                    "error",

                "message":
                    str(e)
            }



S3_BUCKET = os.environ["S3_BUCKET"]

s3_client = boto3.client("s3")


def save_filename_index(
    file_name,
    sha256,
    incident_id
):

    try:

        data = {}

        try:

            obj = s3_client.get_object(
                Bucket=S3_BUCKET,
                Key="wf-index.json"
            )

            data = json.loads(
                obj["Body"].read()
            )

        except Exception:
            data = {}

        data[file_name.lower()] = {
            "sha256": sha256,
            "incident_id": incident_id
        }

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key="wf-index.json",
            Body=json.dumps(data)
        )

        print(
            f"S3_INDEX_SAVE={file_name}"
        )

    except Exception as e:

        print(
            f"S3_INDEX_ERROR={e}"
        )


def lookup_filename_index(
    file_name
):

    try:

        obj = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key="wf-index.json"
        )

        data = json.loads(
            obj["Body"].read()
        )

        return data.get(
            file_name.lower()
        )

    except Exception as e:

        print(
            f"S3_LOOKUP_ERROR={e}"
        )

        return None

