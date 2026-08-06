from orchestrator.planner import Planner
from orchestrator.tool_mapping import get_mapping
from orchestrator.table_catalog import TABLE_CATALOG
from orchestrator.athena_query_generator import (
    AthenaQueryGenerator
)

from mcp_tools.mcp_executor import MCPExecutor

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

            import traceback

            print("ERROR_TYPE =", type(e))
            print("ERROR_REPR =", repr(e))
            print("TRACEBACK =")
            print(traceback.format_exc())

            return {
                "request_id": request_id,
                "status": "error",
                "message": str(e)
            }
