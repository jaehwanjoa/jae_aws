from planner import Planner
from tool_mapping import get_mapping
from athena_query_generator import (
    AthenaQueryGenerator
)

import uuid


class Orchestrator:

    @classmethod
    def process(
        cls,
        question: str,
        table_name: str
    ):

        request_id = str(
            uuid.uuid4()
        )

        try:

            if not table_name:

                raise ValueError(
                    "table_name is required"
                )

            # 1. Planner
            plan = Planner.parse(
                question
            )

            # 2. Intent Mapping
            mapping = get_mapping(
                plan["intent"]
            )

            # 3. SQL 생성
            query = AthenaQueryGenerator.build(
                plan=plan,
                mapping=mapping,
                table_name=table_name
            )

            return {
                "request_id": request_id,
                "status": "success",

                "intent":
                    plan["intent"],

                "query_type":
                    mapping[
                        "query_type"
                    ],

                "table_name":
                    table_name,

                "plan":
                    plan,

                "query":
                    query
            }

        except Exception as e:

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
