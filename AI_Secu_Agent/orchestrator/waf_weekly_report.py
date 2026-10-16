from prompt_builder import PromptBuilder

from mcp_tools.athena_client import AthenaClient

from orchestrator.waf_weekly_queries import (
    WAFWeeklyQueries
)


class WAFWeeklyReport:

    @classmethod
    def run(
        cls
    ):

        print(
            "START_WAF_WEEKLY_REPORT"
        )

        #
        # 날짜 계산
        #

        #
        # Athena 쿼리 실행
        #

        #
        # report_data 생성
        #

        #
        # Prompt 생성
        #

        #
        # Bedrock 호출
        #

        #
        # Teams 전송
        #

print(
    "===== REPORT DATA ====="
)

print(
    json.dumps(
        report_data,
        ensure_ascii=False,
        default=str
    )
)
