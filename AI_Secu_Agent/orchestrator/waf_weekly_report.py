import json

from datetime import (
    datetime,
    timedelta
)

from prompt_builder import (
    PromptBuilder
)

from mcp_tools.athena_client import (
    AthenaClient
)

from orchestrator.waf_weekly_queries import (
    WAFWeeklyQueries
)


class WAFWeeklyReport:

    TABLES = {

        "cloudfront_waf":
            "ons_cjl_am2",

        "regional_waf":
            "ons_cjl_ue1"

    }

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
        # 결과 저장
        #

        report_data = {}

        #
        # CloudFront / Regional 분리 처리
        #

        for waf_type, table_name in (
            cls.TABLES.items()
        ):

            print(
                f"PROCESS={waf_type}"
            )

            print(
                f"TABLE={table_name}"
            )

            report_data[waf_type] = {

                "new_ip": [],

                "new_rule": [],

                "new_domain": [],

                "new_user_agent": []

            }

            #
            # 신규 IP
            #

            ip_query = (
                WAFWeeklyQueries
                .get_new_ip_query(

                    table_name,

                    current_start,

                    current_end,

                    previous_start,

                    previous_end

                )
            )

            print(
                f"===== {waf_type} NEW IP QUERY ====="
            )

            print(
                ip_query
            )

            try:

                ip_result = (
                    AthenaClient.run_query(
                        query=ip_query
                    )
                )

                report_data[waf_type][
                    "new_ip"
                ] = ip_result

                print(
                    f"===== {waf_type} NEW IP RESULT ====="
                )

                print(
                    json.dumps(
                        ip_result,
                        ensure_ascii=False,
                        default=str
                    )
                )

            except Exception as e:

                print(
                    f"{waf_type} NEW IP ERROR"
                )

                print(
                    str(e)
                )

        #
        # 최종 데이터 출력
        #

        print(
            "===== REPORT DATA ====="
        )

        print(
            json.dumps(
                report_data,
                ensure_ascii=False,
                indent=2,
                default=str
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
        # Bedrock 연결 예정
        #

        return
