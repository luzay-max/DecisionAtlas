# DecisionAtlas MCP v2 Read-Only Spike (Not Yet Released)

Status: **Draft implementation spike**. This is not a production MCP service, an approved
enterprise deployment, or a finished agent-autonomy workflow. PR #14 controls G0 evidence
and security release decisions; the implementation PR must remain Draft until approved.

## What this changes (and what it deliberately does not)

The optional Python stdio adapter exposes four MCP tools backed by **existing
DecisionAtlas Engine authenticated API calls**:

- `project_status`: accepted decision count for the explicitly configured workspace.
- `list_project_decisions`: only decisions whose review state is `accepted`.
- `search_project_decisions`: bounded **lexical** ranking of accepted decisions; not an
  embedding or LLM-based semantic search.
- `get_decision_evidence`: resolves the numeric ID against accepted decisions in the
  configured workspace before fetching citations; does not expose arbitrary Decision IDs.

These tools are advisory. Even an `accepted` decision with SourceRefs has not automatically
passed independent source-verification. The response marks missing references explicitly.
No MCP tool can import a repository, change reviews, read local code, execute shell commands,
push Git commits, or change an Engine workspace.

This **does not** automatically identify the Agent's current Git repository. An operator
explicitly configures the target DecisionAtlas `workspace_slug` and a scoped, authorized
Engine session. GitHub/GitLab/Gitee repository-to-workspace mapping and diff checks are
separate follow-up stages.

## Prerequisites and local launch

- Already-running, locally accessible DecisionAtlas Engine API.
- A **real, still-valid** DecisionAtlas viewer (or higher) session with access to the
  chosen workspace. Obtain it via the existing `POST /auth/login` process (or the
  development-only bootstrap if appropriately enabled). Do **not** commit or paste it in
  the repository, MCP config JSON, issue comments, CI artifacts, or shared terminal logs.
- Python 3.11+ and uv. The MCP SDK is **optional and isolated**; the normal Engine
  dependencies and `uv.lock` are intentionally unchanged in this spike.
- A workspace containing human-accepted decisions. A workspace with only candidates
  will return `no_accepted_decisions`, not invent authoritative decisions.

From `services/engine`:

```powershell
$env:DECISIONATLAS_MCP_API_URL = "http://127.0.0.1:8000"
$env:DECISIONATLAS_MCP_WORKSPACE = "your-authorized-workspace"
# Supply DECISIONATLAS_MCP_SESSION_TOKEN via a secure local session environment.
# Do not echo, print, or save the token to the repository.
uv run --with "mcp==2.2.0" python -m app.mcp.server
```

The official MCP Python SDK **v2** uses `MCPServer`, not the old
`from mcp.server.fastmcp import FastMCP` path. In this spike the SDK version is
fixed in the launch command; adding a lockfile and CI protocol-level handshake tests
is a release gate for the next PR.

This command starts **stdio**, so it will not print an interactive shell prompt while
running. An MCP-capable client normally starts it as a child process. Configure the
MCP client to run the exact command with `cwd` set to the Engine directory and arrange
for the three environment variables to be present securely in the subprocess. Do not
paste a live session into an IDE's versioned configuration file.

## Security boundaries

- The **only** accepted Engine API hosts are `127.0.0.1`, `localhost`, or `::1` over
  HTTP with an explicit port. This initial adapter intentionally rejects HTTPS remote
  hosts, URL credentials, additional paths, and query strings.
- Tool parameters never accept a workspace, auth token, repository URL, network host,
  file path, or arbitrary upstream endpoint. Changing the bound workspace requires
  starting a new authorized local server configuration.
- All requests forward the operator's Engine session using the existing
  `x-decisionatlas-session-token` header; the Engine enforces its normal Workspace
  viewer role and Owner Scope restrictions.
- Tool errors are sanitized. Redirects are refused, client environment proxy settings
  are ignored by the default HTTP client, and responses exceeding 2 MB are rejected.
- Retrieved decision text, including source excerpts, remains **untrusted data**; the
  host should treat it as evidence to reason about, not operational instructions.
- MCP Tools expose no private GitLab/Gitee credentials and do not bypass the
  existing candidate → human review → accepted boundary.

## Verification levels

- **Implemented here:** Bridge configuration checks, Engine mocked HTTP contract
  tests, accepted-only filtering, cross-workspace ID guard, citation metadata, input
  limits, and credential/error redaction.
- **Dedicated optional CI test:** Official SDK v2 in-process tool discovery and
  call results, running with a pinned `mcp==2.2.0` dependency (no private data).
- **Not verified yet:** Real `stdio` subprocess negotiation, Claude/Codex/Cursor
  host E2E, realistic accepted decisions in all three Git
  providers, refresh/staleness, agent-trigger hooks, private repository deployment.
- **Release gate:** Connect two real Host clients to a seeded, non-sensitive workspace,
  capture redacted `project_status`/`list_project_decisions`/
  `get_decision_evidence` transcripts, and show that the Agent uses an accepted
  cited decision before modifying a safe sample project. Request security G0
  sign-off before enabling any enterprise data.

Official references:
- [MCP Python SDK v2](https://py.sdk.modelcontextprotocol.io/)
- [Running an MCP stdio server](https://py.sdk.modelcontextprotocol.io/run/)
- [MCP-first project roadmap (Draft PR #14)](https://github.com/luzay-max/DecisionAtlas/pull/14)
