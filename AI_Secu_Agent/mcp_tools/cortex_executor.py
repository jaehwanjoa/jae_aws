import os
import asyncio
import time

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
        start = time.time()

        result = asyncio.run(
            cls._execute(
                tool_name,
                arguments
            )
        )

        print(
            f"MCP_EXECUTE_TIME={time.time() - start:.2f}s TOOL={tool_name}"
        )

        return result

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

    @classmethod
    async def create_session(cls):

        server_params = StdioServerParameters(
            command="python",
            args=[
                "/var/task/cortex-mcp/src/main.py"
            ],
            env=dict(os.environ)
        )

        stdio_ctx = stdio_client(server_params)

        read_stream, write_stream = (
            await stdio_ctx.__aenter__()
        )

        session = ClientSession(
            read_stream,
            write_stream
        )

        await session.__aenter__()
        await session.initialize()

        return (
            session,
            stdio_ctx
        )

    @classmethod
    async def call_tool(
        cls,
        session,
        tool_name,
        arguments
    ):
        return await session.call_tool(
            tool_name,
            arguments
        )


    @classmethod
    async def open_session(cls):

        server_params = StdioServerParameters(
            command="python",
            args=[
                "/var/task/cortex-mcp/src/main.py"
            ],
            env=dict(os.environ)
        )

        ctx = stdio_client(server_params)

        read_stream, write_stream = (
            await ctx.__aenter__()
        )

        session = ClientSession(
            read_stream,
            write_stream
        )

        await session.__aenter__()
        await session.initialize()

        return session, ctx


    @classmethod
    async def call_tool(
        cls,
        session,
        tool_name,
        arguments
    ):
        return await session.call_tool(
            tool_name,
            arguments
        )

