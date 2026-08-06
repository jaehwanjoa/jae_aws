import asyncio
import json

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
                    raise Exception(
                        str(start_result)
                    )

                query_execution_id = None

                for content in start_result.content:

                    if not hasattr(content, "text"):
                        continue

                    try:
                        data = json.loads(
                            content.text
                        )

                        if (
                            "query_execution_id"
                            in data
                        ):
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

                    status_result = (
                        await session.call_tool(
                            "manage_aws_athena_query_executions",
                            {
                                "operation":
                                    "get-query-execution",
                                "query_execution_id":
                                    query_execution_id
                            }
                        )
                    )

                    if status_result.is_error:
                        raise Exception(
                            str(status_result)
                        )

                    state = None
                    reason = None

                    for content in status_result.content:

                        if not hasattr(
                            content,
                            "text"
                        ):
                            continue

                        try:
                            data = json.loads(
                                content.text
                            )

                            query_execution = (
                                data.get(
                                    "query_execution",
                                    {}
                                )
                            )

                            status = (
                                query_execution.get(
                                    "Status",
                                    {}
                                )
                            )

                            state = status.get(
                                "State"
                            )

                            reason = status.get(
                                "StateChangeReason"
                            )

                        except Exception:
                            pass

                    if state == "SUCCEEDED":
                        break

                    if state in (
                        "FAILED",
                        "CANCELLED"
                    ):
                        raise Exception(
                            f"Athena Query {state}: {reason}"
                        )

                    await asyncio.sleep(2)

                result = await session.call_tool(
                    "manage_aws_athena_query_executions",
                    {
                        "operation":
                            "get-query-results",
                        "query_execution_id":
                            query_execution_id
                    }
                )

                if result.is_error:
                    raise Exception(
                        str(result)
                    )

                return result
