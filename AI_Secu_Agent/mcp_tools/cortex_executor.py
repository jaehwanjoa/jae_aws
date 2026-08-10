import os
import asyncio

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters
)

class CortexExecutor:

    @classmethod
    def execute(
        cls,
        tool_name,
        arguments
    ):
        return asyncio.run(
            cls._execute(
                tool_name,
                arguments
            )
        )

    @classmethod
    async def _execute(
        cls,
        tool_name,
        arguments
    ):

        server_params = StdioServerParameters(
            command="python",
            args=[
                "/var/task/cortex-mcp/src/main.py"
            ],
            env=dict(os.environ)
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

                result = await session.call_tool(
                    tool_name,
                    arguments
                )

                return result
