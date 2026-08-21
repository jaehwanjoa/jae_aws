from fastmcp import Context, FastMCP

from usecase.base_module import BaseModule
from usecase.fetcher import get_fetcher


async def get_wildfire_verdict(
    ctx: Context,
    hashes: list[str]
) -> str:

    artifact_hash = hashes[0]

    print(f"WF_HASH={artifact_hash}")

    fetcher = await get_fetcher(ctx)

    response = await fetcher.send_request(
        f"/api/webapp/wildfire/get_report_data/?artifact_hash={artifact_hash}",
        data={}
    )

    return str(response)


class WildFireModule(BaseModule):

    def register_tools(self):
        self._add_tool(get_wildfire_verdict)

    def register_resources(self):
        pass

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
