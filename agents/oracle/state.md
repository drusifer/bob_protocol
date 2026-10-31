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
- 2026-10-30: Added `docs/PERSONA_EVALUATION.md` covering prerequisites/setup, suite selection, Choice+Score grading and pass rules, reports/failure review, and TypeSafe data flow. Linked it from the root README, documentation index, and packaged README; synchronized the packaged doc and index copies.
- 2026-10-30: Committed and pushed the evaluation and persona updates as `ad1be67` (`feat(eval): add Choice and Score persona grading`) to `origin/main`; the tree was clean after push.

### Key Findings
- Root README lacked a contents list and documented `make test` directly; docs index had an outdated update date and referenced an archive file that does not exist.
- No misplaced Markdown files were found. Root-level startup/command guides and `docs/WALKTHROUGH.md` are appropriately placed.
- `bobp update` overlays all 24 packaged shared skills, 16 artifact templates, and all 9 persona `SKILL.md` files. It seeds only missing persona state and `CHAT.md`, regenerates `CHAT.diagram.md`, then rebuilds discovery links.
- Existing state, chat, project-level guides/index/AGENTS, Oracle lessons/memory, and other unrelated project files are not overwritten. The updater does not delete target-only files removed from templates upstream.
- Tests cover representative refreshed skill/persona and preserved state/chat behaviors, but do not explicitly assert exact directory coverage or exclusion of every project-specific file.
- All 16 templates now have one binary check block; both language-specific SDLC files are concise inserts rather than duplicated full guides. Source/live equality, marker-count validation, and `git diff --check` pass.

### Important Notes
- Avoid modifying existing unrelated in-progress changes while grooming; the workspace already contained uv-policy edits.
- The working tree remains uncommitted. Current modifications include Bob's evaluator/Choice+Score implementation and tests (`bobp/tools/persona_eval.py`, `bobp/tools/persona_eval_jev.py`, `tests/test_persona_eval.py`, `pyproject.toml`, `uv.lock`, `docs/SDLC.md`); persona, template, Judge, and packaged-template upgrades across `agents/` and `bobp/templates/`; Bob's evaluation note; Oracle's docs/index/README additions; and updated team chat/state. New Oracle docs are `docs/PERSONA_EVALUATION.md` and its packaged mirror `bobp/templates/docs/PERSONA_EVALUATION.md`. No commit or push was requested or performed.
- Exact `git status --short` paths at checkpoint:
  ```text
  README.md
  agents/AGENTS.md
  agents/CHAT.diagram.md
  agents/CHAT.md
  agents/DOCUMENTATION_INDEX.md
  agents/bob/SKILL.md
  agents/bob/state.md
  agents/cypher/SKILL.md
  agents/morpheus/SKILL.md
  agents/mouse/SKILL.md
  agents/neo/SKILL.md
  agents/oracle/SKILL.md
  agents/oracle/state.md
  agents/skills/judge/SKILL.md
  agents/smith/SKILL.md
  agents/tank/SKILL.md
  agents/templates/_template_PERSONA_SKILL.md
  agents/trin/SKILL.md
  bobp/templates/README.md
  bobp/templates/agents/AGENTS.md
  bobp/templates/agents/DOCUMENTATION_INDEX.md
  bobp/templates/agents/bob/SKILL.md.txt
  bobp/templates/agents/cypher/SKILL.md.txt
  bobp/templates/agents/morpheus/SKILL.md.txt
  bobp/templates/agents/mouse/SKILL.md.txt
  bobp/templates/agents/neo/SKILL.md.txt
  bobp/templates/agents/oracle/SKILL.md.txt
  bobp/templates/agents/skills/judge/SKILL.md.txt
  bobp/templates/agents/smith/SKILL.md.txt
  bobp/templates/agents/tank/SKILL.md.txt
  bobp/templates/agents/templates/_template_PERSONA_SKILL.md
  bobp/templates/agents/trin/SKILL.md.txt
  bobp/templates/docs/PERSONA_EVALUATION.md
  bobp/tools/persona_eval.py
  bobp/tools/persona_eval_jev.py
  docs/PERSONA_EVALUATION.md
  docs/SDLC.md
  pyproject.toml
  tests/test_persona_eval.py
  uv.lock
  agents/bob/persona_sayings_eval_2026-10-30.md (untracked)
  ```

## Current Task
**Status:** Completed
**Assigned to:** Oracle
**Started:** 2026-10-30
**Completed:** 2026-10-30

### Task Description
Add user-facing documentation for the new persona evaluation system and groom the links and packaged documentation copies.

### Progress
- [x] Verified `persona-eval --help`, current suite catalog, grader implementation, and existing SDLC guidance.
- [x] Documented prerequisites, setup, suite selection/repeats, Choice+Score grading, report triage, and TypeSafe data handling.
- [x] Added links from README, documentation index, and packaged README; synchronized the packaged guide and index mirrors.
- [x] Validated the six added local documentation links, exact mirror equality, and `git diff --check`.

### Blockers
No documentation blockers. User confirmed the setup-created discovery links and Via/Codex configuration can remain; no teardown is needed.

### Oracle Consultations
None.

## Next Steps
### Immediate Next Action
No active Oracle task is pending. The last work is committed and pushed as `ad1be67`. On resume, read `agents/CHAT.md` and this state, then follow the user's next request.

### Waiting On
User follow-up; the documentation and requested commit/push are complete.

### Planned Work
- [x] None queued.

---
*Last updated: 2026-10-30*
