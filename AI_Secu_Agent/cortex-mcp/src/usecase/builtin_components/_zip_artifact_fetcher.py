"""
Reusable downloader for Cortex endpoints that return their content as a ZIP
archive containing one or more YAML / JSON files.

The two current consumers are:
    - :mod:`usecase.builtin_components.playbook` (POST /playbooks/get)
    - :mod:`usecase.builtin_components.script`   (POST /scripts/get)

The endpoints share an identical request envelope, response Content-Type
quirk, identifier-routing rule, and error-handling shape. This module
encapsulates all of that so per-tool modules can stay thin shells whose
only job is to provide the LLM-facing tool name, docstring, parameter
descriptions, and the endpoint-specific configuration.

The leading underscore in the filename signals that this is internal
helper code; it is intentionally NOT a :class:`BaseModule` subclass, so
the auto-discovery loop in :mod:`usecase.module_util` skips it during
tool registration.
"""

import io
import json
import logging
import os
import uuid
import zipfile

import yaml
from fastmcp import Context

from entities.exceptions import (
    PAPIAuthenticationError,
    PAPIClientError,
    PAPIClientRequestError,
    PAPIConnectionError,
    PAPIResponseError,
    PAPIServerError,
)
from pkg.util import create_response
from usecase.fetcher import get_fetcher

logger = logging.getLogger(__name__)


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _parse_zip_to_dict(
    zip_bytes: bytes,
    ignored_filenames: frozenset[str] = frozenset(),
) -> tuple[dict[str, dict | list], list[str], int]:
    """
    Parse an in-memory ZIP archive whose entries are YAML / JSON content.

    Each entry whose name ends in ``.yml`` / ``.yaml`` is parsed via
    :func:`yaml.safe_load`; each entry ending in ``.json`` is parsed via
    :func:`json.loads`. Any other entry (images, binary blobs, etc.) is
    skipped and its name returned for transparency.

    Entries whose basename (lowercased) appears in ``ignored_filenames``
    are omitted from the parsed result and listed in ``skipped`` instead.
    The default empty set means no entries are ignored.

    Args:
        zip_bytes: Raw bytes of the ZIP archive.
        ignored_filenames: Lowercased basenames to exclude from the parsed
            output. Defaults to an empty set (ignore nothing).

    Returns:
        Tuple of (parsed_files, skipped_names, total_byte_length).

    Raises:
        zipfile.BadZipFile: If ``zip_bytes`` is not a valid ZIP archive.
    """
    parsed: dict[str, dict | list] = {}
    skipped: list[str] = []
    total_bytes = len(zip_bytes)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            lower = name.lower()
            # Use basename so nested entries (e.g. subdir/metadata.json)
            # are also caught by the ignore-list.
            basename = os.path.basename(lower)
            if basename in ignored_filenames:
                skipped.append(name)
                continue
            try:
                raw = zf.read(name)
                if lower.endswith((".yml", ".yaml")):
                    parsed[name] = yaml.safe_load(raw.decode("utf-8"))
                elif lower.endswith(".json"):
                    parsed[name] = json.loads(raw.decode("utf-8"))
                else:
                    skipped.append(name)
            except Exception as e:  # record any per-entry failure as skipped
                logger.warning("Failed to parse ZIP entry %r: %s", name, e)
                skipped.append(name)

    return parsed, skipped, total_bytes


