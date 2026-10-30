# Agent State

## Context
### Recent Decisions & Discoveries
- 2026-10-29: `*learn` established `uv` as the default for new Python projects (`uv sync`, `uv add`, `uv run`, committed `uv.lock`). Existing package managers remain unless migration is explicitly requested. Updated build-env and Neo guidance plus shipped templates; broadcast the lesson in `agents/CHAT.md`.
- 2026-10-29: `$bob-protocol init` verified agent links and initialized Bob. Root `AGENTS.md` is an existing symlink to `agents/AGENTS.md` (mtime Aug 7); the requested contributor guide was not written because the user explicitly said not to modify an existing file.
- Repository clean and up to date with `origin/main` (commit `6be68e8`).
- All 24 shared skills active and discovered via `.claude/skills/` (`bobp setup-agent-links`).
- Two-tier loop architecture fully formalized:
  - **Planning Loops**: `epic` (*Shape Up* / *Inspired*), `story` (*User Story Mapping* / *Agile Estimating*), `sprint` (*The Scrum Guide*).
  - **Work Loops**: `impl` (*TDD* — Beck), `fix` (*Debugging* — Agans), `refactor` (*Refactoring* — Fowler), `spike` (*XP Installed*), `uat` (*Agile Testing* — Crispin & Gregory), `deploy` (*Continuous Delivery* — Humble & Farley), coordinated by `bloop`.
- All 10 loop skills contain Brookhart-compliant `LOOP_<TARGET>` effectiveness rubrics with standardized chat verdict lines (`rubric <CODE>: CODE1=L CODE2=L ...`).
- All documentation files (`README.md`, `STARTUP.md`, `agents/bob/HELP.md`, `SHORTHAND_GUIDE.md`, `agents/DOCUMENTATION_INDEX.md`) and their template mirrors in `bobp/templates/` are synchronized with zero drift.
- Greenfield application guide created: [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) ("TableCraft — Restaurant Reservation System").
- Full test suite passes: 76 passed, 7 skipped.

### Key Working Files
- Main operating guidelines: [`agents/AGENTS.md`](agents/AGENTS.md)
- Command trigger guide: [`SHORTHAND_GUIDE.md`](SHORTHAND_GUIDE.md)
- Walkthrough guide: [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md)
- Artifact catalog & rubrics: [`agents/templates/ARTIFACTS.md`](agents/templates/ARTIFACTS.md)
- Team chat log: [`agents/CHAT.md`](agents/CHAT.md)

## Current Task
**Status:** Completed
**Assigned to:** Bob
**Started:** 2026-10-15T09:58:00
**Completed:** 2026-10-15T10:00:00

### Task Description
Apply the user's `*learn` instruction to use uv for Python projects going forward.

### Progress
- [x] Read init protocol, recent chat, Bob state, and project capability declarations
- [x] Ran `bobp setup-agent-links`; links verified
- [x] Logged init request and readiness to `agents/CHAT.md`
- [x] Confirmed root `AGENTS.md` already exists and did not alter it
- [x] Updated canonical and shipped build-env guidance, Neo's Python setup guidance, and Python SDLC templates
- [x] Broadcast the convention in `agents/CHAT.md`
- [x] Ran `git diff --check`; no tests run (documentation-only update)

### Blockers
None

## Next Steps
### Immediate Next Action
Await next user request. This lesson sets the default for new Python projects; the repository's current pip-based environment was not migrated.

### Waiting On
User

---
*Last updated: 2026-10-29T15:04:00*
