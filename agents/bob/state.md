# Agent State

## Context
### Recent Decisions & Discoveries
- 2026-10-29: `*learn` established `uv` as the default for new Python projects (`uv sync`, `uv add`, `uv run`, committed `uv.lock`). Existing package managers remain unless migration is explicitly requested. Updated build-env and Neo guidance plus shipped templates; broadcast the lesson in `agents/CHAT.md`.
- 2026-10-29: `$bob-protocol init` verified agent links and initialized Bob. Root `AGENTS.md` is an existing symlink to `agents/AGENTS.md`; the user requested not to modify an existing file.
- 2026-10-29: Planning rule: ask the user only about unresolved decisions with material consequences and high change cost; use repository convention and established practice for routine or reversible choices. Added to canonical and packaged Bob Protocol guidance.
- 2026-10-29: Removed custom `triggers` and `requires` YAML keys from 66 canonical and packaged skill files; retained supported `name`/`description` metadata and moved those concepts into Markdown sections. Synced Bob template and README wording.
- 2026-10-29: Persona rubric follows the artifact-template pattern: canonical `_template_PERSONA_SKILL.md` and packaged mirror contain the removable PERSONA rubric block; generated persona runtime skills do not. Bob links to and applies that template. Added the persona skill to ARTIFACTS.md and aligned Oracle’s rubric-block audit wording.

## Current Task
**Status:** Completed
**Assigned to:** Bob
**Completed:** 2026-10-29

### Task Description
Move the persona rubric to a dedicated authoring template and remove it from runtime persona skills.

### Progress
- [x] Removed custom trigger/require frontmatter from canonical and packaged skill files.
- [x] Added optional Triggers/Requires sections to Bob's skill authoring template.
- [x] Added and synchronized a pass/fail rubric for persona skills.
- [x] Updated Bob’s create/reprompt workflow to use the rubric, frontmatter rules, consequential-question filter, and repository validation.
- [x] Replaced duplicated persona runtime rubrics with a dedicated authoring template containing the removable rubric block.
- [x] Added the template to ARTIFACTS.md, synchronized packaged copies, and updated Bob and Oracle guidance.
- [x] Refreshed agent discovery links and verified no custom keys, mirror equality, and clean diff formatting.
- [x] No tests run; this was documentation-only.

### Blockers
None

## Next Steps
### Immediate Next Action
Await user review or next request. Sources consulted: [Agent Skills specification](https://agentskills.io/specification) and [Anthropic prompting best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables).

### Waiting On
User
