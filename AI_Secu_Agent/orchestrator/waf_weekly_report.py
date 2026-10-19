import json

from datetime import (
    datetime,
    timedelta
)

from agent.prompt_builder import (
    PromptBuilder
)

from mcp_tools.athena_client import (
    AthenaClient
)

from orchestrator.waf_weekly_queries import (
    WAFWeeklyQueries
)

from collections import Counter

class WAFWeeklyReport:

    TABLES = {

        "cloudfront_waf":
            "ons_cjl_am2",

        "regional_waf":
            "ons_cjl_ue1"

    }

    @staticmethod
    def build_summary(
        current_rows,
        previous_rows
    ):
    
        current_ips = {
            r.get("source_ip")
            for r in current_rows
            if r.get("source_ip")
        }
    
        previous_ips = {
            r.get("source_ip")
            for r in previous_rows
            if r.get("source_ip")
        }
    
        current_rules = {
            r.get("rule_id")
            for r in current_rows
            if r.get("rule_id")
        }
    
        previous_rules = {
            r.get("rule_id")
            for r in previous_rows
            if r.get("rule_id")
        }
    
        current_domains = {
            r.get("host_domain")
            for r in current_rows
            if r.get("host_domain")
        }
    
        previous_domains = {
            r.get("host_domain")
            for r in previous_rows
            if r.get("host_domain")
        }
    
        current_ua = {
            r.get("user_agent")
            for r in current_rows
            if r.get("user_agent")
        }
    
        previous_ua = {
            r.get("user_agent")
            for r in previous_rows
            if r.get("user_agent")
        }
    
        new_ips = current_ips - previous_ips
        new_rules = current_rules - previous_rules
        new_domains = current_domains - previous_domains
        new_user_agents = current_ua - previous_ua
    
        ip_counter = Counter()
        rule_counter = Counter()
        domain_counter = Counter()
        ua_counter = Counter()
    
        for row in current_rows:
    
            ip = row.get("source_ip")
            rule = row.get("rule_id")
            domain = row.get("host_domain")
            ua = row.get("user_agent")
    
            if ip in new_ips:
                ip_counter[ip] += 1
    
            if rule in new_rules:
                rule_counter[rule] += 1
    
            if domain in new_domains:
                domain_counter[domain] += 1
    
            if ua in new_user_agents:
                ua_counter[ua] += 1
    
        return {
            "new_ip": ip_counter.most_common(10),
            "new_rule": rule_counter.most_common(10),
            "new_domain": domain_counter.most_common(10),
            "new_user_agent": ua_counter.most_common(10)
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
        
            try:
        
                current_query = (
                    WAFWeeklyQueries
                    .get_weekly_query(
                        table_name,
                        current_start,
                        current_end
                    )
                )
        
                previous_query = (
                    WAFWeeklyQueries
                    .get_weekly_query(
                        table_name,
                        previous_start,
                        previous_end
                    )
                )
        
                print(
                    f"===== {waf_type} CURRENT QUERY ====="
                )
        
                current_result = (
                    AthenaClient.query(
                        database="jaehwan-aws-waf",
                        query=current_query
                    )
                )
        
                print(
                    f"===== {waf_type} PREVIOUS QUERY ====="
                )
        
                previous_result = (
                    AthenaClient.query(
                        database="jaehwan-aws-waf",
                        query=previous_query
                    )
                )
        
                report_data[waf_type] = (
                    cls.build_summary(
                        current_result,
                        previous_result
                    )
                )
        
                print(
                    f"===== {waf_type} SUMMARY ====="
                )
        
                print(
                    json.dumps(
                        report_data[waf_type],
                        ensure_ascii=False,
                        indent=2
                    )
                )
        
            except Exception as e:
        
                print(
                    f"{waf_type} ERROR"
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
