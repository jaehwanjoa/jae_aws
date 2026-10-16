import json

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
        # 예시 데이터
        #

        report_data = {

            "new_ip": [],

            "new_rule": [],

            "new_domain": [],

            "new_user_agent": []

        }

        print(
            "===== REPORT DATA ====="
        )

        print(
            json.dumps(
                report_data,
                ensure_ascii=False,
                default=str,
                indent=2
            )
        )

        #
        # Prompt 생성
        #

        prompt = (
            PromptBuilder
            .build_waf_weekly_prompt(

                report_data=report_data,

                current_start="2026-10-05",

                current_end="2026-10-11"

            )
        )

        print(
            "===== PROMPT ====="
        )

        print(
            prompt
        )

        #
        # Bedrock 호출
        #

        #
        # CloudWatch 확인
        #

        return
