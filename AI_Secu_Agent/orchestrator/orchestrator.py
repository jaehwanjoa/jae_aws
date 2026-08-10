import json
import re
from mcp_tools.cortex_executor import CortexExecutor
from agent.router import select_route
from agent.cortex_query import build_issue_query
from agent.summarizer import summarize_result

import uuid
import traceback


class Orchestrator:

    @classmethod
    def process(
        cls,
        question,
        customer
    ):

        print("### PROCESS START ###")

        request_id = str(uuid.uuid4())

        try:

            route = select_route(question)

            print("ROUTE=")
            print(route)

            if not route:
                return {
                    "request_id": request_id,
                    "status": "error",
                    "message": "지원하지 않는 질문입니다."
                }

            #
            # Cortex
            #
            if route["source"] == "cortex":

                query = build_issue_query(route)

                print("QUERY=")
                print(query)

                result = CortexExecutor.execute(
                    "get_issues",
                    {
                        "filters": query["filters"],
                        "search_from": 0,
                        "search_to": 10
                    }
                )

                print("RESULT=")
                print(str(result))
                print(type(result))

                if route["intent"] == "ONS-Malware":
                    try:
                        raw_json = result.structuredContent["result"]

                        # raw_json newline conversion disabled
                        # raw_json = (
                        #     raw_json
                        #     .replace("\\n", "\n")
                        # )

                        try:
                            data = json.loads(raw_json)

                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error={e}")

                            start = max(0, e.pos - 100)
                            end = min(len(raw_json), e.pos + 100)

                            print("===== ERROR CONTEXT START =====")
                            print(raw_json[start:end])
                            print("===== ERROR CONTEXT END =====")

                            sanitized = re.sub(
                                r'\\(?!["\\/bfnrtu])',
                                r'\\\\',
                                raw_json
                            )

                            print("Invalid escape sequence sanitized")

                            data = json.loads(sanitized)

                        data["reply"]["DATA"] = [
                            x
                            for x in data["reply"]["DATA"]
                            if x.get("status.progress") != "Resolved"
                        ]

                        print("FILTERED_COUNT=")
                        print(len(data["reply"]["DATA"]))

                        result = json.dumps(data)

                    except Exception as e:
                        print(f"FILTER ERROR={e}")

                print("FILTERED_RESULT=")
                print(result)
                print(type(result))
                summary = summarize_result(
                    str(result)
                )

                return {
                    "request_id": request_id,
                    "status": "success",
                    "route": route,
                    "summary": summary
                }

            #
            # Athena
            #
            if route["source"] == "athena":

                return {
                    "request_id": request_id,
                    "status": "success",
                    "route": route,
                    "message": "Athena 분기 예정"
                }

            return {
                "request_id": request_id,
                "status": "error",
                "message": "지원하지 않는 source"
            }

        except Exception as e:

            print("EXCEPTION=")
            print(repr(e))

            print(traceback.format_exc())

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }


