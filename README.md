# UTCP Lab — Direct Tool Discovery and Invocation

A small, hands-on introduction to the **Universal Tool Calling Protocol (UTCP)** for engineers already familiar with MCP.

## What this lab showcases

This lab demonstrates how an AI tool client can **discover and invoke an existing REST API without an MCP server**.

- **Native API:** FastAPI endpoints (`GET /multiply`, `GET /divide`) perform simple calculations.
- **UTCP manual:** `GET /utcp` describes both tools, their inputs/outputs, and how to call the APIs.
- **Discovery and execution:** A Python UTCP client reads the manual and invokes operations using the native HTTP interface.

Unlike an MCP wrapper, the UTCP manual provides tool metadata and invocation instructions; it does **not** proxy every tool call. This example uses an explicit UTCP manual rather than OpenAPI auto-discovery.

The repo includes **three ways to exercise the same provider**, from a plain UTCP client call through LangChain agents with increasing automation.

## Project structure

```text
utcp-lab/
├── app.py                 # FastAPI service, REST endpoints, and UTCP manual
├── client.ipynb           # Minimal UTCP client (discover + call multiply)
├── langchain_agent.ipynb  # LangChain agents: manual @tool vs auto-discovery
├── pyproject.toml
└── README.md
```

## Getting started

