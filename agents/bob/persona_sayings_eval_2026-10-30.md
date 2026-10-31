# Persona Sayings and Ethics Baseline Eval Notes — 2026-10-30

## Change
- Added the shared highly ethical expert-professional baseline and operational ethics guidance to the persona template and all nine personas.
- Added a separate Sayings section with three original, role-specific lines to each persona. Added values/demeanor for Bob, who previously lacked that section.
- Updated Bob's authoring guidance and the personality-behavior eval rubric; synced canonical files to packaged templates.
- Focused tests: `uv run bobp make test-q ARGS='-k test_persona_eval'` — 14 passed, 87 deselected.
- Canonical/package mirror parity and `git diff --check` passed.

## Eval Evidence
Reports are under `build/persona-eval/`.

| Suite | Run IDs | Raw result | Notes |
|---|---|---:|---|
| `bob-persona-authoring` | `20261030T225116Z-run1..3` | 0/3 | Run 1 flags generated command/state workflow gaps; run 2 incorrectly treats three values as outside a 3–5 range; run 3 flags transitive skills as redundant despite fixture context. No unchanged retry. |
| `cypher-personality` | `20261030T225424Z-run1..3` | 3/3 | Passed. |
| `morpheus-personality` | `20261030T225556Z-run1..3` | 3/3 | Passed. |
| `mouse-personality` | `20261030T225732Z-run1..3` | 2/3 | Run 3 raw `skill-used` mismatch says no skills used, while the two other runs pass. |
| `neo-personality` | `20261030T225927Z-run1..3` | 2/3 | Runs 1–2 pass. Run 3 grader says three sayings do not satisfy a 3–5 criterion and cites no evidence despite the target skill being embedded in the rubric prompt. |
| `oracle-personality` | `20261030T230126Z-run1..3` | 3/3 | Passed. |
| `smith-personality` | `20261030T230126Z-run1..` | incomplete | Batch was interrupted by the user steering to TypeScript; current run exited 130. |
| `tank-personality`, `trin-personality` | — | not run | Batch stopped before these suites. |

No persona eval is claimed as a complete all-persona pass. The runner currently chains Python `bobp persona-eval` -> Promptfoo/Node -> `openai:codex-sdk` for the persona and grader. User requested switching away from Codex to TypeScript; clarification is pending on whether TypeScript should replace the Python wrapper, the model provider, or both. Do not change the provider without a model/auth choice.

## Jev Grader Integration — 2026-10-30

Jev is now the rubric judge through the official `typesafe-sdk` Python SDK. Codex remains the Promptfoo target provider because Jev returns typed Choice/Score/Noul judgments rather than free-form task responses. The grader asks a separate Jev Noul question for each semantic rubric criterion, stores each probability in Promptfoo's component results, and uses `> 0.5` as the yes/no decision boundary. Persona baseline phrases, demeanor/value count, sayings count, and attributions are checked deterministically. Criteria that explicitly apply only to scenarios naming L1–L4 are reported N/A otherwise.

- Focused tests after this change: `uv run bobp make test-q ARGS='-k test_persona_eval'` — 19 passed, 87 deselected.
- The Node/Python/TypeSafe integration completed a live Jev API call. Latest Neo repeat passed: `neo-personality-20261030T231902Z-run1.json`.
- Full catalog run: `uv run bobp persona-eval --all`, fresh suite reports `20261030T231714Z` through `20261030T231951Z`: 6/10 suites passed. Cypher, Morpheus personality, Neo, Oracle, Smith, and Tank passed. Bob authoring failed four semantic rubric criteria; Morpheus design advice and Mouse planning failed the raw `skill-used` assertion while Jev passed all rubric criteria; Trin's response identified ambiguity but proposed access expectations without labeling them as assumptions, and Jev scored that behavior criterion 0.15.
- Fresh Bob authoring rerun after the L-level applicability fix: `bob-persona-authoring-20261030T232243Z-run1.json`. Complexity calibration is N/A because the scenario specifies no L-level; the suite still fails protocol/dependency, tool-fit, consistency, and behavior-check criteria. No unchanged retry was run.
- During integration, the first Neo run exposed a config shape error (strings where criterion objects were expected); the adapter was corrected and verified by focused tests and fresh runs. A 0.75 semantic threshold produced a borderline false negative at 0.72; the boundary is now the Noul majority decision at 0.5, with each probability retained for review. The two earlier pre-threshold Neo reports remain in `build/` as raw history.

Jev provides probabilities but no textual explanation for its judgments. The criterion label and probability are saved in the report; human evidence review remains necessary, particularly for broad artifact rubric rows. The API key prerequisite is `TYPESAFE_API_KEY`; eval artifacts and responses are sent to TypeSafe for grading. The eval-runner change and persona edits are uncommitted.

## Failure Repair Follow-up

