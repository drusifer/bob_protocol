# Agent State

## Context
### Recent Decisions
- 2026-10-29: Per user direction, BobProtocol tools should be invoked as direct `bobp <tool>` commands; do not require a target project Makefile for trace annotation.

### Key Findings
None yet

### Important Notes
None yet

## Current Task
**Status:** Completed — handoff to Oracle
**Assigned to:** Tank
**Started:** 2026-10-29

### Task Description
Restore a reliable Bobp trace-annotate workflow for the *judge process without inventing an obsolete Make target.

### Progress
- [x] Confirmed Makefile has no `judge-trace` target and Git history shows it was not restored after Make was returned to host projects.
- [x] Confirmed `bobp trace-annotate` exists in the package/CLI but import fails because Jinja2 is undeclared.
- [x] Added Jinja2 runtime dependency and updated packaged/live Judge, Trin, and Neo instructions to use direct `bobp trace-annotate`; clarified Claude-only transcript coverage.
- [x] Removed the temporary Make wrapper per user direction; no target-project Makefile is required.
- [x] Changed Bobp template instantiation so `install`/`clean` remove reviewer-only check blocks from generated state/chat files; updated cleanup test.
- [x] Installed the project environment, verified target discovery and CLI help, exercised a synthetic Claude transcript, and ran the suite (76 passed, 7 skipped).
- [x] Confirmed real trace cannot run in this Codex workspace because no Claude project directory exists.

### Blockers
None

### Oracle Consultations
None yet

## Next Steps
### Immediate Next Action
No immediate action. The direct Bobp CLI help resolves from the project environment, and active skill guidance no longer requires the Make wrapper.

### Waiting On
None

### Planned Work
- [x] Fixed the runtime dependency and generated-artifact check-block leak.
- [x] Removed the wrapper and aligned all active canonical/live instructions with direct Bobp CLI usage.
- [ ] Codex transcript support remains a separate scope item.

---
*Last updated: [timestamp]*
