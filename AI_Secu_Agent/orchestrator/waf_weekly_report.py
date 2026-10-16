import json

from datetime import (
    datetime,
    timedelta
)

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

        today = datetime.utcnow().date()

        current_end = (
            today
            - timedelta(
                days=today.weekday() + 1
            )
        )

        current_start = (
            current_end
            - timedelta(days=6)
        )

        previous_end = (
            current_start
            - timedelta(days=1)
        )

        previous_start = (
            previous_end
            - timedelta(days=6)
        )

        print(
            f"CURRENT={current_start} ~ {current_end}"
        )

        print(
            f"PREVIOUS={previous_start} ~ {previous_end}"
        )

        #
        # Athena 결과 자리
        #

        report_data = {

            "cloudfront_waf": {

                "new_ip": [],
                "new_rule": [],
                "new_domain": [],
                "new_user_agent": []

            },

            "regional_waf": {

                "new_ip": [],
                "new_rule": [],
                "new_domain": [],
                "new_user_agent": []

            }

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

                current_start=str(
                    current_start
                ),

                current_end=str(
                    current_end
                )

            )
        )

        print(
            "===== PROMPT ====="
        )

        print(
            prompt
        )

        #
        # 다음 단계
        # Athena 연결
        #

        return
