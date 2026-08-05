from planner import Planner
from tool_mapping import get_mapping
from athena_query_generator import AthenaQueryGenerator

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

            # 1. 자연어 분석
            plan = Planner.parse(
                question
            )

            # 2. Intent 매핑
            mapping = get_mapping(
                plan["intent"]
            )

            # 3. Athena Query 생성
            query = AthenaQueryGenerator.build(
                plan=plan,
                mapping=mapping,
                table_name=table_name
            )

            return {
                "request_id": request_id,
                "status": "success",
                "plan": plan,
                "mapping": mapping,
                "table_name": table_name,
                "query": query
            }

        except Exception as e:

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
