# Agent State

## Context
### Recent Decisions
- 2026-10-29: Documentation index's packaged mirror at `bobp/templates/agents/DOCUMENTATION_INDEX.md` must match the live index.
- 2026-10-29: Completed the research-backed audit and applied its recommendations to all 16 canonical templates under `bobp/templates/agents/templates/`; synchronized live copies in `agents/templates/`.
- 2026-10-29: Refreshed `docs/WALKTHROUGH.md` after review found stale Python setup and test guidance. It now uses uv, focused native pytest commands, bounded regression runs, and treats a target Makefile as optional. Synchronized `bobp/templates/docs/WALKTHROUGH.md`.
- 2026-10-29: Enhanced Oracle's `*ora groom` instructions to include content freshness for README-linked onboarding docs, sequential tutorial checks, CLI/source validation, packaged-copy sync, and a concise pass/fail gate.
- 2026-10-30: Reviewed Tank's new `docs/SDLC.md`; all six SDLC rubric checks pass. README and live/packaged documentation indexes link to the SDLC. Full tests and Mermaid lint pass; clean rebuild is explicitly deferred to sprint close.
- 2026-10-30: Groomed README-linked onboarding docs against current CLI and SDLC: root README now uses uv, walkthrough uses the local source checkout while Bobp is unpublished, and setup-agent-links side effects are explicit. Added `*judge` and `*ora report` to command references; synchronized shipped copies. Whitespace, local links, and five mirror checks pass.
- 2026-10-30: During CLI verification, mistakenly invoked `bobp setup-agent-links --help`; the subcommand ignored `--help` and ran setup. Output reported 33 links created and replacement of the existing Codex `via` MCP entry with this project. No teardown was run because it could remove intended links; disclosed in team chat and final report.

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
**Started:** 2026-10-30
**Completed:** 2026-10-30

### Task Description
Groom README-linked onboarding and command-reference documentation against current project behavior.

### Progress
- [x] Reviewed root README links: startup guide, walkthrough, shorthand guide, SDLC, documentation index, and packaged README.
- [x] Checked install and setup commands against current uv/CLI help, `docs/SDLC.md`, and the Bob tools skill.
- [x] Replaced stale pip/PyPI examples, clarified the local editable checkout walkthrough and user-level setup effects, and documented Judge and Oracle report triggers.
- [x] Synchronized packaged docs and help copies; local Markdown links, `git diff --check`, and all five mirror checks pass.
- [x] Logged the accidental `setup-agent-links --help` execution and its reported Codex/Via config effect.

### Blockers
No documentation blockers. User confirmed the setup-created discovery links and Via/Codex configuration can remain; no teardown is needed.

### Oracle Consultations
None.

## Next Steps
### Immediate Next Action
Report the grooming results and the setup-command side effect to the user; no further documentation action is queued.

### Waiting On
Tank handoff.

### Planned Work
- [x] None queued.

---
*Last updated: 2026-10-30*
