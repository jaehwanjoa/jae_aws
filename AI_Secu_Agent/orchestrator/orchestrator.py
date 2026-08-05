from planner import Planner
from tool_mapping import get_mapping
from athena_query_generator import AthenaQueryGenerator

import uuid


class Orchestrator:

    @classmethod
    def process(
        cls,
        question: str
    ):

        request_id = str(
            uuid.uuid4()
        )

        try:

            plan = Planner.parse(
                question
            )

            mapping = get_mapping(
                plan["intent"]
            )

            query = AthenaQueryGenerator.build(
                plan,
                mapping
            )

            return {
                "request_id": request_id,
                "status": "success",
                "plan": plan,
                "mapping": mapping,
                "query": query
            }

        except Exception as e:

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
