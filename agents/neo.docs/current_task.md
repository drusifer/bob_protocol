# Current Task

**Status:** Complete
**Assigned to:** Neo
**Started:** 2026-04-12T12:49

## Task Description
Fix Codex MCP startup failure for the `via` server in `/home/drusifer/Projects/bob_protocol`.

## Progress
- [x] Reproduced failure: missing `.via/index.db` caused `via mcp serve` to exit before initialize response.
- [x] Added TDD coverage for via index creation, Codex MCP registration args/env, and `.mcp.json` hardening.
- [x] Implemented setup changes to ensure via index, set project-local `HOME`, and pass `--no-web`.
- [x] Added `make test` and `make via_index` targets.
- [x] Built `.via/index.db` and updated active Codex MCP config.
- [x] Verified `make test V=-vv` passes.

## Blockers
None

## Oracle Consultations
- Posted initial Oracle consult request in `agents/CHAT.md` before implementation.

---
*Last updated: 2026-04-12T12:56*
