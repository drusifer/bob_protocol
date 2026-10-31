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

- 2026-10-30: Upgraded Cypher, Morpheus, Mouse, Neo, Oracle, Smith, Tank, and Trin to the shared courteous/succinct/respectful baseline with five role-specific working values each. Preserved role/command content; canonical and packaged skills are synchronized.
- 2026-10-30: Added focused Promptfoo behavior suites for those eight upgrades and verified each with three fresh passing runs (24/24). Failure review identified two under-specified scenarios rather than persona defects: Mouse needed task scope details and explicit scope-based level reasons; Neo needed the legitimate-zero boundary called out. Updated those fixture requests without weakening criteria; retained initial reports for audit. Detailed report paths are in `agents/bob/persona_eval_2026-10-30.md`.

- 2026-10-30: Added an explicit highly ethical expert-professional baseline and separate original Sayings section to the shared persona template and all nine personas; updated Bob guidance and the eval rubric, then synced packaged copies. Focused tests passed (14 passed, 87 deselected). Eval evidence, raw failures, and run IDs are recorded in `agents/bob/persona_sayings_eval_2026-10-30.md`. User clarified they meant the Jev TypeSafe Python SDK. Integrated Jev as the typed rubric judge while retaining Codex as the target task executor; current design, focused-test result, and full-catalog raw results are recorded in `agents/bob/persona_sayings_eval_2026-10-30.md`.
- 2026-10-30: Failure repair follow-up: improved installed-skill grading to verify exact fixture skill text in Codex traces, including a later shell failure; fixed Bob guidance to list only direct prerequisites and Trin guidance to label unspecified expected outcomes as assumptions. Focused tests pass (20 passed, 87 deselected). Fresh Trin, Morpheus design, and Mouse suites pass. Latest Bob authoring remains below bar on Tool and repository fit (0.31) and Behavior check (0.13); Usability and size passes (0.82). A real nested relative-link issue is visible in the generated artifact. Stop per anti-loop guard and consult Oracle before another Bob eval.
- 2026-10-30: Oracle consultation confirmed Bob's broken root-relative links and missing Git-worktree/error handling as real tool-fit gaps. Oracle judged Behavior check likely a Jev false negative/criterion ambiguity because the artifact already contains an activation request, command, concrete result, and rationale; Jev provides no explanation. Sayings are not implicated (0.91). Updated Bob guidance and persona template to validate links relative to the nested skill, cover Git prerequisite/failure paths, and make examples explicitly verifiable. These latest prompt edits are not reevaluated; pause for manual user direction before another Bob attempt.
- 2026-10-31: User directed Jev input/rubric improvement. No separate TypeSafe/Jev or Promptfoo style guide exists; added guidance to Judge's existing skill. Noul questions now use SDK-supported true/false criteria descriptions and atomic rubric rows; Jev state includes complete rubric, persona instructions, artifact path, and a concise fixture path/capability/executable inventory. Focused tests pass (22 passed, 87 deselected); Bob's refined `--repeat 3` passed 3/3, final artifact-path-enriched run passed all 16 report components, and Morpheus design holdout passed 4/4. Detailed reports are in `agents/bob/persona_sayings_eval_2026-10-30.md`.
- 2026-10-31: User directed using Jev as a rubric-level classifier, with a score as a second view. Replaced binary Noul judgments with per-criterion Choice (`meets`/`partially_meets`/`does_not_meet`) plus an ordered Score whose expected value is 0–2. Found and fixed two wiring defects during live trials: each question now contains its own criterion text, and Choice is compared to Score's most likely level rather than rounding the expected score. The class must be `meets` and agree with Score's top level to pass. Latest Bob repeat passed 3/3 (`bob-persona-authoring-20261031T003541Z-run1..3.json`); Morpheus holdout passed 4/4 (`morpheus-design-advice-20261031T003727Z-run1.json`); focused tests passed 22/22. Details in the eval note.

## Current Task
**Status:** Completed; Jev context/rubric refinements and fresh verification pass.
**Assigned to:** Bob
**Started:** 2026-10-30
**Completed:** 2026-10-31

### Task Description
Add original role-specific sayings to each persona and the template, reinforce the shared ethical-professional baseline, and improve Jev's Promptfoo rubric judgments with classifier levels, an ordinal score, clearer atomic criteria, and relevant evaluation context.

### Progress
- [x] Added shared baseline, role demeanor/values, and sayings to the persona template and all nine personas.
- [x] Integrated Jev with `typesafe-sdk`, documented the key/data flow, and synced packaged persona files.
- [x] Added a trace-aware skill-use assertion and covered it with a focused unit test.
- [x] Fixed Bob direct-dependency guidance and Trin's assumption-labeling guidance; canonical and packaged files match.
- [x] Focused tests pass after Jev input/rubric changes (22 passed, 87 deselected).
- [x] Fresh Trin, Morpheus design, and Mouse evals pass; latest reports are under `build/persona-eval/` at `trin-personality-20261030T234039Z-run1.json`, `morpheus-design-advice-20261030T234101Z-run1.json`, and `mouse-personality-20261030T234139Z-run1.json`.
- [x] Oracle reviewed Bob's remaining failures; fixed the confirmed link and Git prerequisite guidance and clarified the behavior example requirement.
- [x] Refined atomic checks and Jev evidence context; Bob passed three fresh runs and a final enriched-state run.
- [x] Replaced binary Jev judgments with Choice classification and ordinal Score; fixed criterion prompt wiring and score-level agreement mapping.
- [x] Latest Bob Choice+Score repeat passed 3/3; Morpheus design holdout passed 4/4.
- [x] Verified Morpheus design as a holdout; it passed all four criteria.
- [x] Updated Judge guidance and SDLC documentation; canonical/package mirrors and diff checks pass.

### Blockers
None. Raw Jev reports have varying, sometimes borderline probabilities; see the eval note for per-criterion evidence and report IDs. No pass threshold was changed.

## Next Steps
### Immediate Next Action
Bob's eval work is complete. Handoff to Oracle for the user's new documentation request: groom the docs and add user-facing documentation for the Choice+Score persona eval system. Current evaluator, rubric, persona, and docs changes remain uncommitted in the shared worktree.

### Waiting On
Oracle's documentation grooming handoff.
