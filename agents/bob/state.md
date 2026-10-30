# Agent State

## Context
### Recent Decisions & Discoveries
- 2026-10-29: `*learn` established `uv` as the default for new Python projects (`uv sync`, `uv add`, `uv run`, committed `uv.lock`). Existing package managers remain unless migration is explicitly requested. Updated build-env and Neo guidance plus shipped templates; broadcast the lesson in `agents/CHAT.md`.
- 2026-10-29: `$bob-protocol init` verified agent links and initialized Bob. Root `AGENTS.md` is an existing symlink to `agents/AGENTS.md`; the user requested not to modify an existing file.
- 2026-10-29: Planning rule: ask the user only about unresolved decisions with material consequences and high change cost; use repository convention and established practice for routine or reversible choices. Added to canonical and packaged Bob Protocol guidance.
- 2026-10-29: Removed custom `triggers` and `requires` YAML keys from 66 canonical and packaged skill files; retained supported `name`/`description` metadata and moved those concepts into Markdown sections. Synced Bob template and README wording.
- 2026-10-29: Persona rubric follows the artifact-template pattern: canonical `_template_PERSONA_SKILL.md` and packaged mirror contain the removable PERSONA rubric block; generated persona runtime skills do not. Bob links to and applies that template. Added the persona skill to ARTIFACTS.md and aligned Oracle’s rubric-block audit wording.
- 2026-10-30: Added Morpheus `*advise` guidance: use domain language/boundaries and invariants, concrete BDD behavior examples, and explicit KISS/DRY tradeoffs to recommend a design. Synchronized `agents/morpheus/SKILL.md` with `bobp/templates/agents/morpheus/SKILL.md.txt`.
- 2026-10-30: Planning now assigns executable tasks L1–L4 by observable complexity/scope, dependencies, and uncertainty. Levels calibrate execution depth, never urgency, duration, persona rank, or quality. Added definitions and PLAN `LEVEL` check to task template; persona rubric checks level-calibrated observable behavior. Canonical and packaged copies synced.
- 2026-10-30: Added a fillable `Personality Traits & Values` section to the persona template, with guidance to make it role-fitting and treat it as tone/judgment guidance rather than procedure. Added the corresponding PERSONA rubric criterion and updated Bob's creation guidance; packaged copies synced.
- 2026-10-30: Set the shared persona demeanor baseline in the template: expert professionals who are courteous, succinct, and respectful; role-specific demeanor and values extend that baseline.
- 2026-10-30: Removed the Via Integration scaffold section and added a PERSONA rubric instruction to avoid optional integrations unless enabled and needed. Packaged template synced. Ran same Promptfoo Cypher2 authoring scenario against Bob/template from `main` and working versions. Main lacks Personality & Values; current includes role-specific demeanor and four values. Both fail overall: main also has workflow/template gaps, current duplicates Cypher's role. Eval additionally revealed the rubric accepts personality without explicitly checking the courteous/succinct/respectful baseline.
- 2026-10-30: Started old-main vs current Bob persona-eval comparison for Cypher2. Current run generated `build/persona-eval/runtime/bob-cypher2-current-20261030T201710Z/project/agents/cypher2/SKILL.md`, but judge failed because the persona scaffold includes a Via Integration placeholder while eval fixture has Via disabled. After two failed eval attempts, stopped per anti-loop guard pending user direction on template-vs-eval expectation. Promptfoo prerequisites are installed and working.
- 2026-10-30: Made `*judge` the Bloop Agent/Skill Quality work-loop. Added Promptfoo-specific runner, evidence triage, owner routing, fresh-fixture verification, fixed-criteria guidance, holdout recommendation, and shared anti-loop stopping rule. Added Judge to Bloop's catalog and synchronized both packaged skills.
- 2026-10-30: Ran `*bloop judge bob`. First single run passed, but manual audit found it omitted the shared courteous/succinct/respectful baseline, so strengthened Bob creation guidance and PERSONA rubric. `--repeat 3` yielded one raw pass and two false positives: one `skill-used` assertion contradicted provider metadata/tool trace, and one grader treated transitive `bloop` as a direct dependency despite explicit rubric context. All three generated artifacts explicitly retain all baseline traits and satisfy the persona rubric on review. Updated Judge to record evidence-backed false-positive overrides separately from raw results; packaged copy synced.

## Current Task
**Status:** Completed
**Assigned to:** Bob
**Started:** 2026-10-30
**Completed:** 2026-10-30

### Task Description
Run `*bloop judge bob` and use the eval evidence to improve and verify Bob's persona-authoring behavior.

### Progress
- [x] Ran Bob's catalogued persona-authoring eval in a fresh fixture; initial Promptfoo report passed.
- [x] Reviewed generated artifact, found the shared demeanor baseline was omitted, and strengthened Bob's creation instructions and the measurable PERSONA rubric.
- [x] Ran three fresh verification fixtures; all generated skills explicitly include courteous, succinct, and respectful.
- [x] Adjudicated two raw failures as evaluator false positives using provider trace and explicit direct-dependency instructions; one raw run passed.
- [x] Updated Judge to record evidence-backed overrides separately from raw scores; canonical and packaged copies match and diff check is clean.

### Blockers
Promptfoo raw result for the three-run verification was 1/3 pass; remaining two failures were validated false positives, not Bob artifact defects.

## Next Steps
### Immediate Next Action
No further action; await the user's next request. Preserve reports under `build/persona-eval/` for audit.

### Waiting On
User.
