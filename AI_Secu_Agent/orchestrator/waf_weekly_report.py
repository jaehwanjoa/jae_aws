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

class WAFWeeklyReport:

    TABLES = {

        "cloudfront_waf":
            "ons_cjl_am2",

        "regional_waf":
            "ons_cjl_ue1"

    }

    @staticmethod
    def build_new_ips(
        current_rows,
        previous_rows
    ):
    
        previous_ips = {
            r["source_ip"]
            for r in previous_rows
            if r.get("source_ip")
        }
    
        stats = {}
    
        for row in current_rows:
    
            ip = row.get("source_ip")
    
            if not ip:
                continue
    
            if ip in previous_ips:
                continue
    
            if ip not in stats:
    
                stats[ip] = {
                    "hit_count": 0,
                    "block_count": 0,
                    "count_count": 0,
                    "domains": set(),
                    "rules": set()
                }
    
            stats[ip]["hit_count"] += 1
    
            if row.get("action") == "BLOCK":
                stats[ip]["block_count"] += 1
    
            if row.get("action") == "COUNT":
                stats[ip]["count_count"] += 1
    
            if row.get("host_domain"):
                stats[ip]["domains"].add(
                    row["host_domain"]
                )
    
            if row.get("rule_id"):
                stats[ip]["rules"].add(
                    row["rule_id"]
                )
    
        result = []
    
        for ip, stat in stats.items():
    
            result.append({
                "ip": ip,
                "hit_count": stat["hit_count"],
                "block_count": stat["block_count"],
                "count_count": stat["count_count"],
                "domains": list(stat["domains"]),
                "rules": list(stat["rules"])
            })
    
        return sorted(
            result,
            key=lambda x: x["hit_count"],
            reverse=True
        )[:10]
        

    @staticmethod
    def build_new_domains(
        current_rows,
        previous_rows
    ):
    
        previous_domains = {
            r["host_domain"]
            for r in previous_rows
            if r.get("host_domain")
        }
    
        stats = {}
    
        for row in current_rows:
    
            domain = row.get(
                "host_domain"
            )
    
            if not domain:
                continue
    
            if domain in previous_domains:
                continue
    
            if domain not in stats:
    
                stats[domain] = {
                    "hit_count": 0,
                    "rules": {}
                }
    
            stats[domain]["hit_count"] += 1
    
            rule = row.get(
                "rule_id"
            )
    
            if rule:
    
                stats[domain]["rules"][
                    rule
                ] = (
                    stats[domain]["rules"]
                    .get(
                        rule,
                        0
                    )
                    + 1
                )
    
        results = []
    
        for domain, stat in stats.items():
    
            top_rule = None
    
            if stat["rules"]:
    
                top_rule = max(
                    stat["rules"],
                    key=stat["rules"].get
                )
    
            results.append({
                "domain": domain,
                "hit_count": stat["hit_count"],
                "top_rule": top_rule,
                "review_status": "UNKNOWN"
            })
    
        return sorted(
            results,
            key=lambda x: x["hit_count"],
            reverse=True
        )[:10]    

    @staticmethod
    def build_new_user_agents(
        current_rows,
        previous_rows
    ):
    
        previous_ua = {
            r["user_agent"]
            for r in previous_rows
            if r.get("user_agent")
        }
    
        stats = {}
    
        for row in current_rows:
    
            ua = row.get(
                "user_agent"
            )
    
            if not ua:
                continue
    
            if ua in previous_ua:
                continue
    
            if ua not in stats:
    
                stats[ua] = {
                    "request_count": 0,
                    "ips": {},
                    "domains": set()
                }
    
            stats[ua]["request_count"] += 1
    
            ip = row.get(
                "source_ip"
            )
    
            if ip:
    
                stats[ua]["ips"][ip] = (
                    stats[ua]["ips"]
                    .get(ip, 0)
                    + 1
                )
    
            domain = row.get(
                "host_domain"
            )
    
            if domain:
                stats[ua]["domains"].add(
                    domain
                )
    
        results = []
    
        for ua, stat in stats.items():
    
            top_ip = None
    
            if stat["ips"]:
    
                top_ip = max(
                    stat["ips"],
                    key=stat["ips"].get
                )
    
            results.append({
                "user_agent": ua,
                "request_count":
                    stat["request_count"],
                "ip_count":
                    len(
                        stat["ips"]
                    ),
                "top_ip":
                    top_ip,
                "domains":
                    list(
                        stat["domains"]
                    )
            })
    
        return sorted(
            results,
            key=lambda x: x["request_count"],
            reverse=True
        )[:10]
    
    @staticmethod
    def build_rule_growth(
        current_rows,
        previous_rows
    ):
    
        current_stats = {}
        previous_stats = {}
    
        for row in current_rows:
    
            rule = row.get("rule_id")
    
            if not rule:
                continue
    
            if rule not in current_stats:
    
                current_stats[rule] = {
                    "count": 0,
                    "block_count": 0,
                    "count_count": 0
                }
    
            current_stats[rule]["count"] += 1
    
            if row.get("action") == "BLOCK":
                current_stats[rule]["block_count"] += 1
    
            elif row.get("action") == "COUNT":
                current_stats[rule]["count_count"] += 1
    
        for row in previous_rows:
    
            rule = row.get("rule_id")
    
            if not rule:
                continue
    
            previous_stats[rule] = (
                previous_stats.get(
                    rule,
                    0
                )
                + 1
            )
    
        results = []
    
        for rule, stat in current_stats.items():
    
            current_count = stat["count"]
    
            previous_count = previous_stats.get(
                rule,
                0
            )
    
            increase = (
                current_count
                - previous_count
            )
    
            increase_rate = 100
    
            if previous_count > 0:
    
                increase_rate = round(
                    (
                        increase
                        /
                        previous_count
                    )
                    * 100,
                    2
                )
    
            results.append({
                "rule_id": rule,
                "current_count": current_count,
                "previous_count": previous_count,
                "increase": increase,
                "increase_rate": increase_rate,
                "block_count": stat["block_count"],
                "count_count": stat["count_count"]
            })
    
        return sorted(
            results,
            key=lambda x: x["increase"],
            reverse=True
        )[:10]
    
    @classmethod
    def build_summary(
        cls,
        current_rows,
        previous_rows
    ):
    
        return {
    
            "new_ip":
                cls.build_new_ips(
                    current_rows,
                    previous_rows
                ),
    
            "top_rule":
                cls.build_rule_growth(
                    current_rows,
                    previous_rows
                ),
    
            "new_domain":
                cls.build_new_domains(
                    current_rows,
                    previous_rows
                ),
    
            "new_user_agent":
                cls.build_new_user_agents(
                    current_rows,
                    previous_rows
                )
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
                "top_rule": [],
                "new_domain": [],
                "new_user_agent": []
            }
        
            try:
        
                current_query = (
                    WAFWeeklyQueries
                    .get_weekly_summary_query(
                        table_name,
                        current_start,
                        current_end
                    )
                )
        
                previous_query = (
                    WAFWeeklyQueries
                    .get_weekly_summary_query(
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
