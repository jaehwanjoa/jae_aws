import re
import logging
import json

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
    Retrieve investigation detail and extract malware information.
    """

    fetcher = await get_fetcher(ctx)

    response = await fetcher.send_request(
        f"/xsoar/investigation/{incident_id}",
        method="POST",
        data={
            "pageSize": 100,
            "categories": [],
            "excludeScheduledEntries": True,
        },
        omit_papi_prefix=True,
    )


    logger.warning(
        "RESPONSE_KEYS=%s",
        list(response.keys())
    )

    logger.warning(
        "ENTRY_COUNT=%s",
        len(response.get("entries", []))
    )

    entries = response.get("entries", [])

    for idx, entry in enumerate(entries):
        logger.warning(
            "ENTRY_%s=%s",
            idx,
            json.dumps(
                entry,
                default=str,
                ensure_ascii=False
            )[:10000]
        )

    result = {
        "incident_id": incident_id,
    }

    for entry in entries:

        contents = str(
            entry.get("contents", "")
        )

        incident_type = None

        if (
            "Category Name | Malware" in contents
            or "| Category Name | Malware |" in contents
            or "Initiator SHA256" in contents
        ):

            incident_type = "MALWARE"

            fields = {
                "issue_name": r"\|Issue Name\|\s*(.*?)\s*\|",
                "severity": r"\|Severity\|\s*(.*?)\s*\|",
                "hostname": r"\| Hostname \|\s*(.*?)\s*\|",
                "container_name": r"\| Container Name \|\s*(.*?)\s*\|",
                "image_name": r"\| Image Name \|\s*(.*?)\s*\|",
                "sha256": r"\| Initiator SHA256 \|\s*(.*?)\s*\|",
                "user": r"\| User name \|\s*(.*?)\s*\|",
                "initiator": r"\| Initiated By \|\s*(.*?)\s*\|",
                "initiator_cmd": r"\| Initiator CMD \|\s*(.*?)\s*\|",
                "cluster_name": r"\| Cluster Name \|\s*(.*?)\s*\|",
                "namespace": r"\| Namespace \|\s*(.*?)\s*\|",
                "container_id": r"\| Container ID \|\s*(.*?)\s*\|",

                "account_id": r"\| Cloud Provider Account ID \|\s*(.*?)\s*\|",
                "asset_name": r"\| Cluster Name \|\s*(.*?)\s*\|",
                "file_name": r"\| CGO name \|\s*(.*?)\s*\|",
                "file_path": r"\| Initiator path \|\s*(.*?)\s*\|",
            }

        elif (
            "xdm.vulnerability.cve_id" in contents
            or "VULNERABILITY" in contents
        ):

            incident_type = "VULNERABILITY"

            fields = {
                "issue_name": r"\|Issue Name\|\s*(.*?)\s*\|",
                "severity": r"\|Severity\|\s*(.*?)\s*\|",
                "cve_id": r"\| xdm\.vulnerability\.cve_id \|\s*(.*?)\s*\|",
                "cvss_score": r"\| xdm\.vulnerability\.cvss_score \|\s*(.*?)\s*\|",
                "fix_versions": r"\| xdm\.vulnerability\.fix_versions \|\s*(.*?)\s*\|",
                "asset_id": r"\| Asset IDs \|\s*(.*?)\s*\|",
                "finding_id": r"\| Findings \|\s*(.*?)\s*\|",
                "remediation": r"\| Remediation \|\s*(.*?)\s*\|",
            }

        else:
            continue

        logger.warning(
            "INCIDENT_TYPE=%s",
            incident_type
        )

        logger.warning(
            "INCIDENT_TYPE=%s",
            incident_type
        )

        for field, pattern in fields.items():

            match = re.search(
                pattern,
                contents
            )

            if match:
                result[field] = (
                    match.group(1).strip()
                )

        result["incident_type"] = incident_type

        logger.warning(
            "RESULT_AFTER_PARSE=%s",
            json.dumps(
                result,
                ensure_ascii=False
            )
        )

        logger.warning(
            "RESULT_AFTER_PARSE=%s",
            json.dumps(
                result,
                ensure_ascii=False
            )
        )

        break

    return create_response(data=result)


class IncidentDetailModule(BaseModule):

    def register_tools(self):
        self._add_tool(get_incident_detail)

    def register_resources(self):
        pass

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)
