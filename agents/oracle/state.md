# Agent State

## Context
### Recent Decisions
- 2026-10-29: Documentation index's packaged mirror at `bobp/templates/agents/DOCUMENTATION_INDEX.md` must match the live index.
- 2026-10-29: Completed the research-backed audit and applied its recommendations to all 16 canonical templates under `bobp/templates/agents/templates/`; synchronized live copies in `agents/templates/`.
- 2026-10-29: Refreshed `docs/WALKTHROUGH.md` after review found stale Python setup and test guidance. It now uses uv, focused native pytest commands, bounded regression runs, and treats a target Makefile as optional. Synchronized `bobp/templates/docs/WALKTHROUGH.md`.
- 2026-10-29: Enhanced Oracle's `*ora groom` instructions to include content freshness for README-linked onboarding docs, sequential tutorial checks, CLI/source validation, packaged-copy sync, and a concise pass/fail gate.

### Key Findings
- Root README lacked a contents list and documented `make test` directly; docs index had an outdated update date and referenced an archive file that does not exist.
- No misplaced Markdown files were found. Root-level startup/command guides and `docs/WALKTHROUGH.md` are appropriately placed.
- `bobp update` overlays all 24 packaged shared skills, 16 artifact templates, and all 9 persona `SKILL.md` files. It seeds only missing persona state and `CHAT.md`, regenerates `CHAT.diagram.md`, then rebuilds discovery links.
- Existing state, chat, project-level guides/index/AGENTS, Oracle lessons/memory, and other unrelated project files are not overwritten. The updater does not delete target-only files removed from templates upstream.
- Tests cover representative refreshed skill/persona and preserved state/chat behaviors, but do not explicitly assert exact directory coverage or exclusion of every project-specific file.
- All 16 templates now have one binary check block; both language-specific SDLC files are concise inserts rather than duplicated full guides. Source/live equality, marker-count validation, and `git diff --check` pass.

### Important Notes
- Avoid modifying existing unrelated in-progress changes while grooming; the workspace already contained uv-policy edits.

## Current Task
**Status:** Completed
**Assigned to:** Oracle
**Started:** 2026-10-29
**Completed:** 2026-10-29

### Task Description
Strengthen Oracle's documentation-grooming workflow so important tutorial drift is caught next time.

### Progress
- [x] Added README-linked onboarding freshness checks and a sequential reader-path review to `*ora groom`.
- [x] Added CLI/source verification, safe focused validation, and packaged-copy sync requirements.
- [x] Added a concise PASS/FAIL gate for accuracy, usability, consistency, and mirror sync.
- [x] Synced the packaged Oracle skill and verified canonical/template copies match.
- [x] Refreshed agent discovery links; `git diff --check` passes. No tests run (documentation-only changes).

### Blockers
None

### Oracle Consultations
None.

## Next Steps
### Immediate Next Action
Await the next user request. Future `*ora groom` runs must check root-README-linked onboarding and tutorial docs for stale commands and assumptions.

### Waiting On
User.

### Planned Work
- [ ] None queued.

---
*Last updated: 2026-10-29 23:18*