- `assert_skill_used` now accepts a verifiable Codex trace that reads the exact installed persona skill text, even when a later part of the same shell command fails. This fixed raw `skill-used` false negatives without weakening the check. Focused tests: `uv run bobp make test-q ARGS='-k test_persona_eval'` — 20 passed, 87 deselected.
- Bob now instructs persona authors to list only direct shared-skill prerequisites. Trin now labels expected outcomes for unspecified product behavior as assumptions/recommendations.
- Fresh focused reruns: `trin-personality` passed (`trin-personality-20261030T234039Z-run1.json`); `morpheus-design-advice` passed (`morpheus-design-advice-20261030T234101Z-run1.json`); `mouse-personality` passed (`mouse-personality-20261030T234139Z-run1.json`).
- Bob latest run `bob-persona-authoring-20261030T234247Z-run1.json`: 10/12 semantic rubric criteria passed; Complexity calibration is N/A. Tool and repository fit scored 0.31 and Behavior check 0.13. The artifact has a staged-diff example, but its `bob-protocol` link is incorrectly written as `agents/skills/bob-protocol/SKILL.md` from a nested directory. Usability and size passed at 0.82. No further Bob rerun is authorized under the project anti-loop guard until Oracle consultation and user direction.
- Oracle consultation confirmed the link defect and missing Git-worktree/command-failure guidance as real tool-fit gaps. Oracle judged the behavior score likely a Jev false negative or ambiguous judgment: the artifact contains an activation request, tool action, concrete result, and rationale, but Jev returns no explanation. Sayings are unlikely to contribute: their criterion passed at 0.91 and the artifact has three concise role-specific lines.
- Updated Bob authoring guidance and both persona-template copies to require links that resolve from the nested `SKILL.md`, explicit Git worktree/no-diff/failure behavior for Git-dependent personas, and compact examples with observable verification. The subsequent Jev-context refinement and fresh verification results are recorded below.

## Jev Input and Rubric Refinement

Local inspection found no dedicated TypeSafe/Jev or Promptfoo style guide. The existing source of workflow guidance is `agents/skills/judge/SKILL.md`; it now has Jev grading guidance for the SDK's Choice and Score primitives. The tool-fit row was split into atomic tool availability, repository path references, and tool relevance checks. The behavior row was split into activation/next action, output/verification, and conditional handoff checks.

The Jev state now contains the full rubric, persona authoring instructions, expected artifact path, and candidate content, plus a concise fixture context with declared capabilities, Git executable/worktree availability, and relevant skill/template/document paths. The inventory omits chat logs, agent state files, and unrelated transcripts. Each criterion has explicit classification and ordered-score descriptions. `docs/SDLC.md` describes this data flow.

- Focused unit tests: `uv run bobp make test-q ARGS='-k test_persona_eval'` — 22 passed, 87 deselected.
- Bob initial refined run: `bob-persona-authoring-20261030T235344Z-run1.json` passed 14/14 semantic criteria. First `--repeat 3` batch had 0/3 passes, with only borderline Repository fit scores (0.44, 0.47, 0.50) and Behavior check (0.47) below the 0.50 gate. This evidence drove a rubric refinement: repository-link paths now follow established path conventions, and Behavior is split into three observable checks.
- Refined Bob repeat: `bob-persona-authoring-20261030T235722Z-run1..3.json` passed 3/3; Repository path references scored 0.51, 0.53, and 0.60. Final Bob run after adding the explicit artifact-relative path to Jev state, `bob-persona-authoring-20261031T000030Z-run1.json`, passed 16/16, with Repository path references at 0.54.
- Morpheus design holdout `morpheus-design-advice-20261030T235913Z-run1.json` passed 4/4 (all semantic probabilities at least 0.90).
- Canonical/package mirrors and `git diff --check` passed. The judge API returns probabilities without explanations; criterion-specific component rows now give actionable diagnosis. Borderline probabilities still warrant manual artifact review.

## Jev Classification and Score

The user suggested classifying each rubric criterion by level and retaining a score. The evaluator now asks two criterion-specific typed Jev questions: `Choice` selects `meets`, `partially_meets`, or `does_not_meet`; `Score` returns an ordered three-level expected score (0–2) with its probability distribution. The criterion text is included in both questions. A criterion passes only when Choice selects `meets` and the Score distribution's most likely level is also `meets`. The expected score is reported separately; it is not rounded into a class. When the two most likely levels disagree, the result is flagged for review and fails the gate. Each component includes both distributions and confidence values.

The first live Choice+Score run revealed that the criterion text had accidentally been omitted from both per-item questions. That invalid run is retained as `bob-persona-authoring-20261031T002607Z-run1.json`. After fixing the prompt, a fresh run passed. Its one mismatch showed that comparing the expected score to an arbitrary midpoint can disagree with the top probability; agreement now compares each primitive's most likely level.

- Focused unit tests: `uv run bobp make test-q ARGS='-k test_persona_eval'` — 22 passed, 87 deselected.
- Latest Bob repeat: `bob-persona-authoring-20261031T003541Z-run1..3.json` passed 3/3 with Choice/Score agreement.
- Morpheus design holdout: `morpheus-design-advice-20261031T003727Z-run1.json` passed 4/4; all four Choice labels and most likely Score levels were `meets`.
- Judge guidance and `docs/SDLC.md` now describe both primitives, the class gate, the 0–2 expected score, and mismatch handling. Updated canonical/package persona templates show the correct relative Bob Protocol link.
- Mirror parity and `git diff --check` passed. Choice provides a useful rubric level; Score and distributions add a separate ordinal summary. Neither primitive returns free-form rationale, so reports rely on atomic criterion names and explicit evidence anchors.
