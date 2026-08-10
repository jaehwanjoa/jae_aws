from typing import Annotated, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from usecase.base_module import BaseModule
from usecase.builtin_components._zip_artifact_fetcher import ZipArtifactFetcher

# Filenames inside a Cortex script ZIP that the LLM rarely needs.
# ``metadata.json`` is the content-pack wrapper; carries packID, packName,
# tags, integrations, etc. for marketplace items and is fully empty /
# zeroed for user-authored scripts. Drop it by default to keep responses
# small and focused on the script source itself.
_SCRIPT_METADATA_FILENAMES: frozenset[str] = frozenset({"metadata.json"})


async def get_script(
    ctx: Context,
    identifier: Annotated[
        str,
        Field(
            description=(
                "Script display name (e.g. 'CommonServerPython') or script UUID "
                "(e.g. '652ce32a-167f-48df-8ac5-a43bcacae562'). The tool will "
                "automatically pick the right Cortex filter field unless "
                "identifier_type is set explicitly."
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
                "detection misroutes (e.g. a script whose name happens to be a "
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
                "scripts it is usually empty. Defaults to False to keep "
                "responses focused on the script source."
            ),
            default=False,
        ),
    ] = False,
) -> str:
    """
    Retrieve a script from Cortex by display name or UUID.

    Cortex returns the script as a ZIP archive containing one or more YAML /
    JSON files (the script source plus optional pack metadata). This tool
    downloads the archive in-memory, parses each YAML/JSON entry into a
    structured object, and returns the parsed contents so the LLM can read
    and analyze the script directly.

    Use this tool to:
        - Inspect or summarize what a script does.
        - Find which Cortex / Demisto commands a script invokes.
        - Compare script versions or read its argument / output schema.
        - Audit scripts for compliance or security review.

    Args:
        ctx: The FastMCP context.
        identifier: Script display name or UUID.
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
    ignored = frozenset() if include_metadata else _SCRIPT_METADATA_FILENAMES
    return await ZipArtifactFetcher(
        endpoint="scripts/get",
        item_kind="script",
        ignored_filenames=ignored,
    ).fetch(
        ctx,
        identifier=identifier,
        identifier_type=identifier_type,
    )


class ScriptModule(BaseModule):
    """
    Module for retrieving Cortex scripts (automations).

    Cortex's ``/public_api/v1/scripts/get`` endpoint returns a ZIP archive
    containing the script's YAML definition (and sometimes auxiliary JSON
    entries). The download / extract / parse pipeline is shared with the
    playbook tool via :class:`ZipArtifactFetcher`.

    Tools provided:
        - get_script: fetch a single script by display name or UUID.
    """

    def __init__(self, mcp: FastMCP):
        super().__init__(mcp)

    def register_tools(self):
        self._add_tool(get_script)

    def register_resources(self):
        # No static resources for this module.
        pass
