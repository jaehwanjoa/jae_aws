import asyncio
import json
import time

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)


class MCPExecutor:

    @classmethod
    def execute_athena(
        cls,
        query: str
    ):
        return asyncio.run(
            cls._execute_athena(query)
        )

    @classmethod
    async def _execute_athena(
        cls,
        query: str
    ):

        server_params = StdioServerParameters(
            command="uvx",
            args=[
                "awslabs.aws-dataprocessing-mcp-server@latest",
                "--allow-write",
                "--allow-sensitive-data-access"
            ],
            env={
                "AWS_REGION": "ap-northeast-2"
            }
        )

        async with stdio_client(server_params) as (
            read_stream,
            write_stream
        ):

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                start_result = await session.call_tool(
                    "manage_aws_athena_query_executions",
                    {
                        "operation": "start-query-execution",
                        "query_string": query,
                        "query_execution_context": {
                            "Database": "jaehwan-aws-waf"
                        },
                        "work_group": "jaehwan"
                    }
                )

                if start_result.is_error:
                    raise Exception(str(start_result))

                query_execution_id = None

                for content in start_result.content:

                    if hasattr(content, "text"):

                        try:
                            data = json.loads(content.text)

                            if "query_execution_id" in data:
                                query_execution_id = data[
                                    "query_execution_id"
                                ]
                                break

                        except Exception:
                            pass

                if not query_execution_id:
                    raise Exception(
                        f"QueryExecutionId not found: {start_result}"
                    )

                while True:

                    status_result = await session.call_tool(
                        "manage_aws_athena_query_executions",
                        {
                        
