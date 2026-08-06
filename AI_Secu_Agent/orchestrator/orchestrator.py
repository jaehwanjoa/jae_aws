from planner import Planner
from tool_mapping import get_mapping
from mcp_executor import MCPExecutor
from table_catalog import TABLE_CATALOG
from athena_query_generator import (
    AthenaQueryGenerator
)

import uuid


class Orchestrator:

    @classmethod
    def process(
        cls,
        question: str,
        customer: str
    ):

        request_id = str(
            uuid.uuid4()
        )

        try:
            
            table_meta = TABLE_CATALOG.get(
                customer
            )
            
            if not table_meta:
            
                raise ValueError(
                    f"Unknown customer: {customer}"
                )
            
            database = table_meta[
                "database"
            ]
            
            table_name = table_meta[
                "table_name"
            ]            
 
            # 1. Planner
            plan = Planner.parse(
                question
            )

            # 2. Intent Mapping
            mapping = get_mapping(
                plan["intent"]
            )

            # 3. 쿼리 생성
            query = AthenaQueryGenerator.build(
                plan=plan,
                mapping=mapping,
                table_name=table_name
            )

            # 4. MCP 실행
            athena_result = (
                MCPExecutor.execute_athena(
                    query=query
                )
            )
            
            return {
                "request_id": request_id,
                "status": "success",
            
                "customer":
                    customer,
            
                "database":
                    database,
            
                "table_name":
                    table_name,
            
                "intent":
                    plan["intent"],
            
                "query_type":
                    mapping["query_type"],
            
                "plan":
                    plan,
            
                "query":
                    query,
            
                "athena_result":
                    athena_result
            }

        except Exception as e:

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
