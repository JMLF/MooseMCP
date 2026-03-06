"""MCP server that exposes Moose analysis tools to LLM clients.

This file is the bridge between the Model Context Protocol (MCP) world
and the Moose (Pharo) analysis platform.  Every ``@mcp.tool()``
decorated function translates an MCP tool call into a JSON-RPC request
forwarded to the Moose server via :mod:`mooseRPCClient`.

Usage::

    python mooseMCPServer.py

The server communicates over *stdio* (standard MCP transport).
The Moose JSON-RPC server must be running on ``http://localhost:4444/``
before any tool call is made.
"""

import logging

from mcp.server.fastmcp import FastMCP

from mooseRPCClient import callMooseServer

# ---------------------------------------------------------------------------
# Server & logging setup
# ---------------------------------------------------------------------------

mcp = FastMCP(name="MooseMCPServer")

logging.basicConfig(filename="mooseMCP.log", level=logging.INFO)
logger = logging.getLogger("MooseMCPServer")


# ----------------------------------------------------------------------------
# T O O L S  -  L I S T
# ----------------------------------------------------------------------------

@mcp.tool()
def listEntitiesForType(entityType: str) -> list[str]:
    """List all entities of a given type in the loaded Moose project.

    Args:
        entityType: The entity type as a string, for example ``"Package"``,
                    ``"Class"``, ``"Interface"``, or ``"Method"``.

    Returns:
        A list of strings naming all entities of the requested type.
    """
    return callMooseServer("list:entitiesForType", [entityType])


@mcp.tool()
def listEntityChildren(entity: str) -> list[str]:
    """List all direct children of an entity.

    Args:
        entity: A string naming an entity, for example
                ``"fr.inria.moose"``.

    Returns:
        A list of strings naming all children of the given entity.
    """
    return callMooseServer("list:entityChildren", [entity])


@mcp.tool()
def listEntityClients(entity: str) -> list[str]:
    """List all clients of an entity.

    A *client* is any other entity that depends on (uses) the given one.

    Args:
        entity: A string naming an entity.

    Returns:
        A list of strings naming all clients of the given entity.
    """
    return callMooseServer("list:entityClients", [entity])


@mcp.tool()
def listEntityProviders(entity: str) -> list[str]:
    """List all providers of an entity.

    A *provider* is any other entity that the given one depends on.

    Args:
        entity: A string naming an entity.

    Returns:
        A list of strings naming all providers of the given entity.
    """
    return callMooseServer("list:entityProviders", [entity])


@mcp.tool()
def listEntityParents(entity: str) -> list[str]:
    """List the parents of an entity.

    Typically there is only one parent per entity.

    Args:
        entity: A string naming an entity.

    Returns:
        A list of strings naming all parents of the given entity.
    """
    return callMooseServer("list:entityParents", [entity])


@mcp.tool()
def listEntityTypes() -> list[str]:
    """List all entity types present in the loaded Moose project.

    Returns:
        A list of strings naming all entity types in the project.
    """
    return callMooseServer("list:entityTypes", [])


@mcp.tool()
def listEntityProperty(entity: str) -> list[str]:
    """List all properties of an entity.

    Args:
        entity: A string naming an entity.

    Returns:
        A list of strings naming all properties of the given entity.
    """
    return callMooseServer("list:entityProperties", [entity])


# ----------------------------------------------------------------------------
# T O O L S  -  R E Q U E S T S
# ----------------------------------------------------------------------------

@mcp.tool()
def requestEntityName(entity: str) -> str:
    """Get the fully qualified name of an entity.

    Args:
        entity: A string naming an entity.

    Returns:
        The fully qualified name of the given entity.
    """
    return callMooseServer("request:entityName", [entity])


@mcp.tool()
def requestEntityType(entity: str) -> str:
    """Get the type of an entity.

    Args:
        entity: A string naming an entity.

    Returns:
        A string naming the type of the given entity.
    """
    return callMooseServer("request:entityType", [entity])


@mcp.tool()
def requestModelName() -> str:
    """Get the name of the currently loaded Moose project.

    Returns:
        A string naming the current project.
    """
    return callMooseServer("request:modelName", [])


