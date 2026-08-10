# cortex-mcp

A Python based integration for Cortex MCP (Model Context Protocol).

## Getting Started

### Prerequisites

- Python 3.13 or higher / container environment
- Cortex API credentials (Standard API key and API key ID)

### Installation

#### Option 1: Using Docker

Create a `.env` file with the following environment variables:
```
CORTEX_MCP_PAPI_URL=https://<your-tenant-url>
CORTEX_MCP_PAPI_AUTH_HEADER=<your_api_key>
CORTEX_MCP_PAPI_AUTH_ID=<your_api_key_id>
(optional - defaults to stdio)MCP_TRANSPORT=stdio/streamable-http
(optional, for streamable-http)MCP_HOST=0.0.0.0
(optional, for streamable-http)MCP_PORT=8080
(optional, for streamable-http)MCP_PATH=/api/v1/stream/mcp
```

Build the Docker image:

```bash
docker build -t cortex-mcp .
```

Run a quick test:

Run this command in your terminal. It starts the container, points it to your `.env` file, and stays open so you can see if it crashes or connects:

```bash
docker run -i --rm --env-file .env cortex-mcp
```

What to look for:

- **If it stays open and doesn't immediately spit out an error:** Success! It's waiting for MCP commands. You can stop it by pressing `Control + C`.
- **If you see "Unauthorized" or "401":** There is a typo in your `.env` file or the API key isn't active.
- **If you see "Connection Refused":** Check that your `CORTEX_MCP_PAPI_URL` is correct and includes the `https://`.

#### Option 2: Locally Using Poetry (Virtual Environment)

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install project dependencies:
```bash
poetry install
```

### Running the MCP Server

#### CLI
- See the [CLI](src/CLI_README.md) readme

#### Claude Desktop

-  Open the Claude configuration file (accessible from the `Developer` pane in Claude Desktop settings) and add the following MCP server configuration:


Docker Container:
```json
{
  "mcpServers": {
    "Cortex MCP Server": {
      "command": "docker",
      "args": [
        "run",
        "--env-file",
        "/path/to/.env",
        "-i",
        "--rm",
        "cortex-mcp"
      ]
    }
  }
}
```


Virtual Environment:
```json
{
  "mcpServers": {
    "Cortex MCP Server": {
      "command": "<path to cortex-mcp virtual environment>/bin/python",
      "args": [
        "<path to cortex-mcp>/src/main.py"
      ],
       "env": {
          "CORTEX_MCP_PAPI_URL": "https://<your-tenant-url>",
          "CORTEX_MCP_PAPI_AUTH_HEADER": "<your_api_key>", 
          "CORTEX_MCP_PAPI_AUTH_ID": "<your_api_key_id>",
          "MCP_TRANSPORT": "<stdio/streamable-http>"
   }
    }
  }
}
```


## Development

### Project Structure
```
src/
├── cli.py                           # Command line interface
├── main.py                          # Main application entry point
├── config/                          # Configuration modules
├── entities/                        # Data models and entity classes
├── pkg/                             # Internal package utilities and helpers
├── service/                         # Service layer implementations
└── usecase/                         # Business logic and use cases
    ├── builtin_components/          # MCP components that come with the package
    │   ├── openapi/
    │   └── python modules
    ├── custom_components/           # MCP components that are user-defined 
    │   ├── openapi/
    │   └── python modules
    └── remote_components/           # MCP components that are distributed and updated by Cortex** 
        ├── openapi/
        └── python modules

tests/
├── e2e/                             # End-to-end tests
└── individual test files
```
** When the user runs the [CLI](src/CLI_README.md) update command, any new or updated components provided by Cortex are automatically downloaded into the remote_components folder.
During each update, the folder is fully replaced and all existing contents are recreated.

Do not add custom tools to this directory, as it is managed entirely by Cortex and will be overwritten on every update.

### Adding custom MCP components

To add custom MCP components, follow this [guide](src/usecase/README.md).

### Coding

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black .
poetry run isort .
```

Debug:
The best way to debug MCP servers is with the [MCP inspector](https://github.com/modelcontextprotocol/inspector).
Aside from that, end-to-end tests can be run and added under `tests/e2e`.

## Troubleshooting / FAQ

### Tool calls return HTTP 500 "Value must be integer" (or similar) for numeric fields

**Symptom:** When the LLM invokes an OpenAPI-backed tool (e.g.
`get_audit_management_log`, `get_filtered_endpoints`, `get_vulnerabilities`,
`get_correlation_rules`) with numeric arguments such as `search_from`,
`search_to`, or epoch-millisecond timestamps, the call fails with a Cortex
error like `Value must be integer in epoch milliseconds`. Inspecting the
on-the-wire payload shows the value sent as a JSON float (e.g. `100.0`,
`1730419200000.0`) instead of an integer.

**Cause:** Some LLM clients send numeric arguments as floats even when the OpenAPI schema specifies `type: integer`.

**Workaround:** override `PAPIClient.send()` in your local checkout to
coerce whole-valued floats back to integers before the request leaves
the process. A reference implementation:

```python
# src/pkg/client.py 
import httpx
import json as _json


def _parse_float_preserve_int(s: str) -> float | int:
    """Return int when the JSON token is a whole number, float otherwise."""
    f = float(s)
    return int(f) if f.is_integer() else f


class PAPIClient(httpx.AsyncClient):
    # ... existing __init__ etc ...

    async def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type and request.content:
            try:
                original = request.content
                payload = _json.loads(original, parse_float=_parse_float_preserve_int)
                new_body = _json.dumps(payload).encode("utf-8")
                if new_body != original:
                    request._content = new_body                       # noqa: SLF001
                    request.stream = httpx._content.ByteStream(new_body)
                    request.headers["content-length"] = str(len(new_body))
            except (ValueError, _json.JSONDecodeError):
                pass
        return await super().send(request, **kwargs)
```
