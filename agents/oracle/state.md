# Agent State

## Context
### Recent Decisions
- 2026-10-29: Documentation index's packaged mirror at `bobp/templates/agents/DOCUMENTATION_INDEX.md` must match the live index.
- 2026-10-29: Completed the research-backed audit and applied its recommendations to all 16 canonical templates under `bobp/templates/agents/templates/`; synchronized live copies in `agents/templates/`.

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

### Task Description
Judge the recent template/tooling work and make the trace command consistent with other direct Bobp CLI tools.

### Progress
- [x] Added a root README contents list and links to key docs
- [x] Updated documentation index date, archive listing, naming and directory guidance
- [x] Synchronized the index with its packaged mirror
- [x] Corrected README test command to `bobp make test`
- [x] Verified local links resolve, index copies match, and `git diff --check` passes
- [x] Audited updater copy rules, packaged file counts, and update tests; no omissions found within the documented refresh scope
- [x] Reviewed all 16 templates and verified their packaged counterparts match
- [x] Researched examples for ADRs, architecture, DDD, stories, test strategy, UAT, incident learning, and documentation style
- [x] Wrote the audit report with per-template findings, rubric gaps, research references, and implementation status
- [x] Updated all 16 canonical templates and synchronized all 16 live copies
- [x] Verified one check block per template, matching packaged/live copies, and clean `git diff --check`
- [x] Did not run tests for the docs-only template edits; noted that rubric calibration remains future review work
- [x] Confirmed `bobp trace-annotate` is registered/tracked, but fails due to undeclared `jinja2`; documented `bobp make judge-trace` target is absent from Makefile/history
- [x] Tank restored the `judge-trace` Make target, declared Jinja2, updated Judge/Trin instructions, and ensured template check blocks are stripped from generated CHAT/state files
- [x] Ran the full suite: 76 passed, 7 skipped; synthetic trace smoke test produced the expected annotation
- [x] Recorded that this Codex session cannot receive a numeric TES: the trace tool reads Claude JSONL only and no Claude project directory exists here
- [x] Applied user clarification: removed the Make wrapper and changed Judge, Trin, and Neo guidance to invoke `bobp trace-annotate` directly; verified no active skill references the wrapper

### Blockers
None

### Oracle Consultations
None yet

## Next Steps
### Immediate Next Action
Tank: review `bobp/tools/trace_annotate.py`, `pyproject.toml`, and the Makefile. Decide whether the existing `bobp trace-annotate` CLI should be the judge workflow; address its undeclared Jinja dependency and align the judge/Trin skills. `docs/SDLC.md` is currently absent.

### Waiting On
None

### Planned Work
- [ ] Finish the direct CLI command consistency update and verify no active guidance references `bobp make judge-trace`.
- [ ] Calibrate revised template checks against representative completed artifacts later.

---
*Last updated: 2026-10-29*
