# pythonClient – MooseMCP Python package

This directory contains the Python side of the MooseMCP project.
It acts as a *client* to the Moose JSON-RPC server running in Pharo,
and simultaneously exposes those capabilities as an *MCP server* to
LLM clients such as Claude Desktop.

## Module overview

| File | Role |
|------|------|
| `mooseRPCClient.py` | Low-level JSON-RPC transport to the Moose (Pharo) server. All MCP tools delegate to `callMooseServer()` defined here. |
| `mooseMCPServer.py` | MCP server (stdio transport). Declares every Moose analysis tool with `@mcp.tool()` and forwards calls to `mooseRPCClient`. |
| `mathServer.py` | Optional standalone MCP server for basic arithmetic / comparisons. Can be registered alongside `mooseMCPServer` in any MCP client. |
| `mooseMCPClient.py` | Interactive LLM client using [Groq](https://groq.com) / Qwen. Starts a question loop and delegates to the MCP tools. |
| `mistralClient.py` | Alternative interactive client using a local [Ollama](https://ollama.com) model via the OpenAI-compatible API. Manages the tool-call cycle manually. |

## Installing

```sh
uv venv
uv add -r requirements.txt
```

You must also create a `.env` file declaring your Groq API key:

```
GROQ_API_KEY="... your key here ..."
```

## Running

1. Start the Moose image and load your Famix model, then start the
   JSON-RPC server from the Pharo side:

   ```st
   server := MMCPToolServer new mooseModel: <the-moose-model>; yourself.
   server start.
   ```

2. Start the Python client:

   ```sh
   python mooseMCPClient.py   # Groq / Qwen (default)
   # or
   python mistralClient.py    # local Ollama model
   ```

3. Type your questions at the prompt.  Enter `quit` to exit.

## Port configuration

The Moose JSON-RPC server port is **4444** by default.  It is
configured in two places:

* **Python** – `mooseRPCClient.MOOSE_URL` (default `http://localhost:4444/`).
  Override it at runtime with `mooseRPCClient.configure(url)`.
* **Pharo** – `MMCPServer >> defaultPort`.
