# UTCP Lab — Direct Tool Discovery and Invocation

A small, hands-on introduction to the **Universal Tool Calling Protocol (UTCP)** for engineers already familiar with MCP.

## What this lab showcases

This lab demonstrates how an AI tool client can **discover and invoke an existing REST API without an MCP server**.

- **Native API:** A FastAPI endpoint (`GET /multiply`) performs a simple calculation.
- **UTCP manual:** A second endpoint (`GET /utcp`) describes the tool, its inputs/outputs, and how to call the API.
- **Discovery and execution:** A Python UTCP client reads the manual and invokes the API using its native HTTP interface.

Unlike an MCP wrapper, the UTCP manual provides tool metadata and invocation instructions; it does **not** proxy every tool call. This example uses an explicit UTCP manual rather than OpenAPI auto-discovery.

## Project structure

```text
utcp-lab/
├── app.py       # FastAPI service and UTCP manual
├── client.py    # UTCP discovery and tool invocation
├── pyproject.toml
└── README.md
```

## Getting started

**Prerequisites:** Python 3.11+ and [uv](https://docs.astral.sh/uv/).

From the project directory, install dependencies:

```bash
uv sync
```

## Usage

**1. Start the FastAPI server** in one terminal:

```bash
uv run uvicorn app:app --reload
```

The service is available at `http://127.0.0.1:8000`.

**2. Inspect the REST API and UTCP manual** (optional):

```bash
curl 'http://127.0.0.1:8000/multiply?x=6&y=7'
curl 'http://127.0.0.1:8000/utcp'
```

The REST endpoint returns:

```json
{"result":42}
```

**3. Run the UTCP client** in a second terminal:

```bash
uv run python client.py
```

The client discovers the `multiply` tool from `/utcp` and invokes it with `x=6` and `y=7`. The returned result contains `42` (the exact console representation depends on the SDK version).

## How it works

```text
client.py
   │
   ├── GET /utcp ──────► Tool metadata + HTTP call template
   │
   └── GET /multiply ──► Native REST endpoint ──► {"result": 42}
```

UTCP describes **what the tool does** and **how to call it**. The existing application remains responsible for executing the operation.

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
- The URLs in `app.py` and `client.py` assume the API runs locally on port `8000`.
- Useful next steps: try OpenAPI-based discovery, add authenticated endpoints, or compare the same API wrapped in MCP.

## References

- [UTCP documentation](https://www.utcp.io/docs/)
- [Python UTCP SDK](https://github.com/universal-tool-calling-protocol/python-utcp)
- [Official UTCP vs. MCP comparison](https://www.utcp.io/utcp-vs-mcp)
- [UTCP security considerations](https://www.utcp.io/security)
