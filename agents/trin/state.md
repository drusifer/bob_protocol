# Agent State

## Context
- The Bob persona-authoring suite passed after the grader was grounded in the installed fixture's `agents/PROJECT.md`.
- Morpheus `*advise` was added to the live and packaged persona skills and covered by `morpheus-design-advice`, which installs this checkout into a disposable project and produces an ADR.
- First Morpheus run exposed a rubric ambiguity, not an ADR defect: the template makes Related optional, but DECISION's STATE criterion did not say omission is valid when no earlier ADR exists. Canonical and packaged rubrics now explicitly allow omission or `None` in that case.
- Corrected report: `build/persona-eval/morpheus-design-advice-20261030T132734Z-run1.json`; retained ADR: `build/persona-eval/runtime/morpheus-design-advice-20261030T132734Z-run1/project/docs/decisions/ADR-0001-refund-lifecycle.md`.
- The retained ADR models Payments/Payment/Refund ownership and invariants, gives behavior scenarios, compares three options, and explains KISS/DRY. The report confirms `skill-used: morpheus` and all applicable DECISION rubric criteria pass.
- Full tests: 88 passed, 7 skipped, 9 subtests passed. Mermaid lint passed; Node v24.13 emitted a transitive dependency engine warning, recorded in `docs/SDLC.md`. All pytest/eval scratch and reports are in `build/`.

## Current Task
**Status:** Completed; QA passed and Morpheus review passed.
**Assigned to:** Trin
**Progress:** Reviewed the actual eval report and artifact against the installed shared DECISION rubric after the rubric correction. No behavior-specific rubric was added.

## Next Steps
1. Tank has completed SDLC documentation, and Oracle reviewed it against the full SDLC rubric.
2. Keep future local Promptfoo reports/runtime and pytest scratch under `build/`, never `/tmp`.
3. Do not add Actions or hooks for this gate without a new user decision.
