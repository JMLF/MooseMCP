"""JSON-RPC client for communicating with the Moose server.

This module provides a thin wrapper around the HTTP/JSON-RPC transport
used by the Moose (Pharo) backend.  All MCP tool implementations in
``mooseMCPServer.py`` delegate their work to :func:`callMooseServer`.

Configuration
-------------
The default server URL is ``http://localhost:4444/``.  It can be
overridden at runtime by calling :func:`configure` before the first
tool call, or simply by setting :data:`MOOSE_URL` directly.
"""

import json
import logging

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server configuration
# ---------------------------------------------------------------------------

#: URL of the Moose JSON-RPC server.
MOOSE_URL: str = "http://localhost:4444/"

#: HTTP headers sent with every request.
MOOSE_HEADERS: dict = {"content-type": "application/json"}


def configure(url: str, headers: dict | None = None) -> None:
    """Override the default Moose server connection parameters.

    Args:
        url: Full URL of the Moose JSON-RPC endpoint
             (e.g. ``"http://localhost:4444/"``).
        headers: Optional dict of HTTP headers.  When omitted the
                 default ``Content-Type: application/json`` header is
                 kept unchanged.
    """
    global MOOSE_URL, MOOSE_HEADERS
    MOOSE_URL = url
    if headers is not None:
        MOOSE_HEADERS = headers


# ---------------------------------------------------------------------------
# RPC helper
# ---------------------------------------------------------------------------

def callMooseServer(command: str, args: list[object]):
    """Send a JSON-RPC 2.0 request to the Moose server and return its result.

    Args:
        command: JSON-RPC method name (e.g. ``"list:entitiesForType"``).
        args: Positional parameters forwarded as the ``params`` array.

    Returns:
        The ``result`` field from the JSON-RPC response.

    Raises:
        requests.RequestException: On any HTTP-level error.
        KeyError: If the server response does not contain a ``result`` field
                  (i.e. the server returned a JSON-RPC error object).
    """
    logger.debug("call MooseServer: %s(%s)", command, args)

    payload = {
        "method": command,
        "params": args,
        "jsonrpc": "2.0",
        "id": 1,
    }

    response = requests.post(
        MOOSE_URL, data=json.dumps(payload), headers=MOOSE_HEADERS
    ).json()

    logger.debug("MooseServer answer: %s", response)

    return response["result"]
