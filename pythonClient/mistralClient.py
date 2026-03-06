"""Alternative LLM client using a local Ollama model via the OpenAI-compatible API.

This client connects to a locally running `Ollama <https://ollama.com>`_
instance and uses it together with the Moose MCP server to answer
questions about a software project.

Unlike :mod:`mooseMCPClient` (which uses Groq), this client manages
the full tool-call cycle manually:

1. Send the user question to the LLM.
2. If the LLM requests tool calls, execute them via the MCP session.
3. Send the tool results back to the LLM.
4. Print the final answer.

Requirements
------------
- A running Ollama instance on ``http://localhost:11434``.
- The model specified in :func:`interaction_loop` pulled locally
  (default: ``llama3.1:8b``).
- The Moose JSON-RPC server running on ``http://localhost:4444/``.

Usage::

    python mistralClient.py
"""

import asyncio
import json
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

logging.basicConfig(filename="mooseMCP.log", level=logging.CRITICAL)
logger = logging.getLogger("mistralClient")


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def mcp_tools_to_openai(tools):
    """Convert MCP tool descriptors to the OpenAI function-calling schema.

    Args:
        tools: A list of MCP tool objects as returned by
               ``mcp_session.list_tools()``.

    Returns:
        A list of dicts in the OpenAI ``tools`` array format.
    """
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
        })
    return openai_tools


def ask_llm(openAI, llm, tools, message):
    """Send a chat completion request to the LLM.

    Args:
        openAI: An :class:`openai.OpenAI` client instance.
        llm: Model name string (e.g. ``"llama3.1:8b"``).
        tools: List of tool descriptors in the OpenAI schema.
        message: The conversation history as a list of message dicts.

    Returns:
        The raw completion response object.
    """
    logger.debug("Asking model: %s", message)
    response = openAI.chat.completions.create(
        model=llm,
        messages=message,
        tools=tools,
        tool_choice="force",
        temperature=0.2,
    )
    return response


async def call_tools(mcp_session, tool_calls):
    """Execute a list of MCP tool calls and collect their results.

    Args:
        mcp_session: An active :class:`mcp.ClientSession`.
        tool_calls: The ``tool_calls`` list from the LLM response message.

    Returns:
        A list of ``{"role": "tool", ...}`` message dicts ready to be
        appended to the conversation history.
    """
    answer = []
    for tool in tool_calls:
        logger.debug("tool call: %s", str(tool))
        tool_answer = await mcp_session.call_tool(
            tool.function.name,
            json.loads(tool.function.arguments),
        )
        logger.debug("tool answer: %s", str(tool_answer))
        answer.append({
            "role": "tool",
            "tool_name": tool.function.name,
            "content": str(tool_answer),
        })
    return answer


# ---------------------------------------------------------------------------
# Interaction loop
# ---------------------------------------------------------------------------

async def interaction_loop(mcp_session, openAI, tools):
    """Run the interactive question-answer loop with the user.

    At each iteration:

    1. The user enters a question.
    2. The question is sent to the LLM together with the available tools.
    3. If the LLM requests tool calls they are executed via the MCP session.
    4. The tool results are sent back to the LLM for a final answer.
    5. The final answer is printed.

    Type ``quit`` to exit.

    Args:
        mcp_session: An active :class:`mcp.ClientSession`.
        openAI: An :class:`openai.OpenAI` client instance.
        tools: List of tool descriptors in the OpenAI schema.
    """
    llm = "llama3.1:8b"

    while True:
        print("\n=========================================================================")

        question = input("Question: ")
        if question == "quit":
            break

        message = [
            {"role": "user", "content": question}
        ]
        response = ask_llm(openAI, llm, tools, message)

        llm_answer = response.choices[0].message
        logger.debug("Model answer: %s", str(llm_answer))

        if not llm_answer.tool_calls:
            # No tool call requested – print the direct answer.
            print("Answer:", llm_answer.content)
        else:
            # Execute requested tool calls and send results back to the LLM.
            message.append(llm_answer)

            tool_responses = await call_tools(mcp_session, llm_answer.tool_calls)
            for tool_answer in tool_responses:
                message.append(tool_answer)

            # Request the final answer incorporating the tool results.
            logger.debug("tool answer to LLM: %s", message)
            final = openAI.chat.completions.create(
                model=llm,
                messages=message,
            )

            print(f"Answer: {final.choices[0].message.content}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    """Start the MCP server subprocess, connect, and run the interaction loop.

    Steps:

    1. Launch :mod:`mooseMCPServer` as a subprocess.
    2. Initialise an MCP client session.
    3. Retrieve and convert the available MCP tools.
    4. Connect to the local Ollama server.
    5. Enter the interaction loop.
    """
    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["mooseMCPServer.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()

            # Retrieve and convert MCP tools to the OpenAI schema.
            list_tools_result = await mcp_session.list_tools()
            tools = mcp_tools_to_openai(list_tools_result.tools)

            # Connect to the local Ollama instance (OpenAI-compatible API).
            openAI = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # dummy value – not checked by Ollama
            )

            await interaction_loop(mcp_session, openAI, tools)


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
