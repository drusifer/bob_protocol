# Agent State

## Context
### Recent Decisions & Discoveries
- 2026-10-29: `*learn` established `uv` as the default for new Python projects (`uv sync`, `uv add`, `uv run`, committed `uv.lock`). Existing package managers remain unless migration is explicitly requested. Updated build-env and Neo guidance plus shipped templates; broadcast the lesson in `agents/CHAT.md`.
- 2026-10-29: `$bob-protocol init` verified agent links and initialized Bob. Root `AGENTS.md` is an existing symlink to `agents/AGENTS.md` (mtime Aug 7); the requested contributor guide was not written because the user explicitly said not to modify an existing file.
- 2026-10-29: Planning rule: ask the user only about unresolved decisions with material consequences and high change cost; use repository convention and established practice for routine or reversible choices. Added to canonical and packaged Bob Protocol guidance.
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
**Started:** 2026-10-29T23:10:00
**Completed:** 2026-10-29T23:12:00

### Task Description
Apply the user's `*learn` instruction for planning questions and routine assumptions.

### Progress
- [x] Logged the lesson in `agents/CHAT.md`.
- [x] Added the consequentiality and change-cost filter to canonical and packaged Bob Protocol guidance.
- [x] Refreshed agent discovery links with `bobp setup-agent-links`.
- [x] Followed best practices for this process-only update; no tests run.

### Blockers
None

## Next Steps
### Immediate Next Action
Await the next user request. Planning personas should ask about high-impact, costly-to-change uncertainties and resolve routine choices using convention and best practice.

### Waiting On
User

---
*Last updated: 2026-10-29T15:04:00*