class ZipArtifactFetcher:
    """
    Encapsulates the download-stream-parse pipeline for Cortex endpoints
    that return ZIP archives containing YAML / JSON content.

    Responsibilities:
        - Decide whether to send the Cortex ``filter.field`` as ``id`` or
          ``name`` based on the identifier shape (UUID vs everything else).
        - Pre-serialize the request body (httpx's ``content`` parameter
          rejects dicts on the streaming path).
        - Override the request ``Content-Type`` header to
          ``application/json`` (PAPIClient.stream defaults to
          ``application/zip`` which Cortex rejects with HTTP 415).
        - Stream the response, extract YAML/JSON entries in-memory via
          :func:`pkg.util.parse_zip_to_dict`, and wrap the result with
          :func:`pkg.util.create_response`.
        - Translate the full ``PAPI*Error`` family into structured error
          responses so the LLM receives a JSON payload rather than a
          stack trace.

    Per-tool customization is limited to the constructor: the endpoint
    URL fragment and a human-readable noun for log messages and error
    text (e.g. ``"playbook"`` / ``"script"``).
    """

    def __init__(
        self,
        *,
        endpoint: str,
        item_kind: str,
        ignored_filenames: frozenset[str] = frozenset(),
    ) -> None:
        """
        Args:
            endpoint: Cortex endpoint relative to ``/public_api/v1`` (e.g.
                ``"playbooks/get"`` or ``"scripts/get"``). Forwarded to
                :meth:`Fetcher.send_request` which prepends the API prefix.
            item_kind: Singular noun for the artifact (``"playbook"`` /
                ``"script"``). Used only in log messages and error text;
                does not affect the wire request.
            ignored_filenames: Lowercased basenames to omit from the parsed
                output. Each calling tool decides what's noise for its own
                use case (e.g. ``frozenset({"metadata.json"})`` to drop
                Cortex content-pack wrappers). Defaults to an empty set
                (no filtering). To bypass for a single call, construct a
                fresh fetcher with the default empty set.
        """
        self.endpoint = endpoint
        self.item_kind = item_kind
        self.ignored_filenames = ignored_filenames

    @staticmethod
    def resolve_filter_field(identifier: str, identifier_type: str) -> str:
        """
        Decide whether to send ``filter.field = "id"`` or ``"name"``.

        ``identifier_type`` may be ``"id"`` or ``"name"`` (used verbatim) or
        ``"auto"`` (UUID -> ``"id"``, otherwise ``"name"``).
        """
        if identifier_type == "auto":
            return "id" if _is_uuid(identifier) else "name"
        return identifier_type

    async def fetch(
        self,
        ctx: Context,
        *,
        identifier: str,
        identifier_type: str = "auto",
    ) -> str:
        """
        Download, parse, and JSON-wrap the Cortex artifact identified by
        ``identifier``.

        Args:
            ctx: FastMCP request context (provides authenticated fetcher).
            identifier: Display name or UUID of the artifact.
            identifier_type: ``"auto"`` (default), ``"id"``, or ``"name"``.

        Returns:
            JSON-encoded response (already wrapped via :func:`create_response`).
            On success, contains: ``size_bytes``, ``files``, ``skipped_files``,
            ``filter_used``, ``success: "true"``. On any handled failure,
            contains ``error`` and ``success: "false"``.

            Files whose basenames appear in :attr:`ignored_filenames` are
            listed in ``skipped_files`` rather than ``files``.
        """
        chosen_field = self.resolve_filter_field(identifier, identifier_type)

        payload = {
            "request_data": {
                "filter": {
                    "field": chosen_field,
                    "value": identifier,
                }
            }
        }

        try:
            fetcher = await get_fetcher(ctx)
            # Two non-obvious requirements for the streaming path:
            #   1. ``data`` is forwarded to httpx as ``content=`` by
            #      PAPIClient.stream, which only accepts bytes / str /
            #      iterables. Pre-serialize the dict so it arrives as a
            #      string.
            #   2. PAPIClient.stream's default Content-Type is
            #      ``application/zip`` (intended for the response), but
            #      Cortex rejects anything other than ``application/json``
            #      on the request side with HTTP 415. Override explicitly.
            response = await fetcher.send_request(
                self.endpoint,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                stream=True,
            )
            zip_bytes = response.read()

            if not zip_bytes:
                return create_response(
                    {
                        "error": (
                            f"Empty response from Cortex for {self.item_kind} "
                            f"{identifier!r}"
                        )
                    },
                    is_error=True,
                )

            try:
                parsed, skipped, total_bytes = _parse_zip_to_dict(
                    zip_bytes,
                    ignored_filenames=self.ignored_filenames,
                )
            except zipfile.BadZipFile as e:
                return create_response(
                    {"error": f"Cortex response was not a valid ZIP archive: {e}"},
                    is_error=True,
                )

            if not parsed:
                return create_response(
                    {
                        "error": (
                            f"No YAML or JSON files found in the {self.item_kind} ZIP"
                        ),
                        "skipped_files": skipped,
                        "size_bytes": total_bytes,
                    },
                    is_error=True,
                )

            return create_response(
                {
                    "size_bytes": total_bytes,
                    "files": parsed,
                    "skipped_files": skipped,
                    "filter_used": chosen_field,
                }
            )

        except (
            PAPIConnectionError,
            PAPIAuthenticationError,
            PAPIServerError,
            PAPIClientRequestError,
            PAPIResponseError,
            PAPIClientError,
        ) as e:
            logger.exception(
                "PAPI error while getting %s %s: %s", self.item_kind, identifier, e
            )
            return create_response({"error": str(e)}, is_error=True)
        except Exception as e:  # noqa: BLE001 - mirror cases/issues broad-catch
            logger.exception(
                "Failed to get %s %s: %s", self.item_kind, identifier, e
            )
            return create_response({"error": str(e)}, is_error=True)
