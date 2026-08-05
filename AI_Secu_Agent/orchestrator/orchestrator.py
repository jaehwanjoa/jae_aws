from planner import Planner
from tool_mapping import get_mapping
from athena_query_generator import AthenaQueryGenerator


class Orchestrator:

    @classmethod
    def process(
        cls,
        question: str
    ):

        # 1. 자연어 분석
        plan = Planner.parse(
            question
        )

        # 2. Intent 매핑
        mapping = get_mapping(
            plan["intent"]
        )

        # 3. Athena SQL 생성
        query = AthenaQueryGenerator.build(
            plan
        )

        return {
            "plan": plan,
            "mapping": mapping,
            "query": query
        }