**Prerequisites:** Python 3.12+ and [uv](https://docs.astral.sh/uv/).

Install dependencies:

```bash
uv sync
```

For the LangChain notebooks, you also need a **local OpenAI-compatible LLM**. The examples assume [Ollama](https://ollama.com/) at `http://localhost:11434` with a model such as `qwen3.8:27b`. Adjust the model name in `langchain_agent.ipynb` to match what you have installed.

**Note:** `langchain-utcp-adapters` on PyPI still declares a dependency on LangChain 0.3.x. This project uses a `[tool.uv] override-dependencies` entry in `pyproject.toml` so it can run with LangChain 1.x and `langchain-core` 1.8+.

## Usage

### 1. Start the API

In one terminal:

```bash
uv run uvicorn app:app --reload
```

The service listens at `http://127.0.0.1:8000`.

### 2. Inspect the API and manual (optional)

```bash
curl 'http://127.0.0.1:8000/multiply?x=6&y=7'
curl 'http://127.0.0.1:8000/divide?x=42&y=6'
curl 'http://127.0.0.1:8000/utcp'
```

Example multiply response:

```json
{"result": 42}
```

### 3. Run the examples (notebooks)

`uv run jupyter …` starts the **Jupyter server** from this project’s `.venv`, but each notebook runs in a separate **kernel** process. That kernel is chosen from kernels registered on your machine (`jupyter kernelspec list`), not automatically from the server’s venv.

If imports like `utcp` or `langchain_utcp_adapters` fail, the notebook is almost certainly using the wrong kernel (often the user-wide `python3` spec, which may point at another project’s venv).

**One-time setup** — register a kernel that uses this repo’s interpreter:

```bash
uv run python -m ipykernel install --user --name utcp-lab --display-name "utcp-lab (.venv)"
```

Then start Jupyter from the project directory:

```bash
uv run jupyter lab
# or: uv run jupyter notebook
```

In Jupyter Lab: **Kernel → Change kernel → utcp-lab (.venv)**. The notebooks in this repo default to that kernel name.

**Cursor / VS Code:** use **Python: Select Interpreter** and choose `./.venv/bin/python` for the notebook (the kernel picker in the top-right of the notebook UI).

**Sanity check** — in the first cell:

```python
import sys
sys.executable
```

You should see a path ending in `utcp-lab/.venv/bin/python`.

---

## Three client paths

All examples use the same UTCP configuration: a `manual_call_templates` entry named `demo` that points at `http://127.0.0.1:8000/utcp`. During `UtcpClient.create`, the client discovers tools from that manual (`demo.multiply`, `demo.divide`, and so on).

| Path | Notebook | What it demonstrates |
| --- | --- | --- |
| **1. UTCP client** | [`client.ipynb`](client.ipynb) | Call a discovered tool directly with `client.call_tool`—no agent framework. |
| **2. LangChain + `@tool`** | [`langchain_agent.ipynb`](langchain_agent.ipynb) (first section) | Wrap **one** operation (`multiply`) in a hand-written LangChain tool, then run a LangGraph-backed agent. |
| **3. LangChain + auto-discovery** | [`langchain_agent.ipynb`](langchain_agent.ipynb) (second section) | Use `load_utcp_tools(client)` from `langchain-utcp-adapters` to expose **every** tool in the manual, including `divide`. |

### 1. UTCP client (`client.ipynb`)

Shows the smallest useful flow:

1. Create `UtcpClient` with the `demo` call template.
2. Rely on discovery during initialization.
3. Invoke `demo.multiply` with `client.call_tool`.

No LangChain or LLM is involved—only discovery and a native HTTP call driven by the manual.

### 2. LangChain with the `@tool` annotation (`langchain_agent.ipynb`)

Shows how to plug UTCP into an agent when you only want to expose specific tools:

1. Create the same UTCP client.
2. Define `multiply` with LangChain’s `@tool` decorator; inside the function, call `client.call_tool("demo.multiply", ...)`.
3. Pass that single tool to `create_agent` and send a natural-language prompt (for example, “Calculate 6 * 7”).

The agent only knows about **multiply**. It does not see `divide` unless you add another wrapper.

### 3. LangChain with auto-discovery (`langchain_agent.ipynb`)

Shows adapter-based conversion of the full UTCP tool catalog:

1. Create the UTCP client (same config as above).
2. `tools = await load_utcp_tools(client)` to convert all discovered tools—including **`divide`**—into LangChain `StructuredTool` instances.
3. Pass the full list to `create_agent`.

Try a prompt that chains both operations, for example: *“Multiply 12 by 12 then divide by 10.”* The agent can select multiply and divide from the automatically loaded tool set.

## How it works

```text
Notebooks / UtcpClient
   │
   ├── GET /utcp ─────────► Tool metadata (multiply, divide) + HTTP call templates
   │
   ├── GET /multiply ─────► Native REST ──► {"result": …}
   │
   └── GET /divide ───────► Native REST ──► {"result": …}
```

UTCP describes **what each tool does** and **how to call it**. The FastAPI app still executes the operations. LangChain layers (manual `@tool` or `load_utcp_tools`) only change how those capabilities are presented to an LLM.

## UTCP vs. MCP: trade-offs

Both approaches let agents discover and invoke tools, but they put the integration boundary in different places:

- **UTCP:** The client discovers a *manual* describing a tool's schema and native invocation method, then calls the underlying HTTP API, CLI command, or other supported interface directly.
- **MCP:** The client discovers tools through an MCP server and invokes them using MCP's standardized tool-call interface. The server implements the integration, potentially wrapping other services or providing capabilities of its own.

| Consideration | UTCP | MCP |
| --- | --- | --- |
| Existing REST APIs | Can reuse native endpoints and, with the relevant plugin, discover operations from OpenAPI | Typically requires an MCP adapter/server |
| Runtime overhead | Avoids an extra wrapper/proxy for native calls | A remote proxy can add overhead; a local server need not add a network hop |
| Authentication | Uses the underlying service's auth model | Uses MCP connectivity/auth plus any downstream credentials the server needs |
| Governance | Enforcement lives in the client, API gateway, and/or destination service | An MCP server/gateway can centralize policy, auditing, and rate limits |
| Capabilities | Primarily tool discovery and invocation across native protocols | Tools **plus** resources, prompts, and richer client/server interactions |
| Integration work | Less wrapper code for existing APIs, but clients need transport handlers and execution policies | Additional server surface, but a consistent interface for diverse backends |
| Ecosystem | Useful for API-centric integrations; check client/plugin support for each transport | Broad existing support across agent frameworks and AI applications |

### When to use UTCP

Choose **UTCP** when you:

- Have **existing HTTP APIs or OpenAPI specs** and want to expose them to agents with minimal adapter code.
- Control the agent's runtime and can provide **native credentials, egress controls, and transport plugins**.
- Want direct calls to existing services rather than running an MCP wrapper solely to forward requests.
- Are building a **tool catalog/registry** where discovery and invocation can be kept separate from orchestration.

### When to use MCP

Choose **MCP** when you:

- Need to integrate with **MCP-native tools, servers, or host applications**.
- Want one controlled execution boundary for backend access, **policy enforcement, credential isolation, or auditing**.
- Need **resources, prompts, or other MCP capabilities** beyond ordinary tool invocation.
- Are exposing functionality that is not already a clean API and benefits from **server-side aggregation, state, or business logic**.

### When to use both

A hybrid is often the most practical option. Keep existing MCP integrations while using UTCP for native APIs. Your agent framework can present both through a unified tool registry and dispatch each call through the appropriate client. UTCP also offers an MCP transport plugin for interoperability.

### Production caveats

- **Direct does not mean automatically secure.** Validate discovered manuals and destinations; enforce allowlists, timeouts, least-privilege permissions, and explicit approval for dangerous operations (especially CLI tools). Do not treat tool descriptions as trusted instructions.
- **Native auth is not centralized governance.** If you rely on an MCP gateway today, moving to UTCP may shift authorization, audit logging, quotas, and policy enforcement into your client or existing API infrastructure.
- **Performance improvements are workload-dependent.** Benchmark discovery overhead, tool-call latency, streaming behavior, and tracing rather than assuming UTCP always wins.
- **Maintain observability across both paths.** Instrument the agent dispatcher, client transport, and downstream services; propagate trace context and attribute tool calls consistently.

**Rule of thumb:** If an MCP server would only proxy an already-documented API, evaluate UTCP first. If the server provides meaningful isolation, policy, aggregation, or MCP-specific features, MCP may be the better boundary.

## Notes

- This is a **local learning lab**, not a production integration. It does not include authentication, authorization, or tool-manual trust controls.
- URLs in `app.py` and the notebooks assume the API on port `8000` and Ollama on port `11434`.
- Useful next steps: try OpenAPI-based discovery, add authenticated endpoints, or compare the same API wrapped in MCP.

## References

- [UTCP documentation](https://www.utcp.io/docs/)
- [Python UTCP SDK](https://github.com/universal-tool-calling-protocol/python-utcp)
- [LangChain UTCP adapters](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters)
- [Official UTCP vs. MCP comparison](https://www.utcp.io/utcp-vs-mcp)
- [UTCP security considerations](https://www.utcp.io/security)