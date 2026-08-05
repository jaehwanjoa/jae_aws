from orchestrator.planner import Planner
from orchestrator.tool_mapping import (
    get_mapping
)
from mcp.athena.query_generator import (
    AthenaQueryGenerator
)


class Orchestrator:

    @classmethod
    def process(
        cls,
        question
    ):

        # 1. 질문 분석
        plan = Planner.parse(
            question
        )

        # 2. Intent 매핑
        mapping = get_mapping(
            plan["intent"]
        )

        # 3. SQL 생성
        sql = AthenaQueryGenerator.build(
            plan
        )

        # 4. MCP 호출
        result = cls.execute_athena(
            sql
        )

        # 5. Bedrock 요약
        response = cls.generate_answer(
            question,
            result
        )

        return response