@mcp.tool()
def requestModelRepository() -> str:
    """Get the GitHub repository URL of the currently loaded Moose project.

    Returns:
        The GitHub repository URL of the project.
    """
    return callMooseServer("request:modelRepository", [])


@mcp.tool()
def requestModelSize() -> str:
    """Get the total number of entities in the currently loaded Moose project.

    Returns:
        The total number of entities in the project.
    """
    return callMooseServer("request:modelSize", [])


# ----------------------------------------------------------------------------
# T O O L S  -  P R O P E R T I E S  /  M E T R I C S
# ----------------------------------------------------------------------------

@mcp.tool()
def metricPackageCohesion(entity: str) -> float:
    """Get the Martin cohesion of a package.

    Martin's cohesion ranges between 0 and 1; the higher, the better.

    Args:
        entity: A string naming a package.

    Returns:
        Martin's cohesion value for the given package.
    """
    return callMooseServer("property:packageCohesion", [entity])


@mcp.tool()
def metricPackageCoupling(entity: str) -> int:
    """Get the Martin efferent coupling of a package.

    Martin's efferent coupling is a non-negative integer; the lower,
    the better.

    Args:
        entity: A string naming a package.

    Returns:
        Martin's efferent coupling for the given package.
    """
    return callMooseServer("property:packageCoupling", [entity])


@mcp.tool()
def metricClassLackOfCohesion(entity: str) -> float:
    """Get the Lack of Cohesion in Methods (LCOM) metric for a class.

    Args:
        entity: A string naming a class.

    Returns:
        The LCOM value for the given class.
    """
    return callMooseServer("property:classLackOfCohesion", [entity])


@mcp.tool()
def metricMethodNumberOfStatements(entity: str) -> float:
    """Get the number of statements in a method.

    Args:
        entity: A string naming a method.

    Returns:
        The number of statements in the given method.
    """
    return callMooseServer("property:methodNumberOfStatements", [entity])


@mcp.tool()
def metricMethodCyclomaticComplexity(entity: str) -> float:
    """Get the cyclomatic complexity of a method.

    Args:
        entity: A string naming a method.

    Returns:
        The cyclomatic complexity of the given method.
    """
    return callMooseServer("property:methodCyclomaticComplexity", [entity])


@mcp.tool()
def hasProperty(entity: str, property: str) -> bool:
    """Check whether a given entity has a given property.

    Args:
        entity: A string naming an entity.
        property: A property name.

    Returns:
        ``True`` if the entity has the given property, ``False`` otherwise.
    """
    return callMooseServer("property:hasProperty", [entity, property])


# ----------------------------------------------------------------------------
# T O O L S  -  M E M O R Y
# ----------------------------------------------------------------------------

@mcp.tool()
def memorySet(name: str, entities: list[str]) -> int:
    """Associate a key with a list of entities in the Moose server memory.

    Args:
        name: A key string.
        entities: A list of entity names to associate with the key.

    Returns:
        The number of entities stored under the given key.
    """
    return callMooseServer("memory:set", [name, entities])


@mcp.tool()
def memoryGet(name: str) -> list[str]:
    """Retrieve a list of entities from the Moose server memory by key.

    Args:
        name: The key associated with the list.

    Returns:
        A list of entity names stored under the given key.
    """
    return callMooseServer("memory:get", [name])


# ----------------------------------------------------------------------------
# R E S O U R C E S
# ----------------------------------------------------------------------------

# `dict` return type is automatically serialised as mime_type="application/json"
@mcp.resource("resource://model-report")
def resourceModelReport() -> dict:
    """Provide a summary report on the loaded Moose model.

    The report includes:

    - Raw counts of entities by type (package, class, method, ...)
    - Number of "large" entities
    - Number of "complex" entities

    Returns:
        A dict that is serialised as JSON.
    """
    return callMooseServer("resource:model-report", [])


@mcp.resource(uri="resource://package-dsm", mime_type="image/png")
def resourcePackageDSM() -> bytes:
    """Provide a Dependency Structure Matrix (DSM) image for all packages.

    Returns:
        A PNG image of the package DSM as raw bytes.
    """
    return callMooseServer("resource:package-dsm", [])


# ----------------------------------------------------------------------------
# E N T R Y   P O I N T
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
