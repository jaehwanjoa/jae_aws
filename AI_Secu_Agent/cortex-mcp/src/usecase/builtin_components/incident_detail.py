import re
import logging

from fastmcp import Context, FastMCP

from pkg.util import create_response
from usecase.base_module import BaseModule
from usecase.fetcher import get_fetcher

logger = logging.getLogger(__name__)


async def get_incident_detail(
    ctx: Context,
    incident_id: str,
) -> str:
    """
    Retrieve incident detail and extract malware information.
    """

    fetcher = await get_fetcher(ctx)

    print(f"INVESTIGATION_REQUEST={incident_id}")

    response = await fetcher.send_request(
        f"/xsoar/investigation/{incident_id}",
        method="POST",
        body={
            "pageSize": 100,
            "categories": [],
            "excludeScheduledEntries": True,
        },
        omit_papi_prefix=True,
    )

    print(f"ENTRY_COUNT={len(response.get('entries', []))}")

    result = {
        "incident_id": incident_id,
    }

    entries = response.get("entries", [])

    for entry in entries:
        contents = entry.get("contents", "")

        if "xdm.file.sha256" not in contents:
            continue

        fields = {
            "issue_name": r"\|Issue Name\|\s*(.*?)\s*\|",
            "severity": r"\|Severity\|\s*(.*?)\s*\|",
            "sha256": r"\| xdm\.file\.sha256 \|\s*([a-f0-9]{64})\s*\|",
            "finding_id": r"\| Findings \|\s*(.*?)\s*\|",
            "verdict": r"\| xdm\.malware\.verdict \|\s*(.*?)\s*\|",
            "file_name": r"\| xdm\.file\.filename \|\s*(.*?)\s*\|",
            "file_path": r"\| xdm\.file\.path \|\s*(.*?)\s*\|",
            "asset_id": r"\| Asset IDs \|\s*(.*?)\s*\|",
            "detection_rule_id": r"\| Detection Rule ID \|\s*(.*?)\s*\|",
        }

        for field, pattern in fields.items():
            match = re.search(pattern, contents)
            if match:
                result[field] = match.group(1).strip()

        print(f"SHA256={result.get('sha256')}")
        break

    return create_response(data=result)


class IncidentDetailModule(BaseModule):

    def register_tools(self):
        self._add_tool(get_incident_detail)

    def register_resources(self):
        pass

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
