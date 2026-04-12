# Agent Local Context Template:

Agents *must* use this for keeping their context.md files organized

> ## Recent Decisions
> - 2026-04-12: via MCP setup must create/verify `.via/index.db`, disable via's web UI for stdio MCP, and set `HOME` to the project root so MCP logs are writable under sandboxed clients.
>
> ## Key Findings
> - Codex MCP `via` startup failure:
>   - `via mcp serve` exits before initialize when `.via/index.db` is missing.
>   - In the Codex sandbox, default via MCP logging to `/home/drusifer/.via/mcp.log` fails with read-only filesystem.
>   - `via mcp serve` starts the web UI by default, which can fail when ports 7891-7900 are unavailable.
>
> ## Important Notes
> - Fixed setup to register Codex via MCP as:
>   `codex mcp add via --env HOME=<project-root> -- <via> mcp serve --no-web <project-root>`
> - Added `make test` and `make via_index` project targets.
> - Active Codex MCP config for this workspace was updated with the fixed command and env.
>
>---
>*Last updated: 2026-04-12T12:56*
