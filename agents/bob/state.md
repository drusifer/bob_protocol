# Agent State

## Context
### Recent Decisions & Discoveries
- 2026-10-29: `*learn` established `uv` as the default for new Python projects (`uv sync`, `uv add`, `uv run`, committed `uv.lock`). Existing package managers remain unless migration is explicitly requested. Updated build-env and Neo guidance plus shipped templates; broadcast the lesson in `agents/CHAT.md`.
- 2026-10-29: `$bob-protocol init` verified agent links and initialized Bob. Root `AGENTS.md` is an existing symlink to `agents/AGENTS.md`; the user requested not to modify an existing file.
- 2026-10-29: Planning rule: ask the user only about unresolved decisions with material consequences and high change cost; use repository convention and established practice for routine or reversible choices. Added to canonical and packaged Bob Protocol guidance.
- 2026-10-29: Removed custom `triggers` and `requires` YAML keys from 66 canonical and packaged skill files; retained supported `name`/`description` metadata and moved those concepts into Markdown sections. Synced Bob template and README wording.
- 2026-10-29: Persona rubric follows the artifact-template pattern: canonical `_template_PERSONA_SKILL.md` and packaged mirror contain the removable PERSONA rubric block; generated persona runtime skills do not. Bob links to and applies that template. Added the persona skill to ARTIFACTS.md and aligned Oracle’s rubric-block audit wording.
- 2026-10-30: Added Morpheus `*advise` guidance: use domain language/boundaries and invariants, concrete BDD behavior examples, and explicit KISS/DRY tradeoffs to recommend a design. Synchronized `agents/morpheus/SKILL.md` with `bobp/templates/agents/morpheus/SKILL.md.txt`.

## Current Task
**Status:** Completed
**Assigned to:** Bob
**Started:** 2026-10-30
**Completed:** 2026-10-30

### Task Description
Teach Morpheus `*advise` to resolve design conundrums using domain modeling, BDD examples, and explicit KISS/DRY evaluation.

### Progress
- [x] Added `*advise` trigger and a concise decision method to Morpheus's live and packaged skills.
- [x] Added a stable Morpheus advice suite that creates an ADR and uses the shared DECISION rubric.
- [x] Clarified the DECISION rubric: an optional Related field may be omitted when no decisions relate.
- [x] Focused evaluator suite passes (8 passed); live `morpheus-design-advice` run passes both skill-use and artifact checks.
- [x] Trin QA reviewed the retained run and artifact; Morpheus confirmed the method fits the role and command boundaries.

### Blockers
None

## Next Steps
### Immediate Next Action
No further action; await the user's next request. Reports and fixtures are retained under `build/persona-eval/`.

### Waiting On
User.
