"""Standalone MCP server providing basic mathematical operations.

This server can be registered alongside :mod:`mooseMCPServer` in any
MCP-capable LLM client to give the LLM the ability to perform simple
arithmetic and comparisons without relying on its own internal
calculations.

Usage::

    python mathServer.py
"""

import logging

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server & logging setup
# ---------------------------------------------------------------------------

mcp = FastMCP(name="MooseMCPServer")

logging.basicConfig(filename="mooseMCP.log", level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# T O O L S
# ----------------------------------------------------------------------------

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum ``a + b``.
    """
    logger.info("mathServer: %s + %s", a, b)
    return a + b


@mcp.tool()
def substract(a: float, b: float) -> float:
    """Subtract one number from another.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference ``a - b``.
    """
    logger.info("mathServer: %s - %s", a, b)
    return a - b


@mcp.tool()
def greaterThan(a: float, b: float) -> bool:
    """Compare two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        ``True`` if ``a`` is strictly greater than ``b``, ``False`` otherwise.
    """
    logger.info("mathServer: %s > %s", a, b)
    return a > b


# ----------------------------------------------------------------------------
# E N T R Y   P O I N T
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
