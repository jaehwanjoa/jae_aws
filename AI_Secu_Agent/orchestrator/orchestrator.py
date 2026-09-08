import json
import boto3
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
from agent.prompt_builder import PromptBuilder
from agent.bedrock_analyzer import BedrockAnalyzer
from util.mail_sender import (
    send_mail
)

WF_CACHE_TTL = 3600

S3_BUCKET = os.environ["S3_BUCKET"]

s3_client = boto3.client(
    "s3"
)

MAIL_SENDER = "cp-report@cj.net"

MAIL_RECEIVERS = [
    "jaehwan.myeong@cj.net"
]

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
            Body=json.dumps(
                data,
                ensure_ascii=False
            )
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




S3_BUCKET = os.environ["S3_BUCKET"]

s3_client = boto3.client(
    "s3"
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

def build_wf_summary(
    wildfire_report
):

    wf_info = (
        wildfire_report.get(
            "wildfire",
            {}
        )
    )

    file_info = (
        wf_info.get(
            "file_info",
            {}
        )
    )

    reports = (
        wf_info.get(
            "task_info",
            {}
        )
        .get(
            "report",
            []
        )
    )

    summary_entries = []

    if reports:

        summary_entries = (
            reports[0]
            .get(
                "summary",
                {}
            )
            .get(
                "entry",
                []
            )
        )

    behavior_summary = []

    for item in summary_entries[:15]:

        behavior_summary.append(
            {
                "behavior":
                    item.get("@behavior"),

                "score":
                    item.get("@score"),

                "description":
                    item.get("#text")
            }
        )

    return {

        "sha256":
            file_info.get(
                "sha256"
            ),

        "filetype":
            file_info.get(
                "filetype"
            ),

        "size":
            file_info.get(
                "size"
            ),

        "malware":
            file_info.get(
                "malware"
            ),

        "summary":
            behavior_summary
    }

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
    def process_s3_incident(
        cls,
        issue_id,
        cspm_sha256=None,
        cspm_verdict=None
    ):


        print(
            f"S3_DIRECT_INCIDENT={issue_id}"
        )

        result = CortexExecutor.execute(
            "get_incident_detail",
            {
                "incident_id": str(issue_id)
            }
        )

        print(
            "INCIDENT_DETAIL="
        )

        print(result)

        try:

            incident_detail_json = json.loads(
                result.structuredContent[
                    "result"
                ]
            )

            print(
                "S3_INCIDENT_DETAIL_JSON="
            )

            print(
                json.dumps(
                    incident_detail_json,
                    indent=2,
                    ensure_ascii=False
                )
            )

            incident_type = (
                incident_detail_json.get(
                    "incident_type"
                )
            )
            
            source_type = (
                incident_detail_json.get(
                    "source_type"
                )
            )
            
            if not source_type:
            
                if (
                    incident_detail_json.get("initiator_cmd")
                    or incident_detail_json.get("mitre_tactic")
                    or incident_detail_json.get("causality_id")
                    or incident_detail_json.get("actor_process_instance_id")
                ):
                    source_type = "AGENT"
                else:
                    source_type = "CSPM"
        
            print(
                f"SOURCE_TYPE={source_type}"
            )
            
            print(
                f"S3_INCIDENT_TYPE={incident_type}"
            )

            if cspm_sha256:
                incident_detail_json["sha256"] = cspm_sha256

            if cspm_verdict:
                incident_detail_json["verdict"] = cspm_verdict

            if incident_type == "MALWARE":

                sha256 = (
                    incident_detail_json.get(
                        "sha256"
                    )
                )

                finding_id = (
                    incident_detail_json.get(
                        "finding_id"
                    )
                )

                wf_hash = sha256

                file_name = (
                    incident_detail_json.get(
                        "file_name"
                    )
                )

                print(
                    f"WF_SHA256={sha256}"
                )

                print(
                    f"WF_FINDING_ID={finding_id}"
                )

                print(
                    f"WF_HASH={wf_hash}"
                )

                print(
                    f"WF_FILE_NAME={file_name}"
                )

                if (
                    not sha256
                    and file_name
                ):

                    try:

                        record = (
                            lookup_filename_index(
                                file_name.lower()
                            )
                        )

                        if record:

                            sha256 = (
                                record.get(
                                    "sha256"
                                )
                            )

                            wf_hash = sha256

                            print(
                                f"S3_LOOKUP_SHA256={sha256}"
                            )

                    except Exception as e:

                        print(
                            f"S3_LOOKUP_ERROR={e}"
                        )
                        
                if not wf_hash:
                
                    print(
                        "WF_REPORT_SKIP_NO_HASH"
                    )

                    if source_type == "AGENT":
                
                        prompt = (
                            PromptBuilder.build_agent_prompt(
                                incident_detail_json,
                                None
                            )
                        )
                
                        print(
                            f"PROMPT_LENGTH={len(prompt)}"
                        )
                
                        analysis = (
                            BedrockAnalyzer.analyze(
                                prompt
                            )
                        )
                
                        print(
                            "BEDROCK_ANALYSIS_START"
                        )
                
                        print(
                            analysis
                        )
                
                    elif source_type == "CSPM":
                
                        print(
                            "CSPM_NO_SHA256_SKIP"
                        )
                
                else:
                
                    print(
                        "WF_REPORT_START"
                    )
                
                    try:
                
                        wildfire_report = (
                            get_wildfire_report(
                                wf_hash
                            )
                        )
                
                        print(
                            "WF_REPORT_FETCH_OK"
                        )
                
                        wf_summary = (
                            build_wf_summary(
                                wildfire_report
                            )
                        )
                
                        print(
                            "WF_SUMMARY="
                        )
                
                        print(
                            json.dumps(
                                wf_summary,
                                ensure_ascii=False,
                                indent=2
                            )
                        )
                
                        if source_type == "CSPM":
                
                            prompt = (
                                PromptBuilder.build_cspm_prompt(
                                    incident_detail_json,
                                    wf_summary
                                )
                            )
                
                        else:
                
                            prompt = (
                                PromptBuilder.build_agent_prompt(
                                    incident_detail_json,
                                    wf_summary
                                )
                            )
                
                        print(
                            f"PROMPT_LENGTH={len(prompt)}"
                        )
                
                        print(
                            "BEDROCK_PROMPT_START"
                        )
                
                        print(
                            prompt[:3000]
                        )
                
                        analysis = (
                            BedrockAnalyzer.analyze(
                                prompt
                            )
                        )
                
                        print(
                            "BEDROCK_ANALYSIS_START"
                        )
                
                        print(
                            analysis
                        )
                        
                        analysis_html = analysis.replace("\n", "<br>")
                        
                        severity = incident_detail_json.get("severity", "Unknown")
                        
                        severity_color = {
                            "Critical": "#d32f2f",
                            "High": "#f57c00",
                            "Medium": "#fbc02d",
                            "Low": "#388e3c"
                        }.get(severity, "#1976d2")
                        
                        body = f"""
                        <html>
                        <head>
                        <meta charset="UTF-8">
                        </head>
                        
                        <body style="font-family: Arial, sans-serif; background:#f5f5f5; padding:20px;">
                        
                        <div style="
                            background:white;
                            border-radius:10px;
                            padding:20px;
                            border:1px solid #dddddd;
                        ">
                        
                        <h2 style="margin-top:0;">
                        🚨 Cortex Security Incident Report
                        </h2>
                        
                        <div style="
                            background:{severity_color};
                            color:white;
                            padding:10px;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                        Severity : {severity}
                        </div>
                        
                        <br>
                        
                        <table style="border-collapse:collapse;width:100%;">
                        <tr>
                            <td style="border:1px solid #ddd;padding:8px;"><b>Incident ID</b></td>
                            <td style="border:1px solid #ddd;padding:8px;">{incident_detail_json.get('incident_id')}</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd;padding:8px;"><b>Source Type</b></td>
                            <td style="border:1px solid #ddd;padding:8px;">{source_type}</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd;padding:8px;"><b>Issue Name</b></td>
                            <td style="border:1px solid #ddd;padding:8px;">{incident_detail_json.get('issue_name')}</td>
                        </tr>
                        </table>
                        
                        <br>
                        
                        <div style="
                            background:#f8f9fa;
                            border-left:5px solid #1976d2;
                            padding:15px;
                        ">
                        
                        <h3 style="margin-top:0;">
                        분석 결과
                        </h3>
                        
                        {analysis_html}
                        
                        </div>
                        
                        <br>
                        
                        <hr>
                        
                        <div style="font-size:11px;color:#666;">
                        본 이메일 및 첨부파일은 지정된 수신인을 위한 내용입니다.
                        </div>
                        
                        </div>
                        
                        </body>
                        </html>
                        """                                           

                        for receiver in MAIL_RECEIVERS:
                        
                            try:
                        
                                send_mail(
                                    subject=subject,
                                    body=body,
                                    sender=MAIL_SENDER,
                                    receiver=receiver
                                )
                        
                                print(
                                    f"MAIL_SENT={receiver}"
                                )
                        
                            except Exception as mail_error:
                        
                                print(
                                    f"MAIL_SEND_ERROR={receiver}: "
                                    f"{type(mail_error).__name__}: {mail_error}"
                                )                        
                                     
                    except Exception as e:
                
                        print(
                            f"WF_REPORT_ERROR={str(e)}"
                        )
                
                        import traceback
                
                        print(
                            traceback.format_exc()
                        )
                                      
        except Exception as e:

            print(
                f"S3_PROCESS_ERROR={e}"
            )

        return {
            "status": "success",
            "issue_id": issue_id,
        }

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
                                        "incident_id": issue_id,
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

                                if sha256:

                                    print(
                                        "WF_REPORT_START"
                                    )

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

                                    elif intent == "ONS_MALWARE":

                                        data["reply"]["DATA"][0][
                                            "wildfire"
                                        ] = (
                                            summarize_wildfire(
                                                wildfire_report
                                            )
                                        )

                                    elif intent in WF_DETAIL_INTENTS:

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
                                        ] = (
                                            extract_wildfire_detail(
                                                wildfire_report
                                            )
                                        )

                                print(
                                    "WF_REPORT_END"
                                )

                                print(
                                    "INCIDENT_DETAIL_MERGED"
                                )

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

                print(
                    result
                )

                print(
                    type(result)
                )

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

            print(
                "EXCEPTION="
            )

            print(
                repr(e)
            )

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
