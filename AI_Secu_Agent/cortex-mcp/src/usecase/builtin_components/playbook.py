from typing import Annotated, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from usecase.base_module import BaseModule
from usecase.builtin_components._zip_artifact_fetcher import ZipArtifactFetcher

# Filenames inside a Cortex playbook ZIP that the LLM rarely needs.
# ``metadata.json`` is the content-pack wrapper; carries packID, packName,
# tags, integrations, etc. for marketplace items and is fully empty /
# zeroed for user-authored playbooks. Drop it by default to keep responses
# small and focused on the playbook YAML itself.
_PLAYBOOK_METADATA_FILENAMES: frozenset[str] = frozenset({"metadata.json"})


async def get_playbook(
    ctx: Context,
    identifier: Annotated[
        str,
        Field(
            description=(
                "Playbook display name (e.g. 'Investigation - Suspicious Login') "
                "or playbook UUID (e.g. '3662cb1f-21a8-47bf-8ffb-6a7d2a52abe0'). "
                "The tool will automatically pick the right Cortex filter field "
                "unless identifier_type is set explicitly."
            )
        ),
    ],
    identifier_type: Annotated[
        Literal["auto", "id", "name"],
        Field(
            description=(
                "Whether to look up by 'id' (UUID) or 'name' (display name). "
                "'auto' (default) sends 'id' when the identifier matches the UUID "
                "format, otherwise 'name'. Set explicitly only when the auto "
                "detection misroutes (e.g. a playbook whose name happens to be a "
                "valid UUID string)."
            ),
            default="auto",
        ),
    ] = "auto",
    include_metadata: Annotated[
        bool,
        Field(
            description=(
                "When True, includes the ``metadata.json`` content-pack wrapper "
                "in the response. This file carries packID, packName, tags, "
                "integrations, and similar marketplace metadata. For user-authored "
                "playbooks it is usually empty. Defaults to False to keep "
                "responses focused on the playbook YAML."
            ),
            default=False,
        ),
    ] = False,
) -> str:
    """
    Retrieve a playbook from Cortex by display name or UUID.

    Cortex returns the playbook as a ZIP archive containing one or more YAML /
    JSON files. This tool downloads the archive in-memory, parses each
    YAML/JSON entry into a structured object, and returns the parsed contents
    so the LLM can read and analyze the playbook directly.

    Use this tool to:
        - Inspect or summarize what a playbook does.
        - Find which integrations / commands a playbook uses.
        - Compare playbook versions or extract specific tasks.
        - Audit playbooks for compliance or security review.

    Args:
        ctx: The FastMCP context.
        identifier: Playbook display name or UUID.
        identifier_type: 'auto', 'id', or 'name'. Defaults to 'auto'.
        include_metadata: When True, includes ``metadata.json`` in the
            response. Defaults to False.

    Returns:
        JSON-encoded object containing ``size_bytes``, ``files``,
        ``skipped_files``, ``filter_used``, and ``success``. By default
        the ``metadata.json`` content-pack wrapper is omitted from
        ``files`` and listed in ``skipped_files``; see
        :class:`ZipArtifactFetcher` for the full schema.
    """
    ignored = frozenset() if include_metadata else _PLAYBOOK_METADATA_FILENAMES
    return await ZipArtifactFetcher(
        endpoint="playbooks/get",
        item_kind="playbook",
        ignored_filenames=ignored,
    ).fetch(
        ctx,
        identifier=identifier,
        identifier_type=identifier_type,
    )


class PlaybookModule(BaseModule):
    """
    Module for retrieving Cortex playbooks.

    Cortex's ``/public_api/v1/playbooks/get`` endpoint returns a ZIP archive
    containing the playbook YAML (and sometimes auxiliary JSON / binary
    entries). The download / extract / parse pipeline is shared with the
    script tool via :class:`ZipArtifactFetcher`.

    Tools provided:
        - get_playbook: fetch a single playbook by display name or UUID.
    """

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)

    def register_tools(self):
        self._add_tool(get_playbook)

    def register_resources(self):
        # No static resources for this module.
        pass
